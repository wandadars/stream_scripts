#! /usr/bin/env python

# Purpose:	Reads an output file from Loci-Stream and parses the contents to extract the
#		fluxes on a user specified boundary, plots the data, and writes the images
#               to disk.
#
# Input: 	Name of the boundary to extract data from
#
# Output: 	A set of plots in a directory with the name of the boundary.
#
#
#	Author: Christopher Neal
#	Date   : 02/27/2017
#	Updated: 02/27/2017
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


#Store the name of the boundary that the user wants to plot 
BC_Name = str(sys.argv[1])

#Contruct force data file name
ForceDataFileName = "flux_"+BC_Name + ".dat" 

print("Reading Data From: %s\n"%(ForceDataFileName))

#Go into the output directory and read in the boundary integrated data
OutPutDir = "output"
if not os.path.exists(OutPutDir):
	raise Exception("Can not locate output directory. Make sure code is being executed in main run directory")	
else:
	os.chdir(OutPutDir)



#Test to see if the file exists, otherwise throw exception
try:
  os.path.isfile(ForceDataFileName)
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise

#Count number of non-blank lines in file
non_blank_count = 0
with open(ForceDataFileName,"r") as infp:
    for line in infp:
       if line.strip():
          non_blank_count += 1
print("number of lines found %d\n"%(non_blank_count))



#open file if file exists, otherwise throw exception
try:
  f=open(ForceDataFileName,"r")
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise



#Loop through entire file to extract contents
#Data in the file is structured in the following way:
#iteration, simulation time, mass_flux, Fx, Fy, Fz, energy flux, area

variable_names = ['timestep_number','time','mass_flux','Fx','Fy','Fz','energy_flux','area']

Data = np.zeros((non_blank_count,len(variable_names)))
count = 0 #For placing items into array
for Line in f:

	lineData = Line.rstrip()
	lineData = lineData.split()
		
	Data[count,0] = lineData[0]  
	Data[count,1] = lineData[1]  
	Data[count,2] = lineData[2]  
	Data[count,3] = lineData[3]  
	Data[count,4] = lineData[4]  
	Data[count,5] = lineData[5]  
        Data[count,6] = lineData[6]  
	Data[count,7] = lineData[7]  
	count = count + 1

f.close()





#Now plot & output the data to an output directory

#Go back to the main directory
os.chdir("..")

#Create a directory for the output
OutputDir="BoundaryDataOutput"
if not os.path.exists(OutputDir):
	os.makedirs(OutputDir)
	os.chdir(OutputDir)
else:
	os.chdir(OutputDir)

#Now plot the data 

for variable in variable_names:

    #Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
    MaxVal = np.amax(Data[:,1])
    MinVal = np.amin(Data[:,1])

    #Change the min and max values a little bit so that all data lies within the bounds of the plots
    MaxVal = MaxVal + 0.05*abs(MaxVal)
    MinVal = MinVal - 0.05*abs(MinVal)
 
    plt.plot(Data[:,0],Data[:,1], marker='o')
    plt.xlabel('Time (Seconds)')
    plt.ylabel(variable)
    plt.ylim([MinVal, MaxVal])
    plt.draw
 
    outputFileName = variable + ".png"
    plt.savefig(outputFileName, bbox_inches='tight')
    plt.close()


#Go back to the main directory
os.chdir("..")


print("\n Program has finished... \n")


