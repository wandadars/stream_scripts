#! /usr/bin/env python

# Purpose:      Takes user defined input for min, max, and stepsize of the Scalar Dissipation
#		Rate & generates an output file for copying into the FlameMaster input file.
#
# Input:        s_min, s_max, delta_s
#
# Output:       A S_Values.txt file for use in FlameMaster input file.
#
#
#       Authors: Christopher Neal
#       Date   : 03/18/2016
#       Updated: 12/14/2016
#
########################################################################

import numpy as np
import argparse

OutputFileName = 'S_Values.txt'
OutputString = 'Scalar DissipationRate = '

parser = argparse.ArgumentParser()
parser.add_argument("s_min", help="Minimum value of scalar dissipation rate for range")
parser.add_argument("s_max", help="Maximum value of scalar dissipation rate for range")
parser.add_argument("num_s", help="Number of points to add between the minimum and maximum ranges")
args = parser.parse_args()

print "Provided value of s_min: ",args.s_min
print "Provided value of s_max: ",args.s_max
print "Provided value of num_s: ",args.num_s

s_min = float(args.s_min)
s_max = float(args.s_max)
num_s = float(args.num_s)


##WRITE DATA TO OUTPUT FILE

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")



#Determine the number of entries that will be printed(including the provided bounds)
NumEntries = 1
done = False
SValue = s_min
delta_s = (s_max - s_min)/(num_s + 1)
while(done == False):

	SValue = SValue + delta_s

	if(SValue >= s_max):
		done = True

	NumEntries = NumEntries + 1

print("%d entries will be printed to the output file"%(NumEntries))


StartValue = s_min
FinalValue = s_max
IncValue = delta_s
FlipFlag = False

print("Starting Value is %10.6E"%StartValue)
print("Ending Value is %10.6E"%FinalValue)

if(FinalValue <= StartValue): #Flip ordering so that we can use the same algorithm
	tempData = StartValue
	StartValue = FinalValue
	FinalValue = tempData
	FlipFlag = True

VariationArray = np.zeros(1)
VariationArray[0] = StartValue
Done=False
count = 0
while(Done == False):
	
	if(VariationArray[count] + IncValue < FinalValue):
		VariationArray = np.append(VariationArray,VariationArray[count] + IncValue)
		count = count+1
	else:
		VariationArray = np.append(VariationArray,FinalValue)
		count = count + 2 #has to be 2 because we actually started with an initial element at the beginning
		Done = True


if(FlipFlag == True):
	VariationArray = np.flipud(VariationArray)		

#WRITE DATA TO OUTPUT FILE
for j in range(0,NumEntries):

	OutputStringTemp = "%s %10.6e"%(OutputString,VariationArray[j])
	OutputStringTemp = OutputStringTemp.replace("+", "")
	OutputFile.write("%s\n"%OutputStringTemp)




