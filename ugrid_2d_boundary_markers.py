#! /usr/bin/env python

# Purpose:	Reads a *.ugrid file in the 3D format, and tells you all of the 
#		unique boundary markers. 
#
# Input: 	Name of the UGRID file 
#
# Output: 	A print out of the unique boundary makers in the gird 
#
#	Author: Christopher Neal
#	Date   : 09/27/2016
#	Updated: 09/27/2016
#
########################################################################

import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script

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
# See description at: http://www.simcenter.msstate.edu/software/downloads/doc/ug_io/2d_grid_file_type_ugrid.html

line_count = 0
#Read file header
lines = f.readline()
line = lines.rstrip()
line = line.split()
		
num_nodes = line[0]
num_trias = line[1]
num_quads = line[2]
num_tets = line[3]
num_5pents = line[4]
num_6pents = line[5]
num_hexs = line[6]
line_count = line_count + 1


#loop over the node data, but don't store
while True:
  lines = f.readline()
  line = lines.rstrip()
  line = line.split()
  line_count = line_count + 1
  if line_count > num_nodes : 
    break


#loop over the connectivity data, but don't store
while True:
  lines = f.readline()
  line = lines.rstrip()
  line = line.split()
  line_count = line_count + 1
  if line_count > num_nodes + num_trias + num_quads:
    break


boundary_id_markers = []
#loop over the node data, but don't store
while True:
  lines = f.readline()
  line = lines.rstrip()
  line = line.split()
  if len(line) > 1:
    break

  boundary_id_markers.append(line)


unique_boundary_id_markers = boundary_id_markers.set()

#Print the unique boundary marker ids
print 'Unique Boundary Markers are: ',unique_boundary_id_markers



print("\n Program has finished... \n")

