#! /usr/bin/env python

# Purpose:  Reads the output file from the Loci 'extract' utility that contains information
#       about the heat flux leaving a boundary.
#
# Input:    Name of the file that contains the columnated data that is sorted according to x coordinate values!
#       Format: x y z heat_flux
#
# Output:   A set of plots showing the spatial variation of the heat flux.
#
#
#   Author: Christopher Neal
#   Date   : 07/27/2016
#   Updated: 07/27/2016
#
########################################################################

import os 
import sys 
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def test_file_exists(file_name):
    try:
      os.path.isfile(input_file_name)
      print("Input file detected.\n")
      print("Reading Data From: %s\n"%(input_file_name))
    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)

    try:
      f=open(input_file_name,"r")
    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
      raise

    return f


def read_data_file(f):
    #Data  format:
    #x [y] [z] heat_flux
    #The terms in [] may or may not be present in the actual file
    data = []
    line_count = 0
    with open(input_file_name) as f:

        for lines in f:
            line = lines.rstrip()
            line = line.split()

            if line is not  None:
                data.append([])
                for entry in line:
                    data[line_count].append(entry)
                line_count = line_count + 1
    
    print "Number of entries in file: ", len(data)
    num_cols = len(data[0])
    if num_cols == 2:
        col_names = ['x','qdot']
    elif num_cols == 4:
        col_names = ['x','y','z','qdot']

    #Debugging
    #for entry in data:
    #   print entry
    
    f.close()
    return (data,col_names)


def average_data_values(data):
    numrows = len(data)
    numcols = len(data[0])
    averaged_data = []

    unique_x = []
    unique_x.append(data[0][0]) #the first value is stored to initialize the process
    entry_count = 0 #Number of repeated values in the file that we average over
    qdot_sum = 0
    for i in range(0,numrows):
        #print "Comparing A: ",data[i][0], "   to   B:  ",unique_x[-1], "  Result is:  ",data[i][0]==unique_x[-1]
        if(i == numrows-1): #Last value in file
            averaged_data.append([])
            xloc = unique_x[len(unique_x)-1]
            averaged_data[len(unique_x)-1].append(xloc)
            averaged_data[len(unique_x)-1].append(float(qdot_sum)/float(entry_count)) #store mean heat flux

        elif( data[i][0] == unique_x[-1] ): #Repeat entry that needs to be averaged
            entry_count = entry_count + 1
            qdot_sum = qdot_sum + float(data[i][-1])

        else:   
            averaged_data.append([])
            #store mean value of heat flux
            averaged_data[len(unique_x)-1].append(unique_x[len(unique_x)-1])
            averaged_data[len(unique_x)-1].append(float(qdot_sum)/float(entry_count))
            
            #reset counter and summation variable
            entry_count = 0
            qdot_sum = 0

            #Add the newly found coordinate to the list of unique x coordinates
            unique_x.append(data[i][0])


    #for x_coord in unique_x:
    #   print x_coord

    #Print & output to screen for testing
    #for i in range(0,len(unique_x)):
    #   for j in range(0,len(averaged_data[0])):
    #       print averaged_data[i][j]

    return averaged_data


def convert_data_to_float(data):
    np_data = np.zeros((len(data),len(data[0])))
    for i in range(0,len(data)):
        for j in range(0,len(data[0])):
            np_data[i,j] = float(data[i][j])
    return np_data


def write_data_to_file(data, input_file_name):
    try:
      f=open(input_file_name + '_averaged',"w+")
    except IOError as e:
      print "I/O error({0}): {1}".format(e.errno, e.strerror)
      raise

    for i in range(0,len(data)):
        for j in range(0,len(data[0])):
            f.write("%10.6E\t"%(float(data[i][j])))
        f.write("\n")




#Main
avg_all_data = False  #For averaging out all repeated values of x

input_file_name = str(sys.argv[1])
f = test_file_exists(input_file_name)

data, col_names= read_data_file(f)

if(avg_all_data == True):
    data = average_data_values(data)

np_data = convert_data_to_float(data)

if avg_all_data == True:
    write_data_to_file(data, input_file_name)

#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
MaxVal = np.amax(np_data[:,1])
MinVal = np.amin(np_data[:,1])

#Change the min and max values a little bit so that all data lies within the bounds of the plots
MaxVal = MaxVal + 0.05*abs(MaxVal)
MinVal = MinVal - 0.05*abs(MinVal)
 
plt.plot(np_data[:,0],np_data[:,-1], linestyle='None',marker='o')
plt.xlabel('X (meters)')
plt.ylabel('Heat Flux (qdot)')
plt.ylim([MinVal, MaxVal])
plt.draw
 
outputFileName = "qdot_mean_spatial_average" + ".png"
plt.savefig(outputFileName, bbox_inches='tight')
plt.close()

print("\n Program has finished... \n")


