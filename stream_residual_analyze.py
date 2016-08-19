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


class iteration_data:
	def __init__(self,iteration_num=0,num_residuals=10,residual_list_input=None):
		self.iteration_number = iteration_num
		self.residuals_list = []
		if residual_list_input is None:
			for i in range(0,num_residuals):
				self.residuals_list.append("0.0")
		else:
			for i in range(0,num_residuals):
				self.residuals_list.append(residual_list_input[i])

	def get_residual(self,residual_num):
		return self.residuals_list[residual_num]


	def print_residual(self):
		for i in range(0,len(self.residuals_list)):
			print self.residuals_list[i]


class timestep_data:
        def __init__(self,TimeStamp="0"):
		self.timestamp = TimeStamp
                self.iteration_list = []

	def add_iteration(self,iteration_data):
		self.iteration_list.append(iteration_data)

	def get_time(self):
		return self.timestamp

	def get_starting_residual(self,desired_residual):
		#Desired residual is an integer, while the dict is a key value pair of strings and integers
		return self.iteration_list[0].get_residual(desired_residual)
		
	
	def get_residual(self,iteration_number):
		self.iteration_list[iteration_number].print_residual()


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


#Store the name of the boundary that the user wants to plot the convergence data for.
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



#Store the residual names

#First find out if the simulation was multispecies
line_count = 0
species_line_found = False
for Line in f:
	if 'Species' in Line:
		species_line_found = True
	if species_line_found == True and '}' not in Line:
		line_count = line_count + 1
	if species_line_found == True and '}' in Line:
		break



residual_tmp = []
residual_found = False
for Line in f:
        if 'R:' in Line and residual_found is False:
                residual_tmp = Line.rstrip()
                residual_tmp = residual_tmp.split()
                residual_found = True
		break

	
multi_species = False
if line_count > 1:
	multi_species =True

if(len(residual_tmp[3:]) == 4 ):  #Laminar Incompressible flow, single species(incompressible is always single secies)
	residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual'}
elif(len(residual_tmp[3:]) == 5): # Laminar compressible flow, single species
	residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual',4:'T Residual'}
elif(len(residual_tmp[3:]) == 6):
	if(multi_species == True): #Laminar Compressible, Multi Species
		residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual',4:'T Residual',5:'Y Residual'}
	else: #Turbulent Inconpressible, Single Species
		residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual',4:'k Residual',5:'omega Residual'}
elif(len(residual_tmp[3:]) == 7): #Turbulent compressible, Single species
	residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual',4:'T Residual',5:'k Residual',6:'omega Residual'}
elif(len(residual_tmp[3:]) == 8): #Turbulent compressible, multi species
	residual_names = {0:'U Residual',1:'V Residual',2:'W Residual',3:'P Residual',4:'T Residual',5:'k Residual',6:'omega Residual',7:'Y Residual'}



#Loop through entire file the residual data
#Data in the file is structured in the following way(Note that [] is an optional entry):
#R: n it uRes vRes wRes ppRes eRes kRes omegaRes [yRes]    
residual_data = [ line for line in f if 'R:' in line]

#for line in residual_data: 
#	print line.rstrip()

CountingIterations = False
timesteps_counter = 0
timesteps = [] #Initialize the empty list of timesteps
for Line in residual_data:
	lineData = Line.rstrip()
	lineData = lineData.split()
	
	timestep_value = lineData[1]
	iteration_counter = lineData[2] 

	#Append this timestep to the list
        residual_list = lineData[3:]
	#print residual_list

	if(timesteps_counter == 0):
		timesteps.append(timestep_data(timestep_value))
		iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
		timesteps[timesteps_counter].add_iteration(iteration_tmp)
	elif( timesteps[timesteps_counter].get_time is lineData[1]):
                iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
                timesteps[timesteps_counter].add_iteration(iteration_tmp)
	else:
		timesteps_counter = timesteps_counter + 1
                timesteps.append(timestep_data(timestep_value))
                iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
                timesteps[timesteps_counter].add_iteration(iteration_tmp)


#Debug
print len(timesteps)
for i in range(0,len(timesteps)):
	print i
	timesteps[i].get_residual(0)

#Create a directory for the output
OutputDir="residual_plot_data"
if not os.path.exists(OutputDir):
	os.makedirs(OutputDir)
	os.chdir(OutputDir)
else:
	os.chdir(OutputDir)

#Now plot the data



#Plot the total residual drop across every single iteration(timestep and internal iterations per timestep)

#Initialize empty lists to store x and y data for plotting
x_vector = np.zeros(len(timesteps))
y_vector = np.zeros(len(timesteps))
for i,Residual_name in enumerate(residual_names):
	for j in range(0,len(timesteps)):
		x_vector[j] = float( timesteps[j].get_time() ) 
		print i, j
		y_vector[j] = float( timesteps[j].get_starting_residual(i) )

	
	#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
	MaxVal = np.amax(y_vector[:])
	MinVal = np.amin(y_vector[:])

	#Change the min and max values a little bit so that all data lies within the bounds of the plots
	MaxVal = MaxVal + 0.05*abs(MaxVal)
	MinVal = MinVal - 0.05*abs(MinVal)
	

	plt.plot(Force_Data[:,0],Force_Data[:,1], marker='o')
	plt.xlabel('Timestep Number')
	plt.ylabel(residual_name[Residual_name])
	plt.ylim([MinVal, MaxVal])
	plt.draw
 
	outputFileName = Residual_name + " "+ "initial_timestep_residual" + ".png"
	plt.savefig(outputFileName, bbox_inches='tight')
	plt.close()


#Go back to the main directory
os.chdir("..")


print("\n Program has finished... \n")

