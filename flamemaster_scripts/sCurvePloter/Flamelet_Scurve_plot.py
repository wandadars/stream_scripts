#! /usr/bin/env python

# Purpose:      Reads in a user created S-Curve data file with the contents generated from
#		the FlameMaster 'ListTool' utility, and plots the first column of data
#		against the second column.
#
# Input:        None.
#
# Output:       A S-Curve.png plot.
#
#
#       Authors: Christopher Neal
#       Date   : 03/28/2016
#       Updated: 03/28/2016
#
########################################################################

import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import time
from operator import itemgetter
from Tkinter import Tk
from tkFileDialog import askopenfilename


OutputFileName = 'S-Curve'
PlotImageFormat = 'png'
PlotResolution = 500

#Variable for plotting
FigCount = 1

#Ask user for input data file containing the TMax and chi_st data in column format
print("Navigate to data file containing scalar dissipation rate and max temperature data.")
Tk().withdraw()
InputFilePath=askopenfilename()


#Read user input file
try:
        InputFile = open(InputFilePath, "r")
	print("Reading Data from file:%s"%(InputFilePath))
except:
        print("Cannot find the specified input file.")


####Parse input file contents######
Linecount = 0 #File line counter to identify data location
DataCount = 0
FileData = []
for Line in InputFile:

	tmp = Line.rstrip() #remove newline character
        tmp = tmp.split()
	if(Linecount == 1): #First line of data file contains column information tags

		#Store column labels
		NumColumns = len(tmp)
		print("%d Unique column labels detected in file"%(NumColumns))
		ColumnLabels = []
		for i in range(0,NumColumns):
			ColumnLabels.append(tmp[i])

		#print("Column label data is: \n%s"%(ColumnLabels))
		
	elif(Linecount >1):
		FileData.append([])
		for i in range(0,NumColumns):
			FileData[DataCount].append(tmp[i])

		DataCount = DataCount + 1


	Linecount = Linecount + 1
NumRows = DataCount
############################


#Sort the 2D list based on ascending values of chi_st
FileData.sort(key=itemgetter(1),reverse=True)

#Convert list data that is in string format to floating point data
chi_st = np.zeros(NumRows)
TMax = np.zeros(NumRows)
for i in range(0,NumRows):
	chi_st[i] = float(FileData[i][0])
	TMax[i] = float(FileData[i][1])

#Plot the S curve on a set of normal axes
plt.figure(FigCount)
FigCount = FigCount + 1
plt.plot(chi_st,TMax,color='black',marker='o',linestyle='none',label="S-Curve Data")
plt.legend(loc='best',fontsize=10)
plt.ylabel("TMax (Kelvin)")
plt.xlabel("Stoichiometric Scalar Dissipation Rate $\chi_{st}$")

DataFitString = "%s %5.2E\n %s %5.2E"%("Lowest Temperature= ",np.amin(TMax),"Max Scalar Dissipation",np.amax(chi_st))
ax = plt.gca()
plt.text(0.6,0.3,DataFitString,fontsize=10,transform=ax.transAxes) #uses normalized axes coordinates [0,1]

#plt.draw()
plt.show()


outputFileName = OutputFileName + "." + PlotImageFormat

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")

print("Outputting Plot of Data Fits to: %s"%(outputFileName))

plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()




#Plot the S curve using a horizontal Log axis and a linear y axis(standard)
plt.figure(FigCount)
FigCount = FigCount + 1
plt.plot(chi_st,TMax,color='black',marker='o',linestyle='none',label="S-Curve Data")
plt.legend(loc='best',fontsize=10)
plt.ylabel("TMax (Kelvin)")
plt.xlabel("Stoichiometric Scalar Dissipation Rate $\chi_{st}$")

DataFitString = "%s %5.2E\n %s %5.2E"%("Lowest Temperature= ",np.amin(TMax),"Max Scalar Dissipation",np.amax(chi_st))
ax = plt.gca()
plt.text(0.6,0.3,DataFitString,fontsize=10,transform=ax.transAxes) #uses normalized axes coordinates [0,1]

#Change horizontal axis to log-scale
ax.set_xscale('log')


#plt.draw()
plt.show()


outputFileName = OutputFileName +"_log"+ "." + PlotImageFormat

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")

print("Outputting Plot of Data Fits to: %s"%(outputFileName))

plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()



#Plot the S curve, but have the plot zoomed in on the middle brance of the S-curve.

#Fist we need to locate the position of the middle branch
for i in reversed(xrange(NumRows)):
	if (i == NumRows-1):
		MaxChi = chi_st[i]
	elif( chi_st[i] >=MaxChi):
		MaxChi = chi_st[i]
	else:
		break

print("Chi at Middle branch is %10.6E"%MaxChi)

#Increase MaxChi value for plotting purposes
MaxChi = 1.05*MaxChi

plt.figure(FigCount)
FigCount = FigCount + 1
plt.plot(chi_st,TMax,color='black',marker='o',linestyle='none',label="S-Curve Data")
plt.xlim([np.amin(chi_st),MaxChi])
plt.legend(loc='best',fontsize=10)
plt.ylabel("TMax (Kelvin)")
plt.xlabel("Stoichiometric Scalar Dissipation Rate $\chi_{st}$")

DataFitString = "%s %5.2E\n %s %5.2E"%("Lowest Temperature= ",np.amin(TMax),"Max Scalar Dissipation",np.amax(chi_st))
ax = plt.gca()
plt.text(0.5,0.5,DataFitString,fontsize=10,transform=ax.transAxes) #uses normalized axes coordinates [0,1]

#Change horizontal axis to log-scale
#ax.set_xscale('log')


#plt.draw()
plt.show()


outputFileName = OutputFileName +"_middleBranch"+ "." + PlotImageFormat

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")

print("Outputting Plot of Data Fits to: %s"%(outputFileName))

plt.savefig(outputFileName, format=PlotImageFormat, dpi=PlotResolution, bbox_inches='tight')
plt.close()






