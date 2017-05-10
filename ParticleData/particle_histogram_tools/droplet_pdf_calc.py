#! /usr/bin/env python
#######################################################################################
# The purpose of this script is to read in a data file containing probability density
# function data for particle diameter distributions away from a spray jet and plot
# the data.
#
# Author: Christopher Neal
#
# Date: 02-15-2016
# Updated: 05-19-2016
#
#######################################################################################


#### import modules
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats,special
import time
import os
from droplet_histogram_tools import particle_histogram

#Specify the path to the Data file that contains the formatted slice data

#"""
#Experimental Data Set
InputFileName="AcF3_xD10_DropDis.dat"
FilePathBase = "/Users/chris1/Dropbox/Streamine_Numerics/Stream_VV_Cases/Fall_2015_Cases/Droplet_Vaporization/SprayJetData_Masri/Acetone_Flames/Acetone reacting/Experiment A/Acetone_Flames/AcF3/xD_10/Droplet_Distribution"
OutputFileName = "AcF3_xD10_DropDis_MassWeightedLog_WeibullFit" #User changes this
#OutputFileName = "SP2_xD0.3_DropDis_NumberedWeightedLogFit" #User changes this
#"""


"""
#Simulation Data set
InputFileName="acetone_PDF_XOverD_10.00_Data.txt"
FilePathBase = "/Users/chris1/Dropbox/Streamine_Numerics/Stream_VV_Cases/Fall_2015_Cases/Droplet_Vaporization/data_analysis_scripts/SP2_SprayJetWithBreakup_LPT_Smoothing_Comparison/particle_PDF_data_noSmoothing/"
#FilePathBase = "/Users/chris1/Dropbox/Streamine_Numerics/Stream_VV_Cases/Fall_2015_Cases/Droplet_Vaporization/data_analysis_scripts/SP2_SprayJetWithBreakup_LPT_Smoothing_Comparison/particle_PDF_data_Smoothing"
#OutputFileName = "acetone_PDF_XOverD__0.30_Data_MassWeightedLogFit" #User changes this
OutputFileName = "acetone_PDF_XOverD_10_Data_NumberedWeightedLogFit" #User changes this
"""


#Debug flag
DebugFlag = 0	#0 for off, 1 for on
WeibullPlotFlag = 1  #1 to fit data to Weibull distribution and show on plots, 0 to leave out
#Flag for averaging the PDF over all radii
RadiusAverageFlag = 1	# 0 - only take first value, 1 - average over all radial PDFs in data file
#Provide the density of the liquid for converting number weighted droplet diameter PDFs to mass weighted droplet mass PDF.
MassWeightedFlag = 1	# 0 for using the original diameter data, 1 for converting to mass weighted PDF

#Output options
PlotImageFormat = 'png'
PlotResolution = 500  #Desired dpi of plot


#Factor required to convert diameter data in experimental data file to fundamental unit e.g. if file 
#has diameters listed in terms of micrometers, then the factor needs to be 1e-6 to convert back to meters.
#This is necessary for the section that computes the mass of the particles
DiameterConversionFactor = 1.0e-6  #For experimental dataset
#DiameterConversionFactor = 1.0  #For simulation dataset 

DiameterPlotFactor = 1.0e6 #Factor for scaling the horizontal axis of diameter - for experimental data
#DiameterPlotFactor = 1.0e6 #Factor for scaling the horizontal axis of diameter - for simulation data
#DiameterPlotFactor = 1.0 #Factor for scaling the horizontal axis of diameter - for simulation data with mass weighting debugging - possibly incorrect to use


#No need to change after this line for user

FigCount = 1

FilePath=FilePathBase + "/"+InputFileName

experimental_data = particle_histogram()
experimental_data.read_data(FilePath)

#Rescaledata by DiameterConversionFactor 
experimental_data.rescale_bin_values(DiameterConversionFactor)


if(DebugFlag == 1):
	#Print the bin values to screen
	tmpData = experimental_data.get_horizontal_bins()
	for i in range(0,experimental_data.get_num_bins()):
		print("%4.2E\n"%(tmpData[i]))


if(MassWeightedFlag == 1):
	experimental_data.compute_volume_weighted_pdf(overwrite_pdfs=True)

#Normalize the histogram to bring it into line with approximating a PDF
experimental_data.normalize_pdf()

#Plot pdf to see how it looks
experimental_data.plot_histogram()

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
GeneratedData = experimental_data.sample_from_pdf(1e6,1.5)

#Compute stats on the raw data set to compare with fit
DataSetMean = np.mean(GeneratedData)
DataSetMedian = np.median(GeneratedData)
DataSetStandardDeviation = np.std(GeneratedData)

print("Mean of Generated data:%10.6E"%(DataSetMean))
print("Median of Generated data:%10.6E"%(DataSetMedian))
print("Standard Deviation of Generated data:%10.6E"%(DataSetStandardDeviation))


#Generate a log-normal fit of the data
shape, loc, scale = stats.lognorm.fit(GeneratedData,floc=0)
Estimated_normal_mu = np.log(scale)
Estimated_normal_sigma = shape
print("Log-Normal Scale factor: ",scale)
print("Log-Normal Fit Location Parameter: ",loc)

print("Estimated Normal Distribution mu: %10.6E"%(Estimated_normal_mu))
print("Estimated Normal Distribution sigma: %10.6E"%(Estimated_normal_sigma))

#For getting the mean and standard deviation of log-normal distribution - https://en.wikipedia.org/wiki/Log-normal_distribution
Estimated_lognormal_mu = math.exp(Estimated_normal_mu + 0.5*Estimated_normal_sigma**2)
Estimated_lognormal_sigma = Estimated_lognormal_mu*math.sqrt(math.exp(Estimated_normal_sigma**2)-1) 
print("Estimated Log-Normal Distribution mu: %10.6E"%( Estimated_lognormal_mu))
print("Estimated Log-Normal Distribution sigma: %10.6E"%( Estimated_lognormal_sigma ))


#Take the value from the dataset and store it into generally named variable to make rest of code generic and resuable
HorizontalBins = np.asarray(experimental_data.get_horizontal_bins())
pdf = np.asarray(experimental_data.get_pdf())
width = np.asarray(experimental_data.get_widths())


Binmin = min(HorizontalBins)
BinMax = max(HorizontalBins)


Spacing = np.linspace(Binmin,BinMax,600) 
logNormalPDF = stats.lognorm.pdf(Spacing,shape,scale=scale)

if(WeibullPlotFlag == 1):
	#Generate a weibull distribution of the data
        p0, p1, p2 = stats.weibull_min.fit(GeneratedData,floc=0)
	#p0 = k = Shape, p1=loc=location, p2=lambda=scale
        print(p0)
        print(p1)
        print(p2)
        print("Estimated Weibull shape factor: %f"%(p0))
        print("Estimated Weibull scale factor: %f"%(p2))

	estimated_weibull_mu = p2*special.gamma(1 + 1.0/p0)
	estimated_weibull_sigma = math.sqrt( p2**(2)*(special.gamma(1 + 2.0/p0) - special.gamma(1 + 1.0/p0)**2))
        print("Estimated Weibull Distribution mu: %f"%(estimated_weibull_mu))
        print("Estimated Weibull Distribution sigma: %f"%(estimated_weibull_sigma))
	WeibullPDF   = stats.weibull_min.pdf(Spacing,p0,p1,p2)


#Plot log-normal fit as well as experimental PDF to compare
plt.figure(FigCount)
FigCount = FigCount + 1
plt.plot(Spacing*DiameterPlotFactor,logNormalPDF,color='black',label="Log-Normal PDF Fit") #Log-Normal fit to generated data

plt.bar(HorizontalBins*DiameterPlotFactor,pdf,width*DiameterPlotFactor, color='blue',fill=False,label="Emprical Data PDF") 
plt.axvline(x=DataSetMean*DiameterPlotFactor)

#plt.plot(HorizontalBins,pdfNormalized, color='blue', marker='o', drawstyle='step',linestyle='-',label="Experimental Data PDF")
if(WeibullPlotFlag == 1):
    plt.plot(Spacing*DiameterPlotFactor,WeibullPDF,color='green',label="Weibull PDF Fit")

plt.legend(loc='best',fontsize=10)
plt.ylabel("PDF")

DataFitStringFormat = "%s %5.2E \n%s %5.2E\n%s %5.2E \n%s %5.2E"
DataFitString = DataFitStringFormat%("Estimated Normal mu = ",Estimated_normal_mu,"Estimated Normal sigma = ",Estimated_normal_sigma,"Estimated Log-normal mu = ",Estimated_lognormal_mu,"Estimated Log-normal sigma = ",Estimated_lognormal_sigma)

if(WeibullPlotFlag == 1):
    DataFitStringFormat = "%s %5.2E \n%s %5.2E\n%s %5.2E \n%s %5.2E \n%s %5.2E \n%s %5.2E"
    DataFitString = DataFitStringFormat%("Estimated Normal mu = ",Estimated_normal_mu,"Estimated Normal sigma = ",Estimated_normal_sigma,"Estimated Log-normal mu = ",Estimated_lognormal_mu,"Estimated Log-normal sigma = ",Estimated_lognormal_sigma,"Estimated Weibull mu = ",estimated_weibull_mu,"Estimated Weibull sigma = ",estimated_weibull_sigma)

ax = plt.gca()
plt.text(0.5,0.6,DataFitString,fontsize=10,transform=ax.transAxes) #uses normalized axes coordinates [0,1]

if(MassWeightedFlag == 1):
	plt.xlabel("Diameter ($\mu$meters)")	
else:
	plt.xlabel("Diameter ($\mu$meters)")

plt.draw()
if(WeibullPlotFlag == 1):
    plt.ylim([0,max(max(pdf),max(logNormalPDF),max(WeibullPDF))])
else:
    plt.ylim([0,max(max(pdf),max(logNormalPDF))])

#plt.show(block=True)


#Perform a K-S(Kolmogorov-Smirnoff) Test for the fit to see if it is any good
KS, pValue = stats.ks_2samp(pdf,logNormalPDF)
print("Value of Kolmogorov Statistic for Log-Normal PDF is: %f"%(KS))

if WeibullPlotFlag == 1:
    KS, pValue = stats.ks_2samp(pdf,WeibullPDF)
    print("Value of Kolmogorov Statistic for Weibull PDF is: %f"%(KS))


#Output data to a file for safe keeping
print("Outputting Information about Data Fit\n")
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





