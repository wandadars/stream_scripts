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
#	Author: Christopher Neal
#	Date   : 11/20/2015
#	Updated: 05/11/2016
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
from Read_hdf5_particle import HDF5_Particle_Data_Reader
from ParticleBinClass import ParticleBinCell,ParticleBinDomain
from utilities import *

#For calling the h5dump shell script
ShellScriptPath="/home/neal/codes/locistream/stream_scripts/ParticleData/particle_PDF_script"

#Diameter Bin Parameters
BinFlag = 1 #1 for using diameter bins and 0 for no bins when computing PDF

Diameter_Min = 0.0
Diameter_Max = 150.0e-6
nDBins = 150


#Radial Bins Information: There is an implicit assumption that the axis of the jet corresponds to y=0, therefore allowing for the following formula to be used: r = sqrt(y^2 + z^2)
RadialBinFlag = 0 # 0 for cartesian y bins, 1 for cylindrical R bins. If 1, treat y variable as r in code

#Non-Dimensionalization Parameters
Dl = 0.0105 #Diameter of liquid injection

#Start & Stop value of particle data file indices
iStart = 10000
iStep = 100
iEnd = 21000


#Particle statistics user definition section
nXBins = 3
XMin = 0.0
XMax = 210e-3 

nYBins = 6
YMin = 0.0
YMax = 10.5e-3  
#nYBins = 4
#YMin = 0.0
#YMax = 21e-3  #Old value 15.75e-3

"""
#Particle statistics user definition section
nXBins = 10
XMin = 0.0
XMax = 12.6e-3      

nYBins = 10
YMin = 0.0
YMax = 5.25e-3  #Old value 15.75e-3
"""

"""
#For debugging
#Particle statistics user definition section
nXBins = 2
XMin = 0.0
XMax = 0.01

nYBins = 3
YMin = 0.0
YMax = 2.0e-3

"""

FileIndicies = compute_filename_numbers(iStart,iEnd,iStep)

particle_bin_domain = ParticleBinDomain(XMax,XMin,YMax,YMin,nXBins,nYBins)

#Compute Bin coordinates
X_Bin_Coords = particle_bin_domain.compute_x_bin_coords()
particle_bin_domain.print_x_bin_coords(Dl)
Y_Bin_Coords = particle_bin_domain.compute_y_bin_coords() 
particle_bin_domain.print_y_bin_coords(Dl)

#Store the casename from the user's input to the script
CaseName = str(sys.argv[1])
print("\nCase name is: %s"%(CaseName))

#Initialize 3D array of objects to hold particle data for all bins in each data file. Creates NumFiles x nXBins x nYBins array
PDF_Data = [[[ParticleBinCell() for k in range(nYBins)] for j in range(nXBins)] for i in range(len(FileIndicies))] 

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
for i,time_stamp in enumerate(FileIndicies):

	#Read particle data from HDF5 data files
	print("Reading Data from file: %d"%(i+1))
	hdf5_data_reader = HDF5_Particle_Data_Reader(CaseName,time_stamp,ShellScriptPath)
        ParticleData = hdf5_data_reader.read_hdf_particle_data()  

	#Compute size of ParticleData 2D list
	numrows = len(ParticleData)  
        numcols = len(ParticleData[0])

	print("Number of parcels in dataset %d :\t%d"%(i+1,numrows))

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
	PDF_X_Coords = particle_bin_domain.compute_x_bin_center_coords() 
	PDF_Y_Coords = particle_bin_domain.compute_y_bin_center_coords()
	
        #Loop over Y bins & sweep over the X bins and store particle information
	print("Counting Particles for File: %d"%(i+1))
	for j in range(0,nXBins):
		
	    print("Placing parcels into X-bin:\t%d"%(j+1))
	    for k in range(0,nYBins):

	        print("\tPlacing parcels into Y-bin:\t%d"%(k+1))
		ParcelsInBinCount = 0
		for m in range(0,NumParcels):  #Loop over all parcels to find which are in the current bin
		    if(RealParticleData[m][1] < X_Bin_Coords[1][j] and RealParticleData[m][1] >= X_Bin_Coords[0][j] and 
		       RealParticleData[m][2] < Y_Bin_Coords[1][k] and RealParticleData[m][2] >= Y_Bin_Coords[0][k] ):
			#print("i = %d\tj = %d\tk = %d\n"%(i+1,m+1,k+1))
			PDF_Data[i][j][k].add_data(ParticleData[m][0], ParticleData[m][4])
			ParcelsInBinCount = ParcelsInBinCount + 1
		
                print("\t\tNumber of Parcels in X Bin(%d) & Y Bin(%d) is:\t %d"%(j+1,k+1,ParcelsInBinCount))
		


print("Performing a Sort on the particle diameter data to improve performance")
#Sort diameter data in the data structure to speed up the merging process
for i in range(0,len(FileIndicies)):
    for j in range(0,nXBins):
        print("\nSorting X Bin: %d"%(j+1))
        for k in range(0,nYBins):
            print("\tSorting Y Bin: %d"%(k+1))
            PDF_Data[i][j][k].sort_diameters()


print("Merging data over all files")
#Compute a time averaged PDF by averaging over all time entries
AVG_PDF = [[ParticleBinCell() for k in range(nYBins) ]for j in range(nXBins)]
for i in range(0,len(FileIndicies)):
    print("Merging Data from File: %d"%(i+1))
    for j in range(0,nXBins):
	print("\tMerging X Bin: %d"%(j+1))
	for k in range(0,nYBins):
	    print("\t\tMerging Y Bin: %d"%(k+1))
	    if(i == 0):
	    	AVG_PDF[j][k] = PDF_Data[i][j][k]
	    else:
	    	AVG_PDF[j][k] =  AVG_PDF[j][k] + PDF_Data[i][j][k]
			    
            #Sort and compress the new output
            AVG_PDF[j][k].sort_diameters()

    print("Data file %d successfully merged\n"%(i+1))


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
	DeltaD = float((Diameter_Max-Diameter_Min))/float(nDBins)
	print("Using diameter bin width of: %10.6E"%(DeltaD))
	print("Bin #\t\tLeft Bin Coord\t\tRight Bin Coord")
	for i in range(0,nDBins):
	    UserDefinedBins[0].append( str(Diameter_Min + DeltaD*i) )
	    UserDefinedBins[1].append( str(Diameter_Min + DeltaD*(i+1)) )
	    print("%d\t\t%s\t\t\t%s"%(i+1,UserDefinedBins[0][i],UserDefinedBins[1][i]))


	#Re-Bin all of the diameter data using the newly defined diameters
	for i in range(0,nXBins):
	    for j in range(0,nYBins):
		AVG_PDF[i][j].sort_particlesPerParcel()
		AVG_PDF[i][j].custom_bins(UserDefinedBins)
		AVG_PDF[i][j].sort_diameters()




print("Writing Output Data")

#Create output directory and enter the directory
FilePathBase =os.getcwd()
OutPutDir = FilePathBase +"/particle_PDF_data"
if not os.path.exists(OutPutDir):
    os.makedirs(OutPutDir)
    os.chdir(OutPutDir)
else:
    os.chdir(OutPutDir)

#Write the output so that all of the Y data for a particular X bin is contained within 1 file. The file will match in essence the
#format used for the experimental data file so that post-processing the data will be made faster.
for i in range(0,nXBins):
    print "Writing data for X bin ",i+1," located at: ",PDF_X_Coords[i]

    OutputFileName = CaseName + "_PDF_" + '%s_%4.2f_Data'%('XOverD',PDF_X_Coords[i]/Dl) + ".txt"
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

    if(BinFlag == 1):
        for m in range(0,nDBins):
            f_output.write("%10.6E\t"%( 0.5*(float(UserDefinedBins[0][m]) + float(UserDefinedBins[1][m]) ) ) )

            for j in range(0,nYBins):   #used to be nYBins
                #print "\tWriting data for Transverse bin ",j+1," located at: ",PDF_Y_Coords[j]
                f_output.write("%10.6E\t"%( float(AVG_PDF[i][j].ParticlesPerParcel[m]) ))
    
            f_output.write("\n")
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
        for k in range(0,AVG_PDF[i][j].NumElements):
            if(k==0):
                MaxVal = float(AVG_PDF[i][j].ParticlesPerParcel[k])
                MinVal = float(AVG_PDF[i][j].ParticlesPerParcel[k])

            elif(float(AVG_PDF[i][j].ParticlesPerParcel[k])>MaxVal):
                MaxVal = float(AVG_PDF[i][j].ParticlesPerParcel[k])

            elif(float(AVG_PDF[i][j].ParticlesPerParcel[k])<MinVal):
                MinVal = float(AVG_PDF[i][j].ParticlesPerParcel[k])
                

        #Change the min and max values a little bit so that all data lies within the bounds of the plots
        MaxVal = MaxVal + 0.05*abs(MaxVal)
        MinVal = MinVal - 0.05*abs(MinVal)
                

        xValues = np.asarray(AVG_PDF[i][j].ParticleDiameters)
        for m in range(0,len(AVG_PDF[i][j].ParticleDiameters)):
            xValues[m] = float(xValues[m])*float(DiameterFactor)
        
        yValues = np.asarray(AVG_PDF[i][j].ParticlesPerParcel)

        plt.plot(xValues,yValues, marker='o',linestyle='None')
        plt.xlabel('Parcel Diameter, D micrometer')
        plt.ylabel('Parcel Count, N')
        plt.ylim([MinVal, MaxVal])

        if(RadialBinFlag == 1):
            DimensionName = 'R'
        else:
            DimensionName = 'Y'

        outputFileName = CaseName + '_PDF_' + '%s%4.2f%s'%('XoverD',PDF_X_Coords[i]/Dl,'_') + '%soverD%4.2f'%(DimensionName,PDF_Y_Coords[j]/Dl) + ".png"
        print("Saving a figure to:%s\n"%(outputFileName))
        plt.savefig(outputFileName, bbox_inches='tight')
        plt.close()


#Go back to the original data directory
os.chdir("../..")


print("\n Program has finished... \n")


