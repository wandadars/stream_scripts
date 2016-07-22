#! /usr/bin/env python

# Purpose:	Rotates a 2d grid made by AFLR2D into a 3D axisymmetric grid.
#
#
# Input: 	Base filename of the grid and the angular resolution of the 3D grid.
#
# Output: 	A 3D grid.
#		
#
#	Author: Christopher Neal
#	Date   : 07/08/2016
#	Updated: 07/08/2016
#
########################################################################


import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import time
import subprocess

source_path = os.path.dirname(os.path.abspath(__file__))
shell_script_path=source_path+"/program_operations.sh "
print "Executing file: ", shell_script_path

run_directory = os.getcwd()
print "Running in Directory: ",run_directory



grid_base_name="injector_3d" #Name of the grid i.e. <name>.vog
boundary_1 = "BC_28" #Name of boundary face that is not rotated on the pie slice
boundary_2 = "BC_27" #Name of boundary face that IS rotated on the pie slice
theta_0 = 4 #Angle of initial provided pie-slice sector that was generated from AFLR2d
epsilon = 1e-6 #Define the smallest number that you want to call zero



#Make sure that the initial angle goes equally into 360 degrees
a = 360.0/theta_0
b = a % 1  #To get the decimal remainder from the division

good_to_go = False
if( abs(b) >= epsilon ) :
	print "Error, pie slice does not go evenly into 360 degrees. Make new slice"
else:
	num_rotations = int(360.0/theta_0) - 1  #minus 1 because we start with the original pie slice
	print "Rotating pie slice of: ",theta_0," degrees, ",num_rotations," times."	
	good_to_go = True


if( good_to_go == True):
	for i in range(0,num_rotations):

		if(i == 0 ):
			#Rename the left and right boundaries to face1 and face2
			subprocess.call("%s %s %s %s %s" %(shell_script_path,grid_base_name, "0", boundary_1, boundary_2),shell=True)

			#Rotate the pie slice
			rotation_angle = theta_0*(i+1)
			subprocess.call("%s %s %s %s"%(shell_script_path,grid_base_name,"1",str(rotation_angle)),shell=True)

			#Glue the two faces together
			subprocess.call("%s %s %s" % (shell_script_path,grid_base_name,"2"),shell=True)
			
		elif( i == num_rotations -1):
			#Rotate the pie slice
                        rotation_angle = theta_0*(i+1)
                        subprocess.call("%s %s %s %s" % (shell_script_path,grid_base_name,"1",str(rotation_angle)),shell=True)

			#Glue the final two faces together
			subprocess.call("%s %s %s" % (shell_script_path,grid_base_name,"4"),shell=True)

		else:
			#Rotate the pie slice to the new position
			rotation_angle = theta_0*(i+1)
                        subprocess.call("%s %s %s %s" % (shell_script_path,grid_base_name,"1",str(rotation_angle)),shell=True)

			#Glue the touching faces together
			subprocess.call("%s %s %s" % (shell_script_path,grid_base_name,"3"),shell=True)



print("\n Program has finished... \n")


