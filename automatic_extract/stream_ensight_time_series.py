#! /usr/bin/env python

# Purpose:  Reads in and change the names of the Loci-Stream Ensight Files for use in 
#       Paraview.
#
# Description:  Loci-Stream can output Ensight files, however the case file and filenames of 
#       the post files are in an incorrect format as well as located in different
#       directories for Paraview to open all the output files at once. The program 
#       rectifies this by doing two important steps. 
#       
#       Step 1: Search through the output directories of the current working directory
#           for the output files and change the names of the files to a proper format
#           "property" => <casename>."property"_"intstep". 
#       
#       Step 2: Build a new case file with the proper syntax so Paraview can open all
#           the timesteps from just a single case file. 
#       
#
#   Author: Christopher Neal
#   Date   : 10/11/2015
#   Updated: 09/26/2017
#
########################################################################

#Modules Section
import os   #for use of reading and writing files
import glob #For parsing folder and file contents in directory 
import time #For pausing python for debugging
import shutil   #For Moving files around in directories
import argparse

def generate_timesteps(start,step,stop):
    #inclusive list because that is desirable behavior for users
    return range(start,stop+step,step)

def create_output_dir(output_dir_name):
    if os.path.isdir("./"+output_dir_name) == False:
        os.makedirs(output_dir_name)
    else:
        shutil.rmtree("./" + output_dir_name)
        os.makedirs(output_dir_name)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--casename", type=str, help="casename of output to be processed")
    parser.add_argument("--timesteps", nargs = '*', type=int, help="timestep range to be processed(start,step,stop)")
    parser.add_argument("--extract_path", type=str, help="path to Loci extract utility on system")
    parser.add_argument("--extract_variables", nargs = '*', type=str, help="variables to Loci extract utility")
    parser.add_argument("--extract_format", type=str, help="output format for Loci extract utility")
    parser.add_argument("--geom_changing", nargs='?', type=int, help="flag for whether gometry is changing with time. 0-no, 1-yes")
    return parser.parse_args()


args = parse_arguments()

#print(args.casename)
#print(args.timesteps)
#print(args.extract_path)
#print(args.extract_variables)
#print(args.extract_format)
#print(args.geom_changing)

CaseName = args.casename
VariableList = args.extract_variables
VariableList.append('pg') #Variable that Loci always adds to output directory 
time_step = generate_timesteps(args.timesteps[0],args.timesteps[1],args.timesteps[2])
extract_path = args.extract_path
extract_format = args.extract_format
GeomChanging = bool(args.geom_changing) #True means there are individual .geo files for each timestep, like with moving meshes.



print("Processing Data for Case: %s\n" %(CaseName) )

create_output_dir(CaseName+"_ensight")

PWD=os.getcwd() 
OutputFolderPath=PWD+"/"+CaseName+"_ensight"

print("Processing Timesteps:")
print(time_step)

num_timesteps=len(time_step)
max_digits=len(str(num_timesteps))


print("\nFollowing " + str(len(VariableList)) + " Output Variables Present:")
for var in VariableList:
    print(var)


#Loop over all solutions are process data
for i,ts in enumerate(time_step):
    print("\nProcessing Data From Timestep: %d"%(i+1))
    extract_command = str(extract_path) + ' ' + '-' + str(extract_format) + ' ' + CaseName + ' ' + str(ts) + ' ' + ' '.join(VariableList)

    #print("Running Command: "+extract_command)
    os.system(extract_command)
    current_folder_path = PWD+"/"+CaseName+"_ensight."+str(ts)
    os.chdir(current_folder_path)
    
    #Determine the appropriate amount of padding zeros
    ZeroPad = '0'*( max_digits - len(str(i)) ) 

    #Loop over plotting variable files and copy them to output directory with correct name
    for variables in VariableList:

        NewVariableName = variables.replace("_","") #ENSIGHT doesn't like variable names with underscores
        NewVariableName = NewVariableName + "_" + ZeroPad+str(i) #ENSIGHT GOLD accepted name

        PathToOriginalFile = os.path.join(current_folder_path, variables)
        PathToNewFile      = os.path.join(OutputFolderPath, NewVariableName)
        shutil.copy(PathToOriginalFile, PathToNewFile)

    #Rename any particles files to contain timestamp if they exist
    OldParticlesName= CaseName + "_particles.geo"
    if(os.path.isfile(OldParticlesName) == True):
        NewParticlesName = CaseName + "_particles.geo" + "_" + ZeroPad+str(i)
        PathToOriginalFile = os.path.join(current_folder_path, OldParticlesName)
        PathToNewFile      = os.path.join(OutputFolderPath, NewParticlesName)
        shutil.copy(PathToOriginalFile, PathToNewFile)


    #If geometry changes, then update the geometry file names & move the files
    if(GeomChanging == True):
        OldGeometryName = CaseName + ".geo"
        if(os.path.isfile(OldGeometryName) == True):
            NewGeometryName = CaseName + ".geo" + "_" + ZeroPad+str(i)
            PathToOriginalFile = os.path.join(current_folder_path, OldGeometryName)
            PathToNewFile      = os.path.join(OutputFolderPath, NewGeometryName)
            shutil.copy(PathToOriginalFile, PathToNewFile)

    #Need to move the at least 1 geometry file to output
    if(i == 0 and GeomChanging == False):  
        GeometryName = CaseName + ".geo"
        PathToOriginalFile = os.path.join(current_folder_path, GeometryName)
        PathToNewFile      = os.path.join(OutputFolderPath, GeometryName)
        shutil.copy(PathToOriginalFile, PathToNewFile)

    #Need to move the at least 1 case file to output
    if(i == 0 ):                                             
        CaseFileName = CaseName + ".case"
        PathToOriginalFile = os.path.join(current_folder_path, CaseFileName)
        PathToNewFile      = os.path.join(OutputFolderPath, CaseFileName)
        shutil.copy(PathToOriginalFile, PathToNewFile)

    shutil.rmtree(current_folder_path)
    os.chdir("..")



#Go to the final output directory and edit the case file
os.chdir(OutputFolderPath)  

#Rebuild the case file so that paraview can open as a multi file transient set
#The name of the case file that Paraview will recognize is seperated by "."
case_filename = CaseName+".case"

#Update all variable lines to use wildcard representation
print("\nUpdating Case file Specification")
tmpFile=open("TempCaseFile",'w+')
Wild_Card = "*" * max_digits   #For use in Ensight Gold Case File Output Format
for FileLine in open (case_filename, "r") :
    FileLine=FileLine.rstrip('\n')  #Strip newline character off end of line
    FileLine=FileLine.split()

    for variable in VariableList:
        if variable in FileLine:
            #Note that if variable had underscore in name, the associated file will not have that
            #and so we must remove it from the wildcare filename
            FixedVariableName = variable.replace("_","")
            WildCardString = FixedVariableName + "_" + Wild_Card
            FileLine[-1]=WildCardString

    #Check for particles content->Need to add wildcard name if particles present
    if CaseName + "_particles.geo" in FileLine:
        WildCardString=CaseName + "_particles.geo" + "_" + Wild_Card
        FileLine[-1]=WildCardString

    if(GeomChanging == True):
        if CaseName + ".geo" in FileLine:
            WildCardString = CaseName + ".geo" + "_" + Wild_Card
            FileLine[-1]=WildCardString


    FileLine='\t'.join(FileLine)
    tmpFile.write(FileLine+'\n')


tmpFile.close()


os.rename("TempCaseFile",case_filename)

#Write time series data to file
File=open(case_filename,'a')

File.write("TIME\n")
File.write('time set:\t1\n')
File.write('number of steps:\t' + str(len(time_step)) + '\n')
File.write('filename start number:\t0\n')
File.write('filename increment:\t1\n')
File.write('time values:\t\n') 

#Add the timesteps' numerical names 
for time in time_step:
    File.write(str(time))
    File.write("\n")

File.close()

