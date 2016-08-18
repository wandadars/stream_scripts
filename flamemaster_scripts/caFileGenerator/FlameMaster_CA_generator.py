#! /usr/bin/env python

# Purpose:      Reads in a user created input file for varying flamelet conditions and outputs a
#		CA.in file for use in FlameMaster. 
#               Paraview.
#
# Description:  RocFlu post can output Ensight files, however the case file and filenames of 
#               the post output files are in an incorrect format for Paraview to open all the 
#               output files at once. The program rectifies this by doing two important steps. 
#               
#
# Input:        None.
#
# Output:       A Ca.in file for use in FlameMaster.
#
#
#       Authors: Christopher Neal
#       Date   : 03/08/2016
#       Updated: 03/08/2016
#
########################################################################

import numpy as np


OutputFileName = 'CA.in'



ConstantZR = 1 #Value of ZR in the last column of the CA.in file that never changes

#Read user input file
try:
        InputFile = open("FlameMaster_CA_inputs.dat", "r")
except:
        print("Cannot find the FlameMaster_CA_inputs.dat Input File!")


####Parse input file contents######
count = 0 #File line counter to identify data location
for Line in InputFile:

	tmp = Line.rstrip() #remove newline character
        tmp = tmp.split()
	if(count == 0):
		#Store initial conditions
		Init_Pressure = tmp[0]
		Init_Ox_Temp = tmp[1]
		Init_Fuel_Temp = tmp[2]
		Init_Chi = tmp[3]  #Initial scalar dissipation rate
		
	elif(count == 1):
		Time_Delta = tmp[0]
	elif(count == 2):
		Final_Pressure = tmp[0]
	elif(count == 3):
		Pressure_Delta = tmp[0]
	elif(count==4):
		Final_Ox_Temp = tmp[0]
	elif(count == 5):
		Ox_Temp_Delta = tmp[0]
	elif(count==6):
		Final_Fuel_Temp = tmp[0]
	elif(count == 7):
		Fuel_Temp_Delta = tmp[0]
	elif(count==8):
		Final_Chi = tmp[0]
	elif(count == 9):
		Chi_Delta = tmp[0]


	count = count + 1
############################

DataArray_List = []
DataArray_List.append([])
DataArray_List.append([])
DataArray_List.append([])
DataArray_List.append([])

for i in range(0,4):
	
	if(i == 0): #Store pressure info
		DataArray_List[i].append(Init_Pressure)
		DataArray_List[i].append(Final_Pressure)
		DataArray_List[i].append(Pressure_Delta)

	if(i == 1): #Store Oxidizer info
                DataArray_List[i].append(Init_Ox_Temp)
                DataArray_List[i].append(Final_Ox_Temp) 
		DataArray_List[i].append(Ox_Temp_Delta)

	if(i == 2): #Store Fuel info
                DataArray_List[i].append(Init_Fuel_Temp)
                DataArray_List[i].append(Final_Fuel_Temp)
                DataArray_List[i].append(Fuel_Temp_Delta)
	
	if(i == 3): #Store Scalar dissipation(chi) info
                DataArray_List[i].append(Init_Chi)
                DataArray_List[i].append(Final_Chi)
                DataArray_List[i].append(Chi_Delta)


#Use VaryVariable to decide which variables need to changed 
VaryVariable = []
for i in range(0,4):
	VaryVariable.append(0)	#0 is true, 1 is false

for i in range(0,4):
	if(DataArray_List[i][2] == '0'):
		VaryVariable[i] = 1


##WRITE PREABLE TO OUTPUT FILE
OutputFileName = 'CA.in'

#Open output file
try:
        OutputFile = open(OutputFileName, "w+")
except:
        print("Cannot open output file!")

OutputFile.write("RPM = -1\n")
OutputFile.write("VarsIn = 6\n")
OutputFile.write("Time(s)\t\tPressure(Pa)\tTOx(K)\t\tTFuel(K)\tSci(1/s)\tZR\t\n")
OutputFile.write("%10.6E\t"%(0.0))
for i in range(0,4):
	StartValue = float(DataArray_List[i][0])
	OutputFile.write("%10.6E\t"%(StartValue))

OutputFile.write("%d\n"%ConstantZR)


Time = float(Time_Delta) #Initialize output time
#GENERATE VARIATION ARRAYS
for i in range(0,4):

	if(VaryVariable[i] == 0): #Only do ones that need to be varied
		
		StartValue = float(DataArray_List[i][0])
		FinalValue = float(DataArray_List[i][1])
		IncValue = float(DataArray_List[i][2])
		FlipFlag = False

		print("Starting Value is %f"%StartValue)
		print("Ending Value is %f"%FinalValue)

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
	
			if(VariationArray[count] + IncValue <= FinalValue):
				VariationArray = np.append(VariationArray,VariationArray[count] + IncValue)
				count = count+1
			else:
				VariationArray = np.append(VariationArray,FinalValue)
				count = count + 2 #has to be 2 because we actually started with an initial element at the beginning
				Done = True


		if(FlipFlag == True):
			VariationArray = np.flipud(VariationArray)		

		print(VariationArray)
		print(count)
		#WRITE DATA TO OUTPUT FILE
		for j in range(1,count):

			OutputFile.write("%10.6E\t"%Time)
			for k in range(0,4):
				if(k == i):
					OutputFile.write("%10.6E\t"%VariationArray[j])
				elif(k < i):
					OutputFile.write("%10.6E\t"%float(DataArray_List[k][1]))
				else:
					OutputFile.write("%10.6E\t"%float(DataArray_List[k][0]))

			Time = Time + float(Time_Delta)
			OutputFile.write("%d\n"%ConstantZR)






