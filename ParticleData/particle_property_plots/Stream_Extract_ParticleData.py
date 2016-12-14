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
from Read_hdf5_particle import *

#For calling the h5dump shell script
ShellScriptPath="/home/neal/codes/locistream/stream_scripts/ParticleData/particle_property_plots"

delta_t = 1.0e-2  #Iterations are not ascribed a time, so a mapping must be done

#Start & Stop value of particle data file indices
iStart = 20
iStep = 20
iEnd = 79800

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
	print("%10.2E"%(times))


#Store the casename from the user's input to the script
CaseName = str(sys.argv[1])
print("\nCase name is: %s"%(CaseName))
particle_temperatures = []
particle_diameters = []
for i in range(0,NumFiles):
    #Read particle data from HDF5 data files
    print("Reading Data from file: %d"%(i+1))
    ParticleData=Read_HDF5_Particle_Data(CaseName,file_indices[i],ShellScriptPath)
    
    print(ParticleData)
    #Compute size of ParticleData 2D list
    numrows = len(ParticleData)
    numcols = len(ParticleData[0])
    print("Number of parcels in dataset %d :\t%10.6E"%(i+1,numrows))
    
    particle_temperatures.append(ParticleData[0][1])
    particle_diameters.append(ParticleData[0][0])


print particle_temperatures
print particle_diameters

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
    f_output.write("%10.6E\t%10.6E\t%10.6E\n"%(float(times),float(particle_temperatures[i]),float(particle_diameters[i])))
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
print("Saving a figure to:%s\n"%(outputFileName))
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


#Go back to the original data directory
os.chdir("../..")


print("\n Program has finished... \n")


