#! /usr/bin/env python
#######################################################################################
# The purpose of this script is to read in a data file containing probability density
# function data for particle diameter distributions away from a spray jet and plot
# the data.
#
# Author: Christopher Neal
#
# Date: 02-15-2016
# Updated: 05-16-2016
#
#######################################################################################


#### import modules
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats 
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import time
import random  #For random number generation
import os
import string
import itertools

#Specify the path to the Data file that contains the formatted slice data
#"""
#Experimental Data Set
InputFileName="SP2_xD0.3_DropDis.dat"
FilePathBase = "/Users/chris1/Dropbox/Streamine_Numerics/Stream_VV_Cases/Fall_2015_Cases/Droplet_Vaporization/Acetone-non-reacting/Experiment_A/Non_reacting_spray_jets/SP2/xD_0.3/Droplet_Distribution"
OutputFileName = "SP2_xD0.3_DropDis_NumberedWeightedLogFit" #User changes this
#"""

"""
#Simulation Data set
InputFileName="acetone_PDF_XOverD__0.30_Data.txt"
FilePathBase = "/Users/chris1/Desktop/PDFPlots_nobreakup"
OutputFileName = "acetone_PDF_XOverD__0.30_Data_MassWeightedLogFit" #User changes this
#OutputFileName = "acetone_PDF_XOverD__0.30_Data_NumberedWeightedLogFit" #User changes this
"""


#Debug flag
DebugFlag = 0	#0 for off, 1 for on

WeibullPlotFlag = 0  #1 to fit data to Weibull distribution and show on plots, 0 to leave out

#Flag for averaging the PDF over all radii
RadiusAverageFlag = 1	# 0 - only take first value, 1 - average over all radial PDFs in data file

#Provide the density of the liquid for converting number weighted droplet diameter PDFs to mass weighted droplet mass PDF.
MassWeightedFlag = 0	# 0 for using the original diameter data, 1 for converting to mass weighted PDF
#LiquidDensity = 791  #kg/m^3
LiquidDensity = 791e12	#kg/micrometersm^3


PlotImageFormat = 'png'
PlotResolution = 1000  #Desired dpi of plot


#Factor required to convert diameter data in experimental data file to fundamental unit e.g. if file 
#has diameters listed in terms of micrometers, then the factor needs to be 1e-6 to convert back to meters.
#This is necessary for the section that computes the mass of the particles
DiameterConversionFactor = 1.0e-6  #For experimental dataset
#DiameterConversionFactor = 1.0  #For simulation dataset 

DiameterPlotFactor = 1.0e6 #Factor for scaling the horizontal axis of diameter - for experimental data
#DiameterPlotFactor = 1.0e6 #Factor for scaling the horizontal axis of diameter - for simulation data
#DiameterPlotFactor = 1.0 #Factor for scaling the horizontal axis of diameter - for simulation data with mass weighting debugging - possibly incorrect to use



#No need to change after this line for user

#For making individual figures. Do not edit this value
FigCount = 1


FilePath=FilePathBase + "/"+InputFileName

print("Reading Data From: %s"%(FilePath))
#Open input file
try:
	f = open(FilePath, "r")
except:
	print("Failed to Input File!")


#Loop over all lines in input file and parse
count=0 #Line counter
print("Reading Data File Contents")
DataArrayList = [] #Initialize list
RowCount = 0 #For counting number of data rows in file
for Line in f:

	if(count == 0): #First line with x/D coordinate
		tmp = Line.rstrip() #Remove newline character
		tmp = tmp.split()
		xOverD = float(tmp[-1]) #Extract coordinate(Last element in the split list)
		print("X/D Coordinate is:%f"%(xOverD))

	elif(count == 5): #Line with r/D coordinates
		#Remove all non-numeric characters from the string
		tmp = Line.rstrip()
		tmp = "".join(c for c in tmp if c in '1234567890.' or c in string.whitespace)
		tmp = tmp.split()
		NumRadii = len(tmp)
		rOverD = tmp
		
		print("Number of Radii at which particle PDF is measured: %d"%(NumRadii))
		print("Values of r/D: %s\n"%(rOverD))

	elif(count >8): #This is where the raw pdf data is located in the file

		tmp = Line.rstrip()
		
		#Only perform storage on lines that are not blank in the file
		if(tmp != ''): 

			tmp = tmp.split()
			if(count == 9):
				DataArrayList.append([])
				DataArrayList[RowCount].append(tmp)
				RowCount = RowCount + 1	
			else:
				DataArrayList.append([])
				DataArrayList[RowCount].append(tmp)
				RowCount = RowCount + 1


	count = count + 1

f.close()


#Store number of diameter bins
print("Number of particle diameter bins: %d"%(RowCount))
DiameterBins = RowCount

#Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
DataArrayList=list(itertools.chain.from_iterable(DataArrayList))


#For Debugging purposes - print DataArray
if(DebugFlag == 1):
	for i in range(0,DiameterBins):
		print("%s\n"%(str(DataArrayList[i][:])))

#Now store as a numpy numeric array
DataArray = np.zeros((DiameterBins,NumRadii+1))

for i in range(0,DiameterBins):
	for j in range(0,NumRadii+1):
        	DataArray[i][j] = float(DataArrayList[i][j])

#Data array has the following data
#diameter	R1-pdf	R2-pdf	R3-pdf	...RNumRadii-pdf

######End Data File Parsing###############


if(MassWeightedFlag == 0):
	#Compute number weighted diameter PDF
	HorizontalBins = np.zeros(DiameterBins)
	pdf = np.zeros(DiameterBins)
	for i in range(0,DiameterBins):
		HorizontalBins[i] = DataArray[i][0] #Store diameter bins

		if(RadiusAverageFlag == 1):
			for j in range(0,NumRadii):
				pdf[i] = pdf[i] + DataArray[i][j+1]
		else:
			pdf[i] = DataArray[i][1] #Store first PDF value

else:
	#Compute Mass Weighted PDF
        HorizontalBins = np.zeros(DiameterBins)
        pdf = np.zeros(DiameterBins)
        for i in range(0,DiameterBins):
		#Note that diameters from the experimental data file are given in micrometers, so a conversion is necessary to compute true mass.
                #HorizontalBins[i] = LiquidDensity*(math.pi/6.0)*(DiameterConversionFactor*DataArray[i][0])**3 #Store mass of particles in bin
		HorizontalBins[i] = DataArray[i][0] #Store diameter bins

		if(RadiusAverageFlag == 1):
                        for j in range(0,NumRadii):
                                pdf[i] = pdf[i] + DataArray[i][j+1]
                else:
                        pdf[i] = DataArray[i][1] #Store first PDF value

		#To have a mass weighted PDF we scale the vertical axis to be the mass of the particles in that bin
		pdf[i] = pdf[i] * LiquidDensity*(math.pi/6.0)*(DiameterConversionFactor*DataArray[i][0])**3 #Store mass of particles in bin


	"""
	HorizontalBins = np.zeros(DiameterBins)
        pdf = np.zeros(DiameterBins)
        for i in range(0,DiameterBins):
                #Note that diameters from the experimental data file are given in micrometers, so a conversion is necessary to compute true mass.
                HorizontalBins[i] = LiquidDensity*(math.pi/6.0)*(DataArray[i][0])**3 #Store mass of particles in bin

                if(RadiusAverageFlag == 1):
                        for j in range(0,NumRadii):
                                pdf[i] = pdf[i] + DataArray[i][j+1]
                else:
                        pdf[i] = DataArray[i][1] #Store first PDF value


	"""
	
#Rescaledata by DiameterConversionFactor 
HorizontalBins = HorizontalBins*DiameterConversionFactor

if(DebugFlag == 1):
	#Print the bin values to screen
	for i in range(0,DiameterBins):
		print("%4.2E\n"%(HorizontalBins[i]))



#Integrate data assuming that points are bin heights and widths are variable
C = 0 #Initialize integral to zero
width = np.zeros(DiameterBins)
for i in range(0,DiameterBins):
	if(i == 0):
		width[i] = 0.5*(HorizontalBins[i+1] - HorizontalBins[i])
		C = C + pdf[i]*width[i]
	elif(i==DiameterBins-1):
		width[i] = 0.5*(HorizontalBins[i] - HorizontalBins[i-1])
                C = C + pdf[i]*width[i]
	else:
		width[i] = 0.5*(HorizontalBins[i+1] - HorizontalBins[i]) + 0.5*(HorizontalBins[i] - HorizontalBins[i-1])
                C = C + pdf[i]*width[i]

if(DebugFlag == 1):
	print("Integration of Histogram yields: %10.6E"%(C))


#Now that we have the area under the pdf we can normalize it to 1
pdfNormalized = pdf/C


#For Debugging plot the pdf
if(DebugFlag == 1):
	
	plt.figure(FigCount)
	FigCount = FigCount + 1
	plt.bar(HorizontalBins,pdf,width,color="blue")
	plt.xlabel('Diameter ($\mu$meters)')
	plt.ylabel('Counts')
	plt.draw()

	plt.figure(FigCount)
	FigCount = FigCount + 1
	plt.plot(HorizontalBins,pdfNormalized,color='blue', marker='o')
	plt.xlabel('Diameter ($\mu$meters)')
	plt.ylabel('PDF')
	plt.draw()

	#Plot the CDF of the normalized PDF
	cdf = np.zeros(DiameterBins)
	for i in range(1,DiameterBins):
		cdf[i] = cdf[i-1] + pdfNormalized[i]*width[i]
	plt.figure(FigCount)
	FigCount = FigCount + 1
	plt.plot(HorizontalBins,cdf)
	plt.xlabel(r'$Diameter (\mu meters)$')
	plt.ylabel('CDF')

	plt.show(block=True)



#Generate a spoofed data set for scipy to generate the lognormal fitting parameters from
if(MassWeightedFlag == 0): #Do number weighted
	
	NumSamples = sum(pdf)
	GeneratedData = np.zeros(NumSamples)
	count = 0 #For storing data of samples contiguously
	for i in range(0,DiameterBins):
		for j in range(0,int(pdf[i])):
			GeneratedData[count] = HorizontalBins[i]
			count = count + 1


elif(MassWeightedFlag == 1):
	#Generate a new set of samples based on the mass weighted PDF using the rejection sampling method
	print("Generating samples from the mass weighted distribution")

	N = 100e3 #Number of samples to generate
	M = 1.5 #Parameter used for rejection sampling

	GeneratedData = np.zeros(N)
	g_pdf = pdfNormalized  #Store the g distribution

	#Generate the empirical CDF of the normalized PDF
        g_cdf = np.zeros(DiameterBins)
        for i in range(1,DiameterBins):
                g_cdf[i] = g_cdf[i-1] + g_pdf[i]*width[i]
	
	g_cdf[-1] = 1 #Set the last value to be 1        

	plt.figure(FigCount)
        FigCount = FigCount + 1
        plt.plot(HorizontalBins,g_cdf)
        plt.xlabel(r'$Diameter (\mu meters)$')
        plt.ylabel('CDF')
	plt.show()
	
	count = 0
	while(count < N): #Loop until number of samples have been generated

		#Generate a random number from the uniform distribution between 0 and 1
        	U_rejection = random.uniform(0, 1)
	
		#Use inverse CDF method to sample from the PDF of g
		U = random.uniform(0, 1)
		for i in range(0,len(g_cdf)-1):
			if(i == 0 and U < g_cdf[i]): #Just assume that sample was from the first bin
				d_sample = HorizontalBins[i]
			elif(U >= g_cdf[i] and U <= g_cdf[i+1]):

				#print("Lower Bound: %10.6E\tUpper Bound: %10.6E"%(g_cdf[i],g_cdf[i+1]))

				#Linearly interpolate to obtain the value of the sample
				x_1 = HorizontalBins[i]
				x_2 = HorizontalBins[i+1]
				y_1 = g_cdf[i]
				y_2 = g_cdf[i+1]
				y_3 = U
				x_3 = x_1 +((y_3-y_1)/(y_2-y_1))*(x_2-x_1)
				d_sample = x_3 #Store sample

		#print(d_sample)
		#Evaluate the probability of the original distribution at the newly sampled value
		for i in range(0,len(g_pdf)):
			if(i == 0 and d_sample < (HorizontalBins[i]-0.5*width[i])):
				probability_of_d_sample = 0
			elif( d_sample >=(HorizontalBins[i]-0.5*width[i]) and d_sample <(HorizontalBins[i]+0.5*width[i]) ): #Place sample into this probability range
				probability_of_d_sample = g_pdf[i]
			elif(i == len(g_pdf) and d_sample >= (HorizontalBins[i]-0.5*width[i])):
				probability_of_d_sample = 0


		if(probability_of_d_sample == 0):
			ratio = 0
		else:
			ratio = probability_of_d_sample/(M*probability_of_d_sample)

		#print("Rejection Ratio: %10.6E"%(ratio))
		if(ratio >= U_rejection):
			GeneratedData[count] = d_sample
			count = count + 1
			print("Sample %d is: %10.6E"%(count+1,d_sample))
			



#Compute stats on the raw data set to compare with fit
DataSetMean = np.mean(GeneratedData)
DataSetMedian = np.median(GeneratedData)
DataSetStandardDeviation = np.std(GeneratedData)

#Generate a log-normal fit of the data
shape, loc, scale = stats.lognorm.fit(GeneratedData,floc=0)
Estimated_normal_mu = np.log(scale)
Estimated_normal_sigma = shape
print(scale)
print(loc)

print("Estimated Normal Distribution mu: %10.6E"%(Estimated_normal_mu))
print("Estimated Normal Distribution sigma: %10.6E"%(Estimated_normal_sigma))

#For getting the mean and standard deviation of log-normal distribution - https://en.wikipedia.org/wiki/Log-normal_distribution
Estimated_lognormal_mu = math.exp(Estimated_normal_mu + 0.5*Estimated_normal_sigma**2)
Estimated_lognormal_sigma = Estimated_lognormal_mu*math.sqrt(math.exp(Estimated_normal_sigma**2)-1) 
print("Estimated Log-Normal Distribution mu: %10.6E"%( Estimated_lognormal_mu))
print("Estimated Log-Normal Distribution sigma: %10.6E"%( Estimated_lognormal_sigma ))




Binmin = min(HorizontalBins)
BinMax = max(HorizontalBins)


Spacing = np.linspace(Binmin,BinMax,600) 
logNormalPDF = stats.lognorm.pdf(Spacing,shape,scale=scale)

if(WeibullPlotFlag == 1):
	#Generate a weibull distribution of the data
        p0, p1, p2 = stats.weibull_min.fit(GeneratedData,floc=0)
        print(p0)
        print(p1)
        print(p2)
        print("Estimated Weibull shape factor: %f"%(p0))
        print("Estimated Weibull scale factor: %f"%(p2))
	WeibullPDF   = stats.weibull_min.pdf(Spacing,p0,p1,p2)


#Plot log-normal fit as well as experimental PDF to compare
plt.figure(FigCount)
FigCount = FigCount + 1
plt.plot(Spacing*DiameterPlotFactor,logNormalPDF,color='black',label="Log-Normal PDF Fit") #Log-Normal fit to generated data

plt.bar(HorizontalBins*DiameterPlotFactor,pdfNormalized,width*DiameterPlotFactor, color='blue',fill=False,label="Emprical Data PDF") 
plt.axvline(x=DataSetMean*DiameterPlotFactor)

#plt.plot(HorizontalBins,pdfNormalized, color='blue', marker='o', drawstyle='step',linestyle='-',label="Experimental Data PDF")
if(WeibullPlotFlag == 1):
	plt.plot(Spacing,WeibullPDF,color='green',label="Weibull PDF Fit")

plt.legend(loc='best',fontsize=10)
plt.ylabel("PDF")

DataFitString = "%s %5.2E \n%s %5.2E\n%s %5.2E \n%s %5.2E"%("Estimated Normal mu = ",Estimated_normal_mu,"Estimated Normal sigma = ",Estimated_normal_sigma,"Estimated Log-normal mu = ",Estimated_lognormal_mu,"Estimated Log-normal sigma = ",Estimated_lognormal_sigma)
ax = plt.gca()
plt.text(0.5,0.5,DataFitString,fontsize=10,transform=ax.transAxes) #uses normalized axes coordinates [0,1]

if(MassWeightedFlag == 1):
	plt.xlabel("Diameter ($\mu$meters)")	
else:
	plt.xlabel("Diameter ($\mu$meters)")

plt.draw()
#plt.show(block=True)



#Perform a K-S(Kolmogorov-Smirnoff) Test for the fit to see if it is any good
KS, pValue = stats.ks_2samp(pdfNormalized,logNormalPDF)
print("Value of Kolmogorov Statistic is: %f"%(KS))


#Output data to a file for safe keeping
print("Outputting Data on Experimental Fit\n")
#Create output directory and enter the directory
OutPutDir = FilePathBase +"/DataFit"
if not os.path.exists(OutPutDir):
        os.makedirs(OutPutDir)
        os.chdir(OutPutDir)
else:
        os.chdir(OutPutDir)


outputFileName = OutputFileName + "." + PlotImageFormat
print("Outputting Plot of Data Fits to: %s"%(outputFileName))

plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()



#Go back to the slice data directory
os.chdir("..")





