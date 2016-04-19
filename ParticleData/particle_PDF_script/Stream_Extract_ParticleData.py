#! /usr/bin/env python

# Purpose:	Reads the output files from Loci-Stream and parses the contents to extract the
#		particle positions and diameters & averages over time to generate particle
#		diameter PDF plots.
#
#
# Input: 	Base filename where particle data is stored.
#
# Output: 	A data file containing the particle diameter PDF data for the positions and bin widths
#		specified.
#
#		
#
#	Author: Christopher Neal
#	Date   : 11/20/2015
#	Updated: 04/06/2016
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
from ParticleStatsModule import *
from Read_hdf5_particle import *
from ParticleBinClass import ParticleBinData

#For calling the h5dump shell script
ShellScriptPath="/home/neal/codes/locistream/stream_scripts/ParticleData/particle_PDF_script"

#Diameter Bin Parameters
BinFlag = 1 #1 for using diameter bins and 0 for no bins when computing PDF

Diameter_Min = 0.0
Diameter_Max = 100.0e-6
nDBins = 100


#Radial Bins Information: There is an implicit assumption that the axis of the jet corresponds to y=0, therefore allowing for the following formula to be used: r = sqrt(y^2 + z^2)
RadialBinFlag = 1 # 0 for cartesian y bins, 1 for cylindrical R bins. If 1, treat y variable as r in code

#Non-Dimensionalization Parameters
Dl = 0.0105 #Diameter of liquid injection

#Start & Stop value of particle data file indices
iStart = 800
iStep = 200
iEnd = 3400


#Particle statistics user definition section
nXBins = 4
XMin = 0.0
XMax = 0.21    

nYBins = 5
YMin = 0.0
YMax = 15.75e-3

"""
#For debugging
#Particle statistics user definition section
nXBins = 5
XMin = 0.0
XMax = 0.01

nYBins = 5
YMin = 0.0
YMax = 3.0e-3
"""

#Compute and store data filename numbers
NumFiles = (iEnd-iStart)/iStep
FileIndices = []
iIterate=iStart
for i in range(0,NumFiles):   #make list of timestamps
	FileIndices.append(iIterate)
	iIterate = iIterate + iStep
print(FileIndices)

#Compute spatial bin width
dx = (XMax-XMin)/nXBins
dy = (YMax-YMin)/nYBins

#Compute Bin coordinates
X_Bin_Coords = np.zeros((2,nXBins)) #Create array of location of X bin coordinates
Y_Bin_Coords = np.zeros((2,nYBins)) #Create array of location of Y bin coordinates

#Store coordinates of X bin edges
X_Bin_Coords[0][0] = XMin
X_Bin_Coords[1][0] = XMin + dx
for i in range(1,nXBins):
	X_Bin_Coords[0][i] = X_Bin_Coords[1][i-1]
        X_Bin_Coords[1][i] = X_Bin_Coords[0][i] + dx

print("X Bin Coordinates are:")
for i in range(0,nXBins):
	print("Bin %d \t%10.2E\t%10.2E"%(i+1,X_Bin_Coords[0][i],X_Bin_Coords[1][i]))


#Store coordinates of Y bin edges
Y_Bin_Coords[0][0] = YMin
Y_Bin_Coords[1][0] = YMin + dy
for i in range(1,nYBins):
        Y_Bin_Coords[0][i] = Y_Bin_Coords[1][i-1]
        Y_Bin_Coords[1][i] = Y_Bin_Coords[0][i] + dy

print("\n\nY Bin Coordinates are:")
for i in range(0,nYBins):
        print("Bin %d \t%10.2E\t%10.2E"%(i+1,Y_Bin_Coords[0][i],Y_Bin_Coords[1][i]))


#Store the casename from the user's input to the script
CaseName = str(sys.argv[1])
print("\nCase name is: %s"%(CaseName))

#Initialize 3D array of objects to hold particle data for all bins in each data file. Creates NumFiles x nXBins x nYBins array
PDF_Data = [[[ParticleBinData() for k in range(nYBins)] for j in range(nXBins)] for i in range(NumFiles)] 

#Idiot check to make sure data structure is initialized correctly
#CountI = 0
#CountJ = 0
#CountK = 0
#for i in range(0,NumFiles):
#	CountI = CountI + 1
#	for j in range(0,nXBins):
#		if(i==0):
#			CountJ = CountJ + 1

#		for k in range(0,nYBins):
#			if(i==0 and j == 0):
#				CountK = CountK + 1

#			PDF_Data[i][j][k].print_data()

#print(CountI,CountJ,CountK)
		
for i in range(0,NumFiles):

	#Read particle data from HDF5 data files
	print("Reading Data from file: %d"%(i+1))
	ParticleData=Read_HDF5_Particle_Data(CaseName,FileIndices[i],ShellScriptPath)

	#Compute size of ParticleData 2D list
	numrows = len(ParticleData)  
        numcols = len(ParticleData[0])


	#Now we have all particle data in the file we now process the data
        #Allocate a numpy array to store the floating point data & copy into array
        RealParticleData=np.zeros((numrows,numcols))
        for j in range(0,numrows):
                for k in range(0,numcols):
                        RealParticleData[j][k] = float(ParticleData[j][k])


	#Store particle radius in the y and z positions of the data array
        if(RadialBinFlag == 1):
                for k in range(0,numrows):
                        RealParticleData[k][2] = math.sqrt(RealParticleData[k][2]**2 + RealParticleData[k][3]**2)
                        RealParticleData[k][3] = RealParticleData[k][2]


	NumParcels = numrows

	#Loop over all bins and store data about particles within the bin

	#Initialize PDF coordinates arrays
	PDF_X_Coords = np.zeros(nXBins)
	PDF_Y_Coords = np.zeros(nYBins)
	for j in range(0,nXBins):
		PDF_X_Coords[j] =  0.5*( X_Bin_Coords[1][j] + X_Bin_Coords[0][j] )  #Mean of X bin boundaries i.e. middle of X bins

	for j in range(0,nYBins):
		PDF_Y_Coords[j] =  0.5*( Y_Bin_Coords[1][j] + Y_Bin_Coords[0][j] )  #Mean of Y bin boundaries i.e. middle of Y bins

	#Loop over Y bins & sweep over the X bins and store particle information
	print("Counting Particles for File: %d"%(i+1))
	for j in range(0,nXBins):
		
		print("Computing PDF for X-bin:\t%d"%(j+1))
		for k in range(0,nYBins):
			print("\tComputing PDF for Y-bin:\t%d"%(k+1))
			ParcelsInBinCount = 0
			for m in range(0,NumParcels):  #Loop over all parcels to find which are in the current bin
				if(RealParticleData[m][1] < X_Bin_Coords[1][j] and RealParticleData[m][1] >= X_Bin_Coords[0][j] and 
					RealParticleData[m][2] < Y_Bin_Coords[1][k] and RealParticleData[m][2] >= Y_Bin_Coords[0][k] ):
					#print("i = %d\tj = %d\tk = %d\n"%(i+1,m+1,k+1))
					PDF_Data[i][j][k].add_data(ParticleData[m][0], ParticleData[m][4])
					ParcelsInBinCount = ParcelsInBinCount + 1
			print("\t\tNumber of Parcels in X Bin(%d) & Y Bin(%d) is:\t %d"%(j+1,k+1,ParcelsInBinCount))
		


print("Compressing particle diameter data 1 comprehensive diameter PDF data set")
#Compress each of the data structures to make sure there are no repeated diameter entries(makes data set smaller)
for i in range(0,NumFiles):
	for j in range(0,nXBins):
		for k in range(0,nYBins):
			PDF_Data[i][j][k].compress_data
	



print("Performing a sort on the particle diameter data to improve performance")
#Sort diameter data in the data structure to speed up the merging process
for i in range(0,NumFiles):
        for j in range(0,nXBins):
                print("Sorting X Bin: %d\n"%(j+1))
                for k in range(0,nYBins):
                        print("Sorting Y Bin: %d\n"%(k+1))
                        PDF_Data[i][j][k].sort_diameters() 


print("Merging data over all files")
#Compute a time averaged PDF by averaging over all time entries
AVG_PDF = [[ParticleBinData() for k in range(nYBins) ]for j in range(nXBins)]
for i in range(0,NumFiles):
	print("Merging Data from File: %d"%(i+1))
	for j in range(0,nXBins):
		print("\tMerging X Bin: %d"%(j+1))
		for k in range(0,nYBins):
			print("\t\tMerging Y Bin: %d"%(k+1))
			if(i == 0):
				AVG_PDF[j][k] = PDF_Data[i][j][k]
			else:
				AVG_PDF[j][k] =  AVG_PDF[j][k] + PDF_Data[i][j][k]


	print("Data file %d successfully merged\n"%(i))


#For Debugging 
#for i in range(0,nYBins):
#        for j in range(0,nXBins):
#                AVG_PDF[i][j].print_data()


if(BinFlag == 1): #Use the user defined bins
	print("Re-Mapping Particle Diameter data to user-defined bins")

	#Compute the user defined bin coordinates
	UserDefinedBins = []
	UserDefinedBins.append([])
	UserDefinedBins.append([])
	
	#Store the Delta-D bin spacing
	DeltaD = float((Diameter_Max-Diameter_Min))/nDBins

	for i in range(0,nDBins):
		UserDefinedBins[0].append( str(Diameter_Min + DeltaD*i) )
		UserDefinedBins[1].append( str(Diameter_Min + DeltaD*(i+1)) )

	#Re-Bin all of the diameter data
	for i in range(0,nXBins):
		for j in range(0,nYBins):
			AVG_PDF[i][j].custom_bins(UserDefinedBins)



print("Writing Output Data")
#Write the Average PDF Data to a file of the same basename as the particle data file
OutputFileName= CaseName + "_PDF" + "_" + str(i) + "." + "dat"
f_output = open(OutputFileName,"w")

#Write the output so that all of the Y data for a particular X bin is contained within 1 file. The file will match in essence the
#format used for the experimental data file so that post-processing the data will be made faster.
for i in range(0,nXBins):
        OutputFileName = CaseName + "_PDF_" + '%s_%4.2f_Data'%('XOverD_',PDF_X_Coords[i]/Dl) + ".txt"
        f_output = open(OutputFileName,"w")

	f_output.write("%s\t%s %10.6E\n"%("X Coordinate","X/D = ",PDF_X_Coords[i]/Dl))
	
	f_output.write("\n")
	f_output.write("\n")
	f_output.write("\n")
	f_output.write("\n")
	
	f_output.write("%s\t%s\t"%("Radial Coordinate","r/D = ") )
	
	for j in range(0,len(PDF_Y_Coords)):
		f_output.write("%10.6E\t"%(PDF_Y_Coords[j]/Dl))

	f_output.write("\n")
	f_output.write("\n")
	f_output.write("\n")
	f_output.write("\n")	
	f_output.write("\n")

	for m in range(0,nDBins):
	
		f_output.write("%10.6E\t"%( 0.5*(float(UserDefinedBins[0][m]) + float(UserDefinedBins[1][m]) ) ) )

        	for j in range(0,nYBins):
                	f_output.write("%10.6E\t"%( float(AVG_PDF[i][j].ParticlesPerParcel[m]) ))
	
		f_output.write("\n")

	f_output.close()




#####Plot output data##########

#Create output directory and enter the directory
FilePathBase =os.getcwd()
OutPutDir = FilePathBase +"/PDFPlots"
if not os.path.exists(OutPutDir):
	os.makedirs(OutPutDir)
	os.chdir(OutPutDir)
else:
	os.chdir(OutPutDir)


#Plot PDF variable over diameter space. That is, for a given x value, make plots of D Versus N at the different values of the radial coordinate.
DiameterFactor = 1e6

#Plot data about radial distribution of particles at each X coordinate
for i in range(0,nXBins):

	for j in range(0,nYBins):

		#Find the maximum value of the variable about to be plotted so that the 
		#plot vertical axis can be scaled appropriately
		MaxVal = float(max(AVG_PDF[i][j].ParticlesPerParcel))
		MinVal = float(min(AVG_PDF[i][j].ParticlesPerParcel))

		#Change the min and max values a little bit so that all data lies within the bounds of the plots
		MaxVal = MaxVal + 0.05*abs(MaxVal)
		MinVal = MinVal - 0.05*abs(MinVal)
			

		xValues = np.asarray(AVG_PDF[i][j].ParticleDiameters)
		for m in range(0,len(AVG_PDF[i][j].ParticleDiameters)):
			xValues[m] = float(xValues[m])*float(DiameterFactor)
		
		yValues = np.asarray(AVG_PDF[i][j].ParticlesPerParcel)
	
		plt.plot(xValues,yValues, marker='o')
		plt.xlabel('Parcel Diameter, D micrometer')
		plt.ylabel('Parcel Count, N')
		plt.ylim([MinVal, MaxVal])

		if(RadialBinFlag == 1):
			DimensionName = 'R'
		else:
			DimensionName = 'Y'

		outputFileName = CaseName + '_PDF_' + '%s%4.2f%s'%('X',PDF_X_Coords[i]/Dl,'_')+ '%s%4.2f%s'%(DimensionName,PDF_Y_Coords[j]/Dl,'_') + ".png"
		print("Saving a figure to:%s\n"%(outputFileName))
		plt.savefig(outputFileName, bbox_inches='tight')
		plt.close()


#Go back to the original data directory
os.chdir("..")


print("\n Program has finished... \n")


