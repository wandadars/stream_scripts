#######################################################################################
# The purpose of this module is to read the particle data that is stored in HDF5 format
# and return an array to the calling program that is filled with particle data 
# information.
#
# Author: Christopher Neal
#
# Date: 11-27-2015
# Updated: 11-27-2015
#
#######################################################################################

def Read_HDF5_Particle_Data(CaseName,timeStamp,ScriptPath):

	import numpy as np
	import os
	import itertools

	#Read particle diameter HDF5 File
	FileName = "ptdia_ptsca."+str(timeStamp)+"_"+CaseName

	BashCommand = ScriptPath+"/"+"Extract_HDF5Data.sh "+ FileName
	os.system(BashCommand)
	#The system call to the script has generated an output file with particle diameter data
	#called: tempPythonFile.txt
	
        #open file if file exists, otherwise throw exception
	try:
		f=open("tempPythonFile.txt",'r')
        except IOError as e:
    		print "Unable to open file" #Does not exist OR no read permissions
        

	print("Storing diameter data from file: %s"%(FileName))
	DiameterData=[]
	ReadyToRead = False
	entryCount = 0
	for Line in f:

		#Stop when we have been reading data and we encounter a brace character on the line
                if(ReadyToRead == True  and "}" in Line ):
                        break

		if(ReadyToRead == True):
			#Parse line
			LineData=Line.rstrip()
			LineData =LineData.replace(","," ")
			LineData=LineData.split()

			DiameterData.append(LineData)

			#Count number of entries on this line
			entryCount = entryCount + len(LineData)

		if( "DATA {" in Line ):	#Real data is on next line. Prepare to read
			ReadyToRead = True
	


	#Close and delete the data file
	f.close()
	os.remove("tempPythonFile.txt")

	#Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
	DiameterData=list(itertools.chain.from_iterable(DiameterData))

	print("Detected %d parcels in data file"%(entryCount))


	#Read Parcel Coordinate Data from File
        FileName = "particle_pos."+str(timeStamp)+"_"+CaseName

	BashCommand = ScriptPath+"/"+"Extract_HDF5Data.sh "+ FileName
        os.system(BashCommand)
        #The subprocess call to the script has generated an output file with particle diameter data
        #called: tempPythonFile.txt
	
	#open file if file exists, otherwise throw exception
	try:
                f=open("tempPythonFile.txt",'r')
        except IOError as e:
                print "Unable to open file" #Does not exist OR no read permissions


	print("Storing parcel coordinate data from file: %s"%(FileName))

	#Store data in a 3xN list
        PositionData=[]
	PositionData.append([])
	PositionData.append([])
	PositionData.append([])

        ReadyToRead = False
        StopRead = False
        ParcelCount = 0
	for Line in f:

                #Stop when we have been reading data and we encounter a brace character on the line
                if(ReadyToRead == True and ParcelCount == entryCount ):
			break

                if(ReadyToRead == True):

			Line=f.next()	#Skip the { symbol line

                        #Parse next 3 lines
                        LineData=Line.rstrip()
                        LineData =LineData.replace(","," ")
                        LineData=LineData.split()

                        PositionData[0].append(LineData)

			Line=f.next()
			LineData=Line.rstrip()
                        LineData =LineData.replace(","," ")
                        LineData=LineData.split()

			PositionData[1].append(LineData)

			Line=f.next()
                        LineData=Line.rstrip()
                        LineData =LineData.replace(","," ")
                        LineData=LineData.split()

			PositionData[2].append(LineData)


			#Skip the last brace
			Line=f.next()
			
			ParcelCount = ParcelCount + 1

                if("DATA {" in Line):   #Real data is on next line. Prepare to read
                        ReadyToRead = True


        #Close and delete the data file
        f.close()
	os.remove("tempPythonFile.txt")

	#Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
	for k in range(0,3):
        	PositionData[k]=list(itertools.chain.from_iterable(PositionData[k]))

	print("Number of rows in parcel position data set:%d\nNumber of columns in parcel position data set:%d"%(len(PositionData),len(PositionData[0])))
	

	#Read number of particles per parcel data from HDF5 File
        FileName = "ptnump_ptsca."+str(timeStamp)+"_"+CaseName

	BashCommand = ScriptPath+"/"+"Extract_HDF5Data.sh "+ FileName
        os.system(BashCommand)
        #The subprocess call to the script has generated an output file with particle diameter data
        #called: tempPythonFile.txt

        #open file if file exists, otherwise throw exception
	try:
                f=open("tempPythonFile.txt",'r')
        except IOError as e:
                print "Unable to open file" #Does not exist OR no read permissions


	print("Storing particles per parcel data from file: %s"%(FileName))

        ParticleNumberData=[]
        ReadyToRead = False
	parcel_check_counter = 0 #For checking that all data is actually being read from file
	for Line in f:

                #Stop when we have been reading data and we encounter a brace character on the line
                if(ReadyToRead == True and "{" in Line ):
                        break

                if(ReadyToRead == True):
                        #Parse line
                        LineData=Line.rstrip()
                        LineData =LineData.replace(","," ")
                        LineData=LineData.split()
		

                        ParticleNumberData.append(LineData)
			parcel_check_counter = parcel_check_counter + 1

                if("DATA {" in Line):   #Real data is on next line. Prepare to read
                        ReadyToRead = True


        #Close the data file
        f.close()
	os.remove("tempPythonFile.txt")	

	#Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
        ParticleNumberData=list(itertools.chain.from_iterable(ParticleNumberData))

	print("Number of particles per parcel data read: %d"%(parcel_check_counter))

	#Store all of the particle data that is currently in a list format into one large list
	ParticleData=[]
	for i in range(0,entryCount):
		ParticleData.append([])

		ParticleData[i].append(DiameterData[i])
		ParticleData[i].append(PositionData[0][i])
        	ParticleData[i].append(PositionData[1][i])
        	ParticleData[i].append(PositionData[2][i])
		ParticleData[i].append(ParticleNumberData[i])


	return ParticleData

