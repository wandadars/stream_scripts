#! /usr/bin/env python

#### import modules
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats 
import sys
import time
from droplet_histogram_tools import particle_histogram
from utilities import *


if len(sys.argv) <2:
    print 'Error: Must give input file to script'
    sys.exit(1)

input_reader = user_input_parser()

file_name = sys.argv[1]
file_path = os.getcwd()
user_settings = input_reader.parse_user_input_file(file_name,file_path)


#Experimental Data Set
ExpInputFileName = user_settings['ExpInputFileName']
ExpFilePathBase = user_settings['ExpFilePathBase']

ExpDataTag = 'Data Set 1'
if 'ExpDataTag' in user_settings: ExpDataTag = user_settings['ExpDataTag'] 

#Simulation Data Set
SimInputFileName = user_settings['SimInputFileName'] 
SimFilePathBase = user_settings['SimFilePathBase']

SimDataTag = 'Data Set 2'
if 'SimDataTag' in user_settings: SimDataTag = user_settings['SimDataTag'] 


OutputFileName = user_settings['OutputFileName'] 

#Debug flag
DebugFlag = int(user_settings['DebugFlag'])

WeibullPlotFlag = int(user_settings['WeibullPlotFlag'])  #1 to fit data to Weibull distribution and show on plots, 0 to leave out

#Flag for averaging the PDF over all radii
RadiusAverageFlag = int(user_settings['RadiusAverageFlag'])	# 0 - only take first value, 1 - average over all radial PDFs in data file

#Provide the density of the liquid for converting number weighted droplet diameter PDFs to mass weighted droplet mass PDF.
MassWeightedFlag = int(user_settings['MassWeightedFlag'])	# 0 for using the original diameter data, 1 for converting to mass weighted PDF


#Output options
PlotImageFormat = user_settings['PlotImageFormat'] 
PlotResolution = float(user_settings['PlotResolution'])  #Desired dpi of plot


#Factor required to convert diameter data in experimental data file to fundamental unit e.g. if file 
#has diameters listed in terms of micrometers, then the factor needs to be 1e-6 to convert back to meters.
#This is necessary for the section that computes the mass of the particles
ExpDiameterConversionFactor = float(user_settings['ExpDiameterConversionFactor'])   #For experimental dataset
SimDiameterConversionFactor = float(user_settings['SimDiameterConversionFactor'])  #For simulation dataset 

ExpDiameterPlotFactor = float(user_settings['ExpDiameterPlotFactor']) #Factor for scaling the horizontal axis of diameter - for experimental data
SimDiameterPlotFactor = float(user_settings['SimDiameterPlotFactor']) #Factor for scaling the horizontal axis of diameter - for simulation data



FigCount = 1

ExpFilePath=ExpFilePathBase + "/"+ExpInputFileName
SimFilePath=SimFilePathBase + "/"+SimInputFileName

experimental_data = particle_histogram()
experimental_data.read_data(ExpFilePath)

simulation_data = particle_histogram()
simulation_data.read_data(SimFilePath)

#Rescaledata by DiameterConversionFactor 
experimental_data.rescale_bin_values(ExpDiameterConversionFactor)
simulation_data.rescale_bin_values(SimDiameterConversionFactor)


if(DebugFlag == 1):
    #Print the bin values to screen
    tmpData = experimental_data.get_horizontal_bins()
    for i in range( 0,experimental_data.get_num_bins() ):
            print("%4.2E\n"%(tmpData[i]))

    tmpData = simulation_data.get_horizontal_bins()
    for i in range(0,simulation_data.get_num_bins()):
           print("%4.2E\n"%(tmpData[i]))



if(MassWeightedFlag == 1):
    experimental_data.compute_volume_weighted_pdf(overwrite_pdfs=True)
    simulation_data.compute_volume_weighted_pdf(overwrite_pdfs=True)

#Normalize the histogram to bring it into line with approximating a PDF
experimental_data.normalize_pdf()
simulation_data.normalize_pdf()

#Plot pdf to see how it looks
#experimental_data.plot_histogram()
#simulation_data.plot_histogram()


"""
#Generate a spoofed data set for scipy to generate the lognormal fitting parameters from
print("For Experimental Data Set")
GeneratedExpData = experimental_data.sample_from_pdf(1e6,1.5)

#Compute stats on the raw data set to compare with fit
DataSetMean = np.mean(GeneratedExpData)
DataSetMedian = np.median(GeneratedExpData)
DataSetStandardDeviation = np.std(GeneratedExpData)

print("Mean of Generated data:%10.6E"%(DataSetMean))
print("Median of Generated data:%10.6E"%(DataSetMedian))
print("Standard Deviation of Generated data:%10.6E"%(DataSetStandardDeviation))

#Generate a log-normal fit of the data
exp_shape, loc, exp_scale = stats.lognorm.fit(GeneratedExpData,floc=0)
Estimated_normal_mu = np.log(exp_scale)
Estimated_normal_sigma = exp_shape
print(exp_scale)
print(loc)

print("Estimated Normal Distribution mu: %10.6E"%(Estimated_normal_mu))
print("Estimated Normal Distribution sigma: %10.6E"%(Estimated_normal_sigma))

#For getting the mean and standard deviation of log-normal distribution - https://en.wikipedia.org/wiki/Log-normal_distribution
Estimated_lognormal_mu = math.exp(Estimated_normal_mu + 0.5*Estimated_normal_sigma**2)
Estimated_lognormal_sigma = Estimated_lognormal_mu*math.sqrt(math.exp(Estimated_normal_sigma**2)-1) 
print("Estimated Log-Normal Distribution mu: %10.6E"%( Estimated_lognormal_mu))
print("Estimated Log-Normal Distribution sigma: %10.6E"%( Estimated_lognormal_sigma ))


#Generate a spoofed data set for scipy to generate the lognormal fitting parameters from
print("For Simulation Data Set")
GeneratedSimData = simulation_data.sample_from_pdf(1e6,1.5)

#Compute stats on the raw data set to compare with fit
DataSetMean = np.mean(GeneratedSimiData)
DataSetMedian = np.median(GeneratedSimData)
DataSetStandardDeviation = np.std(GeneratedSimData)

print("Mean of Generated data:%10.6E"%(DataSetMean))
print("Median of Generated data:%10.6E"%(DataSetMedian))
print("Standard Deviation of Generated data:%10.6E"%(DataSetStandardDeviation))

#Generate a log-normal fit of the data
sim_shape, loc, sim_scale = stats.lognorm.fit(GeneratedSimData,floc=0)
Estimated_normal_mu = np.log(sim_scale)
Estimated_normal_sigma = sim_shape
print(sim_scale)
print(loc)

print("Estimated Normal Distribution mu: %10.6E"%(Estimated_normal_mu))
print("Estimated Normal Distribution sigma: %10.6E"%(Estimated_normal_sigma))

#For getting the mean and standard deviation of log-normal distribution - https://en.wikipedia.org/wiki/Log-normal_distribution
Estimated_lognormal_mu = math.exp(Estimated_normal_mu + 0.5*Estimated_normal_sigma**2)
Estimated_lognormal_sigma = Estimated_lognormal_mu*math.sqrt(math.exp(Estimated_normal_sigma**2)-1) 
print("Estimated Log-Normal Distribution mu: %10.6E"%( Estimated_lognormal_mu))
print("Estimated Log-Normal Distribution sigma: %10.6E"%( Estimated_lognormal_sigma ))
"""


#Take the value from the dataset and store it into generally named variable to make rest of code generic and resuable
ExpHorizontalBins = np.asarray(experimental_data.get_horizontal_bins())
SimHorizontalBins = np.asarray(simulation_data.get_horizontal_bins())

print ExpHorizontalBins
print SimHorizontalBins

Exppdf = np.asarray(experimental_data.get_pdf())
Expwidth = np.asarray(experimental_data.get_widths())

Simpdf = np.asarray(simulation_data.get_pdf())
Simwidth = np.asarray(simulation_data.get_widths())


ExpBinmin = min(ExpHorizontalBins)
ExpBinMax = max(ExpHorizontalBins)

SimBinmin = min(SimHorizontalBins)
SimBinMax = max(SimHorizontalBins)

ExpSpacing = np.linspace(ExpBinmin,ExpBinMax,600) 
SimSpacing = np.linspace(SimBinmin,SimBinMax,600) 

#ExplogNormalPDF = stats.lognorm.pdf(ExpSpacing,exp_shape,scale=exp_scale)
#SimlogNormalPDF = stats.lognorm.pdf(SimSpacing,sim_shape,scale=sim_scale)


plt.figure(FigCount)
FigCount = FigCount + 1

plt.subplot(2,2,1)
plt.bar(ExpHorizontalBins*ExpDiameterPlotFactor,Exppdf,Expwidth*ExpDiameterPlotFactor, color='blue',fill=True,label="Emprical Data PDF") 
plt.ylim([0,max(max(Exppdf),max(Simpdf))])
plt.xlim([0,max(max(ExpHorizontalBins*ExpDiameterPlotFactor),max(SimHorizontalBins*SimDiameterPlotFactor))])
plt.legend(loc='best',fontsize=7)
plt.ylabel("PDF")

plt.subplot(2,2,2)
plt.bar(SimHorizontalBins*SimDiameterPlotFactor,Simpdf,Simwidth*SimDiameterPlotFactor, color='red',fill=True,label="Simulation Data PDF") 
plt.ylim([0,max(max(Exppdf),max(Simpdf))])
plt.xlim([0,max(max(ExpHorizontalBins*ExpDiameterPlotFactor),max(SimHorizontalBins*SimDiameterPlotFactor))])
plt.legend(loc='best',fontsize=7)
plt.ylabel("PDF")

plt.subplot(2,2,3)
plt.bar(SimHorizontalBins*SimDiameterPlotFactor,Simpdf,Simwidth*SimDiameterPlotFactor, color='red',fill=True,label="Simulation Data PDF") 
plt.ylim([0,max(max(Exppdf),max(Simpdf))])
plt.xlim([0,max(max(ExpHorizontalBins*ExpDiameterPlotFactor),max(SimHorizontalBins*SimDiameterPlotFactor))])
plt.legend(loc='best',fontsize=7)
plt.ylabel("PDF")

plt.xlabel("Diameter ($\mu$meters)")	

plt.draw()

outputFileName = OutputFileName + "." + PlotImageFormat
print("Outputting Plot of Data Fits to: %s"%(outputFileName))
plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()

"""
#Perform a K-S(Kolmogorov-Smirnoff) Test for the fit to see if it is any good
KS, pValue = stats.ks_2samp(ExplogNormalPDF,SimlogNormalPDF)
print("Value of Kolmogorov Statistic is: %f"%(exp_KS))
"""


#Compare the PDFs of the two distributions to each other
plt.figure(FigCount)
FigCount = FigCount + 1

plt.bar(ExpHorizontalBins*ExpDiameterPlotFactor,Exppdf,Expwidth*ExpDiameterPlotFactor, color='black',fill=False,label="Emprical Data PDF")
plt.step(SimHorizontalBins*SimDiameterPlotFactor,Simpdf, color='red',label="Simulation Data PDF") 
plt.ylim([0,max(max(Exppdf),max(Simpdf))])
plt.xlim([0,max(max(ExpHorizontalBins*ExpDiameterPlotFactor),max(SimHorizontalBins*SimDiameterPlotFactor))])
plt.legend(loc='best',fontsize=7)
plt.ylabel("PDF")
plt.xlabel("Diameter ($\mu$meters)")
plt.draw()

outputFileName = OutputFileName + "_pdf_overlay"+"." + PlotImageFormat
print("Outputting Plot of Data Fits to: %s"%(outputFileName))
plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()




#Plot log-normal fit as well as experimental PDF to compare
plt.figure(FigCount)
FigCount = FigCount + 1

experimental_data.compute_cdf()
simulation_data.compute_cdf()

Expcdf = np.asarray(experimental_data.get_cdf())
Expwidth = np.asarray(experimental_data.get_widths())

Simcdf = np.asarray(simulation_data.get_cdf())
Simwidth = np.asarray(simulation_data.get_widths())

plt.step(ExpHorizontalBins*ExpDiameterPlotFactor,Expcdf, color='blue',label="Emprical Data CDF") 
plt.step(SimHorizontalBins*SimDiameterPlotFactor,Simcdf, color='red',label="Simulation Data CDF") 

plt.ylim([0,1])
plt.legend(loc='best',fontsize=10)
plt.ylabel("CDF")

plt.xlabel("Diameter ($\mu$meters)")	
plt.draw()


outputFileName = OutputFileName +"_CDF_compare"+ "." + PlotImageFormat
print("Outputting Plot of Data Fits to: %s"%(outputFileName))
plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')










#Go back to the slice data directory
os.chdir("..")





