#! /usr/bin/env python
# Purpose:	Reads in a file containing two columns of names. The first column is the species name in the
#		.mdl file and the second column is the corresponding species name in the ascii flamelet table.
#		particle positions and diameters & averages over time to generate particle
#		diameter PDF plots.
#
#
# Input: 	(1) - Name of ascii flamelet table to be adjusted
#		(2) - Name of ascii file from which to read the desired species name subsitutions 
#
# Output: 	An updated ascii flamelet table containing the proper species names that were provided by the user.
#		specified.
#
#		
#
#	Author: Christopher Neal
#	Date   : 03/22/2016
#	Updated: 03/22/2016
#
########################################################################


import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import time #For deubbging
from shutil import copyfile


#Store user input filename
try:
	speciesNameKeyFilename = sys.argv[2]
	flameletTableFilename = sys.argv[1]
except:
	print("Error reading inputs")

print("Reading species name swaps from: %s"%speciesNameKeyFilename)
print("Operating on flamelet table: %s"%flameletTableFilename)


#Read in data from name key file
try:
	speciesNameKeyFile = open(speciesNameKeyFilename,'r')
except:
	print("Error Opening name key file")

originalSpeciesNames = []
newSpeciesNames = []
for Line in speciesNameKeyFile:

	tmp = Line.rstrip()
	tmp = tmp.split()

	originalSpeciesNames.append(tmp[0])
	newSpeciesNames.append(tmp[1])
	


print("Original Species Name - New Species Name :")
for i in range(0,len(originalSpeciesNames)):
	print("%s\t-> %s\n"%(originalSpeciesNames[i], newSpeciesNames[i])).expandtabs(16)


#Open the flamelet table file for reading
try:
        flameletTableFile = open(flameletTableFilename,'r')
except:
        print("Error Opening flamelet table input file")

#Store flamelet table file data
flameletTableData = flameletTableFile.read()

flameletTableFile.close()

#Loop over species rename list and replace aall instances in the copied flamelet table file
for i,SpeciesName in enumerate(originalSpeciesNames):
	
	flameletTableData = flameletTableData.replace(SpeciesName,newSpeciesNames[i])


#Open the a new flamelet table file
try:
        flameletTableFile = open(flameletTableFilename+"_new",'w')
except:
        print("Error Opening flamelet table output file")

flameletTableFile.write(flameletTableData)
flameletTableFile.close()


print("Program Finished...")

