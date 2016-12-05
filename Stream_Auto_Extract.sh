#/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to make several calls to a loci-stream post-
# 	   processing script. The calls will loop over the timestamps of the files that
#	   the user wants to post process. 
#
#
# Author: Christopher Neal
#
# Date: 07-09-2015
# Updated: 12-01-2016
#
#######################################################################################

# This script should be executed in the directory that contains head simulation file. 
# In addition to generating post-procesed filed, it will move all files into a directory
# called paraivew_data to quicken access to the solution files and to prevent clutter in
# the main directory.
#
# It takes the following 2 arguments:
# 1.) The solution stride that you want to post-process i.e. every 2 files, every 3,etc.
# 2.) The integer value of the timestamp that you want to start processing from
#	i.e. if argument 1 is 1 and argument 2 is 6 then the script will process
#	all solutions INCLUDING and after the 6th one in the directory. This feature is 
#	useful for processing additional solutions without re-processing every solution 
#	file in the working directory.
#

ExtractString="v P r t a"
CaseName="case"
OutputFormat="en"

RunString="/home/jeff/software/Loci-3.3-p3/Loci-Linux-x86_64-mpic++-rel-3-3-p3/bin/extract" 

echo 'Running Loci-Stream Post-Processing Chain Submission Script'

##Extract Solution Times####
echo "Extracting List of Solution Times From Solution Files"

cd output

#Put all files in current directory into a text file
ls t_sca.* > temp.txt


#Trim filename up the first underscore.
sed -n -i "s/[^_]*_//p" temp.txt

#Trim filenames up to the first period.
sed  -i 's/^[^.]*.//' temp.txt

#Flip Lines
sed -i '/\n/!G;s/\(.\)\(.*\n\)/&\2\1/;//D;s/.//' temp.txt

#Trim filename up the first underscore.
sed -n -i "s/[^_]*_//p" temp.txt

#Reverse lines back to orginal orientation
sed  -i '/\n/!G;s/\(.\)\(.*\n\)/&\2\1/;//D;s/.//' temp.txt


#At this point we have all of the timestamps, but they mat not be sorted.
#Sort the times and store them in the file Extracted_Timestamps.txt

sort -k1g temp.txt > Extracted_Timestamps.txt

#Remove temporary files
rm -rf temp.txt

mv Extracted_Timestamps.txt ..

cd ..

###

echo "Extracting Variables: $ExtractString"


#Loop over times in the file Extracted_Timestamps.txt and submit jobs
c=1
while read line1
do

if [ $(($c%$1)) == 0 ]; then #Check to see if the file is a multiple of the stride # input

   if [ -z "$2" ]; then #If argument returns true is the second input argument is empty

      echo "Running extract on file $c for post-processing timestamp: $line1 "
   
      $RunString -$OutputFormat $CaseName $line1 $ExtractString

  
   else
   
      if [ $line1 -ge $2 ]; then  #Process files starting from file number stored in $2
         
         echo "Running extract on file $c for post-processing timestamp: $line1 "

         $RunString -$OutputFormat $CaseName $line1 $ExtractString

      fi #$c -ge $2

   fi #-z "$2"

fi #$(($c%$1)) == 0 

#Increment the counting variable, c
c=$(($c+1))

done < Extracted_Timestamps.txt

#For Paraview data move all into 1 single directory
if [ $OutputFormat == "vtk" ]; then
	rm -rf paraview_data
	mkdir paraview_data
	mv vtk* paraview_data
fi


echo 'Program Finished...Ending'

