#! /usr/bin/env python

# Purpose:	Reads the output files from Loci-Stream and parses the contents to extract the
#		particle properties and creates time history plots of the properties.
#
#
# Input: 	Base filename where particle data is stored.
#
# Output: 	A data file containing the time history of a particle property 
#
#
#	Author: Christopher Neal
#	Date   : 11/10/2016
#	Updated: 11/10/2016
#
########################################################################

import argparse
import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import math
import numpy as np
import time #For deubbging
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import particle_data_reader 


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool for plotting lagrangian particle data.  Example: --case droplet --delta_t 1e-2 --start 10 --step 10 --stop 1000')
    parser.add_argument('--delta_t', required=True, type=float, metavar='timestep', help='timestep between solutions')
    parser.add_argument('--start', required=True, type=int, metavar='starting solution timestep number', help='integer timestep number to start processing data from')
    parser.add_argument('--step', required=True, type=int, metavar='step size between solutions', help='integer timestep gap to process data over i.e. every nth solution')
    parser.add_argument('--stop', required=True, type=int, metavar='stopping solution timestep number', help='integer timestep number to stop processing data at')
    parser.add_argument('--case', required=True, type=str, metavar='name of the vars file given to the case', help='name ascribed to case. Usually same as the vars file name.')

    args = parser.parse_args()
    if len(sys.argv) == 1: #Case case where poor user supplies nothing to the program and re-direct them back to the help :)
        parser.print_help(sys.stderr)
        sys.exit(1)

    arguments = {'delta_t': args.delta_t, 'start': args.start, 'step': args.step, 'stop': args.stop, 'case': args.case}
    return arguments


if __name__ == '__main__':
    arguments = parse_arguments()

    delta_t = arguments['delta_t']
    iStart = arguments['start']
    iStep = arguments['step']
    iEnd = arguments['stop']
    CaseName = arguments['case']

    #Compute and store data filename numbers
    NumFiles = (iEnd-iStart)/iStep
    file_indices = []
    iIterate=iStart
    for i in range(0,NumFiles):   #make list of timestamps
        file_indices.append(iIterate)
        iIterate = iIterate + iStep
    print(file_indices)

    #Store the times for each iteration- ASSUMPTION: Each iteration has the same timestep
    time_steps = []
    for i,iteration in enumerate(file_indices):
        time_steps.append(delta_t*float(iteration)) 

    print("Values of time being considered are:")
    for times in time_steps:
        print("%10.2G"%(times))

    #Store the casename from the user's input to the script
    print("\nCase name is: %s"%(CaseName))
    particle_temperatures = []
    particle_diameters = []
    for i in range(0,NumFiles):
        #Read particle data from HDF5 data files
        print("Reading Data from file: %d"%(i+1))
        hdf5_reader = particle_data_reader.HDF5ParticlePropertyPlotterDataReader(CaseName, file_indices[i])
        ParticleData = hdf5_reader.read_hdf_particle_data()
        
        print(ParticleData)
        #Compute size of ParticleData 2D list
        numrows = len(ParticleData)
        numcols = len(ParticleData[0])
        print("Number of parcels in dataset %d :\t%10.6E"%(i+1,numrows))
        
        particle_temperatures.append(ParticleData[0][1])
        particle_diameters.append(ParticleData[0][0])


    #print particle_temperatures
    #print particle_diameters

    print("Writing Output Data")

    #Create output directory and enter the directory
    FilePathBase =os.getcwd()
    OutPutDir = FilePathBase +"/particle_history_data"
    if not os.path.exists(OutPutDir):
            os.makedirs(OutPutDir)
            os.chdir(OutPutDir)
    else:
            os.chdir(OutPutDir)

    #Write the output 
    OutputFileName = CaseName + "_Particle_Data" + ".txt"
    f_output = open(OutputFileName,"w")
    for i,times in enumerate(time_steps):
        f_output.write("%10.6E,\t%10.6E,\t%10.6E"%(float(times),float(particle_temperatures[i]),float(particle_diameters[i])))
        f_output.write("\n")

    f_output.close()



    #####Plot output data##########

    window_buffer_factor = 0.01

    #Find the maximum value of the temperature variable about to be plotted so that the 
    #plot vertical axis can be scaled appropriately
    for k,temp in enumerate(particle_temperatures):
        if(k==0):
            MaxVal = float(particle_temperatures[k])
            MinVal = float(particle_temperatures[k])
        elif(float(particle_temperatures[k])>MaxVal):
            MaxVal = float(particle_temperatures[k])
        elif(float(particle_temperatures[k])<MinVal):
            MinVal = float(particle_temperatures[k])
                

    #Change the min and max values a little bit so that all data lies within the bounds of the plots
    MaxVal = MaxVal + window_buffer_factor*abs(MaxVal)
    MinVal = MinVal - window_buffer_factor*abs(MinVal)
                

    xValues = np.asarray(time_steps)
    yValues = np.asarray(particle_temperatures)
        
    plt.plot(xValues,yValues, marker='o')
    plt.xlabel('Time, t (seconds)')
    plt.ylabel('Particle Temperature, T(Kelvin)')
    plt.ylim([MinVal, MaxVal])

    outputFileName = CaseName + '_temperature_history'+".png"
    print("Saving a figure to:%s"%(outputFileName))
    plt.savefig(outputFileName, bbox_inches='tight')
    plt.close()



    #Find the maximum value of the diameter variable about to be plotted so that the 
    #plot vertical axis can be scaled appropriately
    for k,temp in enumerate(particle_diameters):
        if(k==0):
            MaxVal = float(particle_diameters[k])
            MinVal = float(particle_diameters[k])
        elif(float(particle_diameters[k])>MaxVal):
            MaxVal = float(particle_diameters[k])
        elif(float(particle_diameters[k])<MinVal):
            MinVal = float(particle_diameters[k])


    #Change the min and max values a little bit so that all data lies within the bounds of the plots
    MaxVal = MaxVal + window_buffer_factor*abs(MaxVal)
    MinVal = MinVal - window_buffer_factor*abs(MinVal)

    xValues = np.asarray(time_steps)
    yValues = np.asarray(particle_diameters)

    plt.plot(xValues,yValues, marker='o')
    plt.xlabel('Time, t (seconds)')
    plt.ylabel('Particle Diameter, D(Meters)')
    plt.ylim([MinVal, MaxVal])

    outputFileName = CaseName + '_diameter_history'+".png"
    print("Saving a figure to:%s\n"%(outputFileName))
    plt.savefig(outputFileName, bbox_inches='tight')
    plt.close()



    #Plot the square of the diamter(for evaporation cases this is a useful metric. See D-squared law)
    xValues = np.asarray(time_steps)
    yValues = np.asarray(particle_diameters)
    yValues = np.square(yValues.astype(float))
    MaxVal_new = MaxVal*MaxVal
    MinVal_new = MinVal*MinVal

    plt.plot(xValues,yValues, marker='o')
    plt.xlabel('Time, t (seconds)')
    plt.ylabel('Particle Diameter Squared, D^2(meters^2)')
    plt.ylim([MinVal_new, MaxVal_new])

    outputFileName = CaseName + '_square_diameter_history'+".png"
    print("Saving a figure to:%s\n"%(outputFileName))
    plt.savefig(outputFileName, bbox_inches='tight')
    plt.close()

    #Plot the square of the diamter in millimeters
    xValues = np.asarray(time_steps)
    yValues = np.asarray(particle_diameters)
    yValues = np.square(yValues.astype(float)*1000) 
    MaxVal_new = MaxVal*MaxVal * 1e6
    MinVal_new = MinVal*MinVal * 1e6

    fig, ax = plt.subplots()
    ax.plot(xValues,yValues, marker='o')
    ax.set(xlabel='Time, t (seconds)', ylabel='Particle Diameter Squared, D^2(millimeters^2)')
    ax.set_ylim([MinVal_new, MaxVal_new])

    outputFileName = CaseName + '_square_diameter_mm_history'+".png"
    print("Saving a figure to:%s\n"%(outputFileName))
    fig.savefig(outputFileName, bbox_inches='tight')
    plt.close(fig)

    #Go back to the original data directory
    os.chdir("../..")


    print("\n Program has finished... \n")


