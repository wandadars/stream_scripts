#! /usr/bin/env python

# Purpose:	Reads the output file from Loci-Stream and parses the contents to extract the
#		residual data in the file and visualize the progress of the residuals for error
#		checking.
#
# Input: 	Name of the output file that contains the residual data
#
# Output: 	A set of plots showing the progression of the residuals.
#
#
#	Author: Christopher Neal
#	Date   : 04/01/2016
#	Updated: 04/01/2016
#
########################################################################


def time_iteration:
	def __init__(self,N=0):
		#N is the number of internal iterations per timestep used for this timestep
		self.internal_iterations = []
		for i in range(0,N):
			self.internal_iterations.append(residual_info())

def residual_info:
	def __init__(self):
		self.residual_data = "0.0"
		for i in range(0,10):
			self.residual_data.append("0.0")


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


#Store the name of the boundary that the user wants to plot the force data over.
Residual_File_Name = str(sys.argv[1])

#Test to see if the file exists, otherwise throw exception
try:
  os.path.isfile(Residual_File_Name)
  print("Reading Data From: %s\n"%(Residual_File_Name))
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise



#open file if file exists, otherwise throw exception
try:
  f=open(Residual_File_Name,"r")
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise

#Loop through entire file the residual data
#Data in the file is structured in the following way:
#R: n it uRes vRes wRes ppRes eRes kRes omegaRes yRes
CountingIterations = False
for Line in f:
	lineData = Line.rstrip()
	lineData = lineData.split()
		
	if(lineData[0] == "R:"):
		IterPerTimestep = 1
		CountingIterations = True
		IterationN = lineData[1]

	if(CountingIterations == True and lineData[1]==IterationN):
		IterPerTimestep = IterPerTimestep + 1
	else:
		break
	

#Re-open and perform full analysis
f.seek(0,0)	#Rewind file for reading

time_iteration_data = []
TimeStepCount = 0
for Line in f:
        lineData = Line.rstrip()
        lineData = lineData.split()

        if(lineData[0] == "R:"):
		time_iteration_data.append(time_iteration(IterPerTimestep))
		time_iteration_data[TimeStepCount].internal_iterations[0].residual_data = lineData[1:]

		for i in range(1,IterPerTimestep):
			Line=f.next()
			lineData = Line.rstrip()
			lineData = lineData.split()
			time_iteration_data[TimeStepCount].internal_iterations[i].residual_data = lineData[1:]
			IterationData.append



f.close()

#Print & output to screen for testing
for i in range(len(time_iteration_data)):
	for j in range(0,IterPerTimestep):
		print(time_iteration_data[i].internal_iterations[j].residual_data)





time.sleep(5)
#Create a directory for the output
OutputDir="ForceDataOutput"
if not os.path.exists(OutputDir):
	os.makedirs(OutputDir)
	os.chdir(OutputDir)
else:
	os.chdir(OutputDir)

#Now plot the force 

#Update the force from the pie slice to the whole sperical geometry
Force_Data[:,1:3] = NumSlices*Force_Data[:,1:3]

#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
MaxVal = np.amax(Force_Data[:,1])
MinVal = np.amin(Force_Data[:,1])

#Change the min and max values a little bit so that all data lies within the bounds of the plots
MaxVal = MaxVal + 0.05*abs(MaxVal)
MinVal = MinVal - 0.05*abs(MinVal)
 
plt.plot(Force_Data[:,0],Force_Data[:,1], marker='o')
plt.xlabel('Time (Seconds)')
plt.ylabel('Total Force')
plt.ylim([MinVal, MaxVal])
plt.draw
 
outputFileName = "X_Force_Plot" + ".png"
plt.savefig(outputFileName, bbox_inches='tight')
plt.close()


#Plot Drag Coefficient
CD = np.zeros((non_blank_count,4))
CD[:,1:3] = Force_Data[:,1:3]/(0.5*RhoRef*URef**2*ARef)
CD[:,0] = Force_Data[:,0]

#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
MaxVal = np.amax(CD[:,1])
MinVal = np.amin(CD[:,1])

#Change the min and max values a little bit so that all data lies within the bounds of the plots
MaxVal = MaxVal + 0.05*abs(MaxVal)
MinVal = MinVal - 0.05*abs(MinVal)

plt.plot(CD[:,0],CD[:,1], marker='o')
plt.xlabel('Time (Seconds)')
plt.ylabel('Drag Coefficient in Streamwise Direction')
plt.ylim([MinVal, MaxVal])
plt.draw

outputFileName = "X_Drag_Plot" + ".png"
plt.savefig(outputFileName, bbox_inches='tight')
plt.close()


#Go back to the main directory
os.chdir("..")


print("\n Program has finished... \n")


