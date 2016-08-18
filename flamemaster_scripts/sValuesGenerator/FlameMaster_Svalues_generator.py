#! /usr/bin/env python

# Purpose:      Takes user defined input for min, max, and stepsize of the Scalar Dissipation
#		Rate & generates an output file for copying into the FlameMaster input file.
#
# Input:        None.
#
# Output:       A S_Values.txt file for use in FlameMaster input file.
#
#
#       Authors: Christopher Neal
#       Date   : 03/18/2016
#       Updated: 03/18/2016
#
########################################################################

import numpy as np


OutputFileName = 'S_Values.txt'
OutputString = 'Scalar DissipationRate = '

S_Min = 2e5
S_Max = 1e6
DeltaS = 33e3


#Testcase for perfect match
#S_Min = 2e5
#S_Max = 3e5
#DeltaS = 1e4

##WRITE DATA TO OUTPUT FILE

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")



#Determine the number of entries that will be printed(including the provided bounds)
NumEntries = 1
done = False
SValue = S_Min
while(done == False):

	SValue = SValue + DeltaS

	if(SValue >= S_Max):
		done = True

	NumEntries = NumEntries + 1

print("%d entries will be printed to the output file"%(NumEntries))


StartValue = S_Min
FinalValue = S_Max
IncValue = DeltaS
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




