#! /usr/bin/env python
import csv
import os 
import math
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
from scipy.signal import butter, lfilter, freqz
import matplotlib.ticker as ticker

r = random.Random()
r.seed('plots')


class DataObject(object):
    def __init__(self, data_path, data_tag):
        self.data_path = data_path
        self.data_tag = data_tag
        self.data = None

    def read_data(self):
        self.data = read_simulation_data_file(self.data_path)


def count_lines_of_data(file_name):
    non_blank_count = 0
    with open(file_name,'r') as f:
        for line in f:
           if line.strip() and ('#' not in line):
              non_blank_count += 1
    print("number of data entries found in %s: %d\n"%(file_name, non_blank_count))
    return non_blank_count

def test_for_file(file_name):
    #Test to see if the file exists, otherwise throw exception
    try:
      os.path.isfile(file_name)
    except IOError as e:
      print('I/O error({0}): {1}'.format(e.errno, e.strerror))
      raise

    non_blank_count = count_lines_of_data(file_name)
    try:
      f = open(file_name,"r")
    except IOError as e:
      print('I/O error({0}): {1}'.format(e.errno, e.strerror))
      raise

    return f, non_blank_count


def read_simulation_data_file(filename):
    data = []
    column_name_map = {0: 'iteration', 1: 'time', 2: 'mass_flowrate', 3: 'fx', 4: 'fy', 5: 'fz', 6: 'energy_transfer', 7: 'total_area'}
    f, non_blank_count = test_for_file(filename)
    count = 0 
    for line in f:
        if line.strip() and ('#' not in line):
            line_data = line.rstrip()
            line_data = line_data.split()
            tmp = {}
            for i, value in enumerate(line_data):
                tmp[column_name_map[i]] = float(value)
            data.append(tmp)
    f.close()
    return data


def plot_forces(data_store, output_name, force_component):
    sim_data = data_store['simulation_data']
    
    fig, ax = plt.subplots()
    for i, data in enumerate(sim_data):
        red, green, blue = r.uniform(0,1), r.uniform(0,1), r.uniform(0, 1)
        color = (red, green, blue, 1)
        force = [tmp[force_component] for tmp in data.data]
        time = [tmp['time'] for tmp in data.data]
        ax.plot(time, force, marker='.', color=color, label='Loci-Stream: ' + data.data_tag)
    
    handles,labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='best')

    ax.tick_params(axis='both', which='both')
    ax.grid('on', which='major', linestyle='-', linewidth='1')
    ax.minorticks_on()

    ax.set_xlabel('Time(seconds)')
    ax.set_ylabel('Force(Newtons)')
    ax.set_title('Force History')
    #ax.set_ylim([0.0, 70])
    #ax.set_xlim([-0.5, 1.5])
    fig.draw

    outputFileName = output_name + '_' + str(force_component) + '.png'
    fig.savefig(outputFileName, bbox_inches='tight')
    fig.clf()


def plot_force_power_spectrum(data_store, output_name, force_component):
    sim_data = data_store['simulation_data']

    time = []
    pressure = []
    for i, data in enumerate(sim_data):
        time = [tmp['time'] for tmp in data.data]
        p = [tmp[force_component] for tmp in data.data]

    #Remove mean from data set
    p_mean = np.sum(p) / len(p)
    p = p - p_mean

    #Scale signal using Hanning window
    #window = np.hanning(len(p))
    window = np.hamming(len(p))
    p = p*window

    delta_t = time[1] - time[0]
    N = p.size // 2 + 1
    fa = 1.0 / delta_t # scan frequency
    print('Info about dataset: ' + str(force_component))
    print('dt= %.5fs (Sample Time)' % delta_t)
    print('fa= %.2fHz (Frequency)\n' % fa)

    pf = np.fft.fft(p)  
    #Lowpass filter to reduce noise in FFT output
    cutoff_frequency = 3000 #Hz
    sampling_frequency = 1.0 / delta_t
    pf = butter_lowpass_filter(pf, cutoff_frequency, sampling_frequency, order=1)
    
    tf = np.linspace(0.0, fa / 2.0, N, endpoint=True)

    fig, ax = plt.subplots()
    #ax.plot(tf, 2*np.abs(pf[:N])/N)
    ax.plot(tf, np.abs(pf[:N]))
    ax.set_xlabel('Frequency ($Hz$)')
    ax.set_ylabel('Power')
    ax.set_xlim([-5, 2000])
    tick_spacing = 400
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #plt.grid()
    plt.savefig(output_name + '_' + str(force_component) + '_fft' + '.png')
    
    #Quick print of dominant frequency
    power_levels = np.abs(pf[:N])
    max_loc = 0
    max_power = 0
    for i, power in enumerate(power_levels):
        if power >= max_power:
            max_power = power
            max_loc = i
    
    print('For force component: ' + str(force_component))
    print('Maximum power of {0:10.6f} located at frequency: {1:10.6f}'.format(max_power, tf[max_loc]))

    #Write CSV file
    with open(output_name + '_' + str(force_component) + '.csv', mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i, power in enumerate(power_levels):
            frequency_formatted = '{0:10.6f}'.format(tf[i])
            power_formatted = '{0:>10.6f}'.format(power)
            line = [frequency_formatted, power_formatted]
            output_writer.writerow(line)

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


class FFTUnitTester():
    def __init__(self):
        pass

    def run_unit_tests(self):
        self.unit_test_1()
        self.unit_test_2()
        self.unit_test_3()

    def unit_test_1(self):
        #Unit test for FFT
        t = np.linspace(0, 2*np.pi, 1000, endpoint=True)
        f = 3.0
        A = 100
        hann = np.hanning(len(t))
        s = A * np.sin(2*np.pi*f*t)
        s = s*hann
        data = np.zeros((t.size, 2))

        for i, (time, sine) in enumerate(zip(t, s)):
            data[i][0] = time
            data[i][1] = sine

        self.test_power_spectrum(data, [0,10], 'fft_unittest_1')


    def unit_test_2(self):
        #Unit test 2 for FFT
        t = np.linspace(0, 0.5, 1000, endpoint=True)
        f1 = 40
        f2 = 90
        hann = np.hanning(len(t))
        s = np.sin(f1 * 2 * np.pi * t) + 0.5 * np.sin(f2 * 2 * np.pi * t) 
        #s = s*hann
        data = np.zeros((t.size, 2))

        for i, (time, sine) in enumerate(zip(t, s)):
            data[i][0] = time
            data[i][1] = sine
        
        self.test_power_spectrum(data, [0,100], 'fft_unittest_2')
    
    def unit_test_3(self):
        self.test_lowpass_filter()

    def test_power_spectrum(self, data, window_range, output_name):
        time = []
        pressure = []
        time = data[:,0]
        p = data[:, 1]
        
        delta_t = time[1] - time[0]

        N = p.size // 2 + 1
        fa = 1.0 / delta_t # scan frequency
        print('dt= %.5fs (Sample Time)' % delta_t)
        print('fa= %.2fHz (Frequency)' % fa)

        pf = np.fft.fft(p)  
        tf = np.linspace(0.0, fa/2.0, N, endpoint=True)

        fig, ax = plt.subplots()
        ax.plot(tf, 2*np.abs(pf[:N])/N)
        ax.set_xlabel('Frequency ($Hz$)')
        plt.grid()
        ax.set_xlim(window_range)
        plt.savefig(output_name +'.png')

    def test_lowpass_filter(self):
        order = 6
        fs = 30
        cutoff = 3.667

        b, a = butter_lowpass(cutoff, fs, order)

        # Plot the frequency response.
        w, h = freqz(b, a, worN=8000)
        plt.subplot(2, 1, 1)
        plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
        plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
        plt.axvline(cutoff, color='k')
        plt.xlim(0, 0.5*fs)
        plt.title("Lowpass Filter Frequency Response")
        plt.xlabel('Frequency [Hz]')
        plt.grid()
        plt.savefig('lowpass_filter_frequency_response.png')

        # Demonstrate the use of the filter.
        # First make some data to be filtered.
        T = 5.0         # seconds
        n = int(T * fs) # total number of samples
        t = np.linspace(0, T, n, endpoint=False)

        # "Noisy" data.  We want to recover the 1.2 Hz signal from this.
        data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)

        # Filter the data, and plot both the original and filtered signals.
        y = butter_lowpass_filter(data, cutoff, fs, order)

        plt.subplot(2, 1, 2)
        plt.plot(t, data, 'b-', label='data')
        plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()

        plt.subplots_adjust(hspace=0.35)
        plt.savefig('filtered_test_data.png')
    


#Unit tests
#unit_tester = FFTUnitTester()
#unit_tester.run_unit_tests()


#--------------Main----------------
base_path = './output/'
file_name = 'flux_rtd.dat'
output_tag = 'rtd' #Name that is pre-pended to output files

data = [] #A list of DataObject(s) 

data_tag = 'rtd' #This is what goes on the plot legends
data_path = base_path + file_name 
data_object = DataObject(data_path, data_tag)
data_object.read_data()

data.append(data_object)

data_store = {'simulation_data': data}

force_components=['fx', 'fy', 'fz']
for force in force_components:
    plot_forces(data_store, output_tag, force)
    plot_force_power_spectrum(data_store, output_tag, force)

print("\nProgram has finished\n")

