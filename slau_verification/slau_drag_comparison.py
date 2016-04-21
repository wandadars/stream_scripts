#! /usr/bin/env python

# Purpose:	Reads the output file from Loci-Stream and parses the contents to extract the
#		forces on a user defined boundary and writes the data to new files.
#
# Input: 	Name of the boundary condition to extract force data from
#
# Output: 	A force file for the boundary marker in the domain.
#
#
#	Author: Christopher Neal
#	Date   : 01/22/2016
#	Updated: 01/22/2016
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


#IMPORTANT PARAMETERS TO CHECK BEFORE RUNNING
PieSliceAngle = 1.0  #This is used to compute total force on a pie slice domain

#Normalization Properties
RhoRef = 1.375478   #kg/m^3
URef = 116.7856     #m/s
ARef = math.pi*(0.04)**2	#Particle radius us 40mm

#For Rocflu Data conversion to match other data sets
TRef = 293	#pre-shock temperature in Kelvin
MachRef = 1.22  #Shock Mach number
Radius = 40e-3	#Radius of the 80mm diameter particle
gamma = 1.4	#Specific heat ratio of air
RGas = 287.04	#Specific heat of air (J/kg k)

#Compute how many sectors are necessary to recover the full spherical domain
NumSlices = 360.0/PieSliceAngle

#Store the name of the boundary that the user wants to plot the force data over.
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



#Loop through entire file to extract force contents
#Data in the file is structured in the following way:
#iteration, simulation time, mass flux, Fx, Fy, Fz, energy flux, area
Force_Data = np.zeros((non_blank_count,4))
count = 0 #For placing items into array
for Line in f:

	lineData = Line.rstrip()
	lineData = lineData.split()
		
	Force_Data[count,0] = lineData[1]  # simulation time
	Force_Data[count,1] = lineData[3]  # Fx
	Force_Data[count,2] = lineData[4]  # Fy
	Force_Data[count,3] = lineData[5]  # Fz

	count = count + 1

f.close()

#Go back to the main directory
os.chdir("..")





#Read the Experimental Data File into memory
ExperimentalDataFileName = "ExperimentalData.txt"
#Test to see if the file exists, otherwise throw exception
try:
  os.path.isfile(ExperimentalDataFileName)
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise

#Count number of non-blank lines in file
NumLines = 0
with open(ExperimentalDataFileName,"r") as infp:
    for line in infp:
       if line.strip():
          NumLines += 1
print("number of lines found %d\n"%(NumLines))

#open file if file exists, otherwise throw exception
try:
  f=open(ExperimentalDataFileName,"r")
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise


#Loop through entire file to extract Experimental drag coefficient contents
#Data in the file is structured in the following way:
#iteration, simulation time, mass flux, Fx, Fy, Fz, energy flux, area
Experimental_CD_Data = np.zeros((NumLines,2))
count = 0 #For placing items into array
for Line in f:

        lineData = Line.rstrip()
        lineData = lineData.split()

        Experimental_CD_Data[count,0] = lineData[0]  # simulation time
        Experimental_CD_Data[count,1] = lineData[1]  # Fx

        count = count + 1

f.close()

#Convert Experimental CD Data time to seconds to match the simulation data
Experimental_CD_Data[:,0] = (10.0**-6)*Experimental_CD_Data[:,0] 




#Read the Rocflu Simulation Data File into memory
RocfluDataFileName = "RocfluShockData.txt"
#Test to see if the file exists, otherwise throw exception
try:
  os.path.isfile(RocfluDataFileName)
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise

#Count number of non-blank lines in file
NumRocfluLines = 0
with open(RocfluDataFileName,"r") as infp:
    for line in infp:
       if line.strip():
          NumRocfluLines += 1
print("number of lines found in Rocflu Data %d\n"%(NumRocfluLines))

#open file if file exists, otherwise throw exception
try:
  f=open(RocfluDataFileName,"r")
except IOError as e:
  print "I/O error({0}): {1}".format(e.errno, e.strerror)
  raise


#Loop through entire file to extract Rocflu drag coefficient contents
#Data in the file is structured in the following way:
# non-dimensional time, drag coefficient
Rocflu_CD_Data = np.zeros((NumRocfluLines,2))
count = 0 #For placing items into array
for Line in f:

        lineData = Line.rstrip()
        lineData = lineData.split()

        Rocflu_CD_Data[count,0] = lineData[0]  # simulation time
        Rocflu_CD_Data[count,1] = lineData[1]  # Fx

        count = count + 1

f.close()

#Convert Experimental CD Data time to seconds to match the simulation data
Rocflu_CD_Data[:,0] = (Radius/(MachRef*math.sqrt(gamma*RGas*TRef)))*Rocflu_CD_Data[:,0]





#Now plot & output the force data to an output directory


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

#Because we are comparing experimental results we need to shift our plot so that the origins are the same. Let the origin of the
#simulation data be shifted by whatever time it takes to make the drag at time 0 be 1
CD = np.zeros((non_blank_count,4))
CD[:,1:3] = Force_Data[:,1:3]/(0.5*RhoRef*URef**2*ARef)
CD[:,0] = Force_Data[:,0]


TimeLoc = 0
for i in range(0,non_blank_count):

	if(CD[i,1]<=1.0):
		TimeLoc = i
	else:
		break

CD[:,0] = CD[:,0] - CD[TimeLoc,0]
#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
MaxVal = np.amax(CD[:,1])
MinVal = np.amin(CD[:,1])

#Change the min and max values a little bit so that all data lies within the bounds of the plots
MaxVal = MaxVal + 0.05*abs(MaxVal)
MinVal = MinVal - 0.05*abs(MinVal)

plt.plot(CD[:,0],CD[:,1], marker='.', label='Stream SLAU')
plt.plot(Experimental_CD_Data[:,0],Experimental_CD_Data[:,1], marker='x',label='Sun Exp Data')
plt.plot(Rocflu_CD_Data[:,0],Rocflu_CD_Data[:,1], marker='.', label='Rocflu AUSM+')
plt.xlabel('Time (Seconds)')
plt.ylabel('Drag Coefficient in Streamwise Direction')
plt.ylim([-1.0, 10])
legend = plt.legend(loc='upper right', shadow=True)

# The frame is matplotlib.patches.Rectangle instance surrounding the legend.
frame = legend.get_frame()
frame.set_facecolor('0.90')

# Set the fontsize
for label in legend.get_texts():
    label.set_fontsize('large')

for label in legend.get_lines():
    label.set_linewidth(1.5)  # the legend line width

plt.draw

outputFileName = "X_Drag_Plot" + ".png"
plt.savefig(outputFileName, bbox_inches='tight')
plt.close()


#Go back to the main directory
os.chdir("..")


print("\n Program has finished... \n")


