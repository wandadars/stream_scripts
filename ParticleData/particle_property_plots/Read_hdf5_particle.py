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
        if( "DATA {" in Line ): #Real data is on next line. Prepare to read
            ReadyToRead = True
    


    #Close and delete the data file
    f.close()
    os.remove("tempPythonFile.txt")

    #Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
    DiameterData=list(itertools.chain.from_iterable(DiameterData))

    print("Detected %d parcels in data file"%(entryCount))


    #Read particle diameter HDF5 File
    FileName = "pttemp_ptsca."+str(timeStamp)+"_"+CaseName

    BashCommand = ScriptPath+"/"+"Extract_HDF5Data.sh "+ FileName
    os.system(BashCommand)
    #The system call to the script has generated an output file with particle diameter data
    #called: tempPythonFile.txt
    
    #open file if file exists, otherwise throw exception
    try:
        f=open("tempPythonFile.txt",'r')
    except IOError as e:
        print "Unable to open file" #Does not exist OR no read permissions
        

    print("Storing temperature data from file: %s"%(FileName))
    TemperatureData=[]
    ReadyToRead = False
    for Line in f:

        #Stop when we have been reading data and we encounter a brace character on the line
        if(ReadyToRead == True  and "}" in Line ):
            break

        if(ReadyToRead == True):
            #Parse line
            LineData=Line.rstrip()
            LineData =LineData.replace(","," ")
            LineData=LineData.split()

            TemperatureData.append(LineData)

        if( "DATA {" in Line ): #Real data is on next line. Prepare to read
            ReadyToRead = True
    

    #Close and delete the data file
    f.close()
    os.remove("tempPythonFile.txt")

    #Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
    TemperatureData=list(itertools.chain.from_iterable(TemperatureData))

    #Store all of the particle data that is currently in a list format into one large list
    ParticleData=[]
    for i in range(0,entryCount):
        ParticleData.append([])
        ParticleData[i].append(DiameterData[i])
        ParticleData[i].append(TemperatureData[i])


    return ParticleData

