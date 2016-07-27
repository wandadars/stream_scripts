#! /usr/bin/env python

# Purpose:	Reads the output file from the Loci 'extract' utility that contains information
#		about the heat flux leaving a boundary.
#
# Input: 	Name of the file that contains the columnated data
#		Format: x y z heat_flux
#
# Output: 	A set of plots showing the spatial variation of the heat flux.
#
#
#	Author: Christopher Neal
#	Date   : 07/27/2016
#	Updated: 07/27/2016
#
########################################################################


import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import numpy as np
import time
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter


avg_all_data = True  #For averaging out all repeated values of x


#Store the name of the file that the user wants to plot the from.
input_file_name = str(sys.argv[1])

#Test to see if the file exists, otherwise throw exception
try:
  os.path.isfile(input_file_name)
  print("Reading Data From: %s\n"%(input_file_name))
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise



#open file if file exists, otherwise throw exception
try:
  f=open(input_file_name,"r")
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise



#Loop through entire file
#Data in the file is structured in the following way:
#x [y] [z] heat_flux
#The terms in [] may not be present in the actual file
with open(input_file_name,'r') as content_file:
	data = content_file.read()

#store the number of rows of data
numrows = len(data)
numcols = len(data[0])

if numcols == 2:
	col_names = ['x','qdot']
elif numcols == 4:
	col_names = ['x','y','z','qdot']


if(avg_all_data == True):

	averaged_data = []

	uniquex_x = [data[0][0]] #the first value is stored to initialize the process
	entry_count = 0
	unique_rows = 0
	Sum = 0
	for i in range(0,numrows):
		if(data[i][0] == unique_x[len(unique_x)): #Repeat entry that needs to be averaged
			entry_count = entry_count + 1
			Sum = Sum + data[i][-1]
		elif(i == numrows-1):
			averaged_data[len(unique_x)].append
		else:	
	
			averaged_data.append()
			#store mean value of heat flux
			averaged_data[len(unique_x)].append(unique_x[len(unique_x)])
			averaged_data[len(unique_x)].append(float(Sum)/float(entry_count))
			
			#reset counters
			entry_count = 0
			Sum = 0

			unique_x.append(data[i][0])



#Print & output to screen for testing
for i in range(len(unique_x)):
	for j in range(0,len(averaged_data[0])):
		print averaged_data[i][j]





#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
MaxVal = np.amax(averaged_data[:,1])
MinVal = np.amin(averaged_Data[:,1])

#Change the min and max values a little bit so that all data lies within the bounds of the plots
MaxVal = MaxVal + 0.05*abs(MaxVal)
MinVal = MinVal - 0.05*abs(MinVal)
 
plt.plot(Force_Data[:,0],Force_Data[:,1], marker='o')
plt.xlabel('X (meters)')
plt.ylabel('Heat Flux (qdot)')
plt.ylim([MinVal, MaxVal])
plt.draw
 
outputFileName = "qdot_mean_spatial_average" + ".png"
plt.savefig(outputFileName, bbox_inches='tight')
plt.close()

print("\n Program has finished... \n")


