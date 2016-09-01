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

	def query_dataset(self):
		print "Iteration Number is: ", self.iteration_number
		print "Number of residual entries: ",len(self.residuals_list)
		print "Residual data is: "
		self.print_residual()
	

class timestep_data:
        def __init__(self,TimeStamp=None):
		if TimeStamp is None:
			self.timestamp = "0"
		else:
			self.timestamp = TimeStamp

                self.iteration_list = []

	def add_iteration(self,iteration_data):
		self.iteration_list.append(iteration_data)

	def get_time(self):
		return self.timestamp

	def get_num_iterations(self):
		return len(self.iteration_list)

	def get_starting_residual(self,desired_residual_id):
		return self.iteration_list[0].get_residual(desired_residual_id)
	
	def get_ending_residual(self,desired_residual_id):
                return self.iteration_list[-1].get_residual(desired_residual_id)

	def get_residual(self,iteration_number,desired_residual):
		return self.iteration_list[iteration_number].get_residual(desired_residual)

	def query_dataset(self):
		print "Timestamp value is: ", self.timestamp
		print "Number of Iterations is: ", len(self.iteration_list)


import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import numpy as np
import time
import math
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter



#Store the name of the residual file that is to be analzed.
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

print "Species present in data: ",species_line_found


f.seek(0)  #Rewind file to read through again
residual_tmp = []
residual_found = False
for Line in f:
        if 'R:' in Line and residual_found is False:
                residual_tmp = Line.rstrip()
                residual_tmp = residual_tmp.split()
                residual_found = True
		break

#print residual_tmp
	
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


print "Detected residual list is: ", residual_names


#Loop through entire file the residual data
#Data in the file is structured in the following way(Note that [] is an optional entry):
#R: n it uRes vRes wRes ppRes eRes kRes omegaRes [yRes]    
raw_residual_data = [ line for line in f if 'R:' in line]

#for line in raw_residual_data: 
#	print line.rstrip()

CountingIterations = False
timesteps_counter = 0
timesteps = [] #Initialize the empty list of timesteps
inserted_first_timestep = False
for Line in raw_residual_data:
	lineData = Line.rstrip()
	lineData = lineData.split()
	
	#print "Line Data from file: ", lineData

	timestep_value = lineData[1]
	#print "Timestep in Dataset is: ", timestep_value
	
	iteration_counter = lineData[2] 
	#print "Iteration number is: ",iteration_counter


	#Append this timestep to the list
        residual_list = lineData[3:]
	#print "Residual data is: ",residual_list
	

	if( inserted_first_timestep is False):
		timesteps.append(timestep_data(timestep_value))
		iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
		#iteration_tmp.query_dataset()

		timesteps[timesteps_counter].add_iteration(iteration_tmp)
		#timesteps[timesteps_counter].query_dataset()
		inserted_first_timestep = True

	elif( timesteps[timesteps_counter].get_time() == timestep_value): #Entry that is within the same timestep
                iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
		#iteration_tmp.query_dataset()

                timesteps[timesteps_counter].add_iteration(iteration_tmp)
		#timesteps[timesteps_counter].query_dataset()

	else:  #New timestep detected
		timesteps_counter = timesteps_counter + 1
                timesteps.append(timestep_data(timestep_value))

                iteration_tmp = iteration_data(iteration_counter,len(residual_list),residual_list)
		#iteration_tmp.query_dataset()

                timesteps[timesteps_counter].add_iteration(iteration_tmp)
		#timesteps[timesteps_counter].query_dataset()
	


#Debug
#print "Numer of timesteps detected: ",len(timesteps)
#for i in range(0,len(timesteps)):
#	print "Timestep # ",i+1
#	timesteps[i].query_dataset()




#Debug section to recreate the original input data to verify that nothing was corrupted
#for i in range(0,len(timesteps)):
#	for j in range(0,timesteps[i].get_num_iterations()):
#		print("%s  %d "%(timesteps[i].get_time(),j)),
#		for k,Residual_Name in residual_names.iteritems():
#			print(" %s "%(timesteps[i].get_residual(j,k))),


#Create a directory for the output
OutputDir="residual_plot_data"
if not os.path.exists(OutputDir):
	os.makedirs(OutputDir)
	os.chdir(OutputDir)
else:
	os.chdir(OutputDir)

#Now plot the data



#Plot the total residual drop across every single iteration(timestep and internal iterations per timestep)


#Create a directory for the output
OutputDir="starting_residuals"
if not os.path.exists(OutputDir):
        os.makedirs(OutputDir)
        os.chdir(OutputDir)
else:
        os.chdir(OutputDir)

#Initialize empty lists to store x and y data for plotting
x_vector = np.zeros(len(timesteps))
y_vector = np.zeros(len(timesteps))
for i,Residual_name in residual_names.iteritems():
	#print Residual_name,i
	for j in range(0,len(timesteps)):
		x_vector[j] = float( timesteps[j].get_time() ) 
		y_vector[j] = float( timesteps[j].get_starting_residual(i) )
		#print Residual_name, timesteps[j].get_starting_residual(i), float(timesteps[j].get_starting_residual(i)), y_vector[j]
	
	#Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
	MaxVal = np.amax(y_vector[:])
	MinVal = np.amin(y_vector[:])

	#print "Residual bounds for ",Residual_name," -- Lower: ",MinVal,"    Upper: ",MaxVal

	#Change the min and max values a little bit so that all data lies within the bounds of the plots
	MaxVal = MaxVal + 0.05*abs(MaxVal)
	MinVal = MinVal - 0.05*abs(MinVal)
	
	plt.scatter(x_vector,y_vector, marker='o')
	plt.xlabel('Timestep Number')
	plt.ylabel(Residual_name)
	plt.title("Initial Residuals For Each Timestep")
	plt.ylim([MinVal, MaxVal])
	plt.draw
 
	outputFileName = Residual_name + "_" + "initial_residuals" + ".png"
	plt.savefig(outputFileName, bbox_inches='tight')
	plt.close()

#Go back up to the residual data directory 
os.chdir("..")



####PLOT THE TOTAL RESDUAL HISTORY###
#Create a directory for the output
OutputDir="all_residuals"
if not os.path.exists(OutputDir):
        os.makedirs(OutputDir)
        os.chdir(OutputDir)
else:
        os.chdir(OutputDir)


#Determine the toal number of iterations
total_iterations = 0
for Time in timesteps:
	total_iterations = total_iterations + Time.get_num_iterations()

print "Total number of iterations is: ", total_iterations
	

#Initialize empty lists to store x and y data for plotting
x_vector = np.zeros(total_iterations)
y_vector = np.zeros(total_iterations)
for i,Residual_name in residual_names.iteritems(): #Loop for the different variables

	iteration_count = 0 # Reset to zero for each new variable
        for j in range(0,len(timesteps)):
		for k in range(0,timesteps[j].get_num_iterations()):
                	x_vector[iteration_count] = iteration_count + 1
			#print timesteps[j].get_residual(k,i)
                	y_vector[iteration_count] = float( timesteps[j].get_residual(k,i) )
			iteration_count = iteration_count + 1


        #Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
        MaxVal = np.amax(y_vector[:])
        MinVal = np.amin(y_vector[:])

        print "Residual bounds for ",Residual_name," -- Lower: ",MinVal,"    Upper: ",MaxVal

        #Change the min and max values a little bit so that all data lies within the bounds of the plots
        MaxVal = MaxVal + 0.05*abs(MaxVal)
        MinVal = MinVal - 0.05*abs(MinVal)

        plt.semilogy(x_vector,y_vector, marker='o')
        plt.xlabel('Iteration Number')
        plt.ylabel(Residual_name)
	plt.title("Residual History for Every Iteration")
        plt.ylim([MinVal, MaxVal])
        plt.draw
	#plt.show()

        outputFileName = Residual_name + "_" + "residual_history" + ".png"
        plt.savefig(outputFileName, bbox_inches='tight')
        plt.close()


#Go back up to the residual data directory 
os.chdir("..")




####PLOT THE TOTAL RESDUAL DROP WITHIN EACH TIMESTEP###
#Create a directory for the output
OutputDir="residual_drops"
if not os.path.exists(OutputDir):
        os.makedirs(OutputDir)
        os.chdir(OutputDir)
else:
        os.chdir(OutputDir)


#Initialize empty lists to store x and y data for plotting
x_vector = np.zeros( len(timesteps) )
y_vector = np.zeros( len(timesteps) )
for i,Residual_name in residual_names.iteritems(): #Loop for the different variables
        for j in range(0,len(timesteps)):
		Residual_drop = float( timesteps[j].get_starting_residual(i) ) / float( timesteps[j].get_ending_residual(i) )
        	x_vector[j] = timesteps[j].get_time() 
                y_vector[j] = Residual_drop 


        #Find the maximum value of the variable about to be plotted so that the plot vertical axis can be scaled appropriately
        MaxVal = np.amax(y_vector[:])
        MinVal = np.amin(y_vector[:])

        print "Residual Drop bounds for ",Residual_name," -- Lower: ",MinVal,"    Upper: ",MaxVal

        #Change the min and max values a little bit so that all data lies within the bounds of the plots
        MaxVal = MaxVal + 0.05*abs(MaxVal)
        MinVal = MinVal - 0.05*abs(MinVal)

        plt.semilogy(x_vector,y_vector, marker='o')
        plt.xlabel('Timestep Number')
        plt.ylabel(Residual_name + ": R1/RN")
	plt.title("Residual Drop Within Each Timestep\n(Larger is better)")
        plt.ylim([MinVal, MaxVal])
        plt.draw
        #plt.show()

        outputFileName = Residual_name + "_" + "residual_drop" + ".png"
        plt.savefig(outputFileName, bbox_inches='tight')
        plt.close()






#Go back to the main directory
os.chdir("..")


print("\n Program has finished... \n")

