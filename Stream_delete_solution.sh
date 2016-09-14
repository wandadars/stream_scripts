#!/bin/bash
#######################################################################################
# The purpose of this script is to delete solution files in a directory. The script
# looks at the solutions in the directory and performs a strided deletion of the files.
# For example: If the argument to the script is 2 then it will delete every second file.
#
# Author: Christopher Neal
#
# Date: 09-06-2016
# Updated: 09-06-2016
#
#######################################################################################

# This script should be executed in the directory that contains head simulation files. 
#
# It takes the following 2 arguments:
# 1.) The solution stride that you want to post-process i.e. every 2 files, every 3,etc.
# 2.) The integer value of the timestamp that you want to start processing from
#	i.e. if argument 1 is 1 and argument 2 is 6 then the script will process
#	all solutions INCLUDING and after the 6th one in the directory. This feature is 
#	useful for processing additional solutions without re-processing every solution 
#	file in the working directory.
#

echo 'Running Loci-Stream Solution Deleting Script'

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


#Loop over times in the file Extracted_Timestamps.txt and submit jobs
c=1
while read line1
do

if [ $(($c%$1)) == 0 ]; then #Check to see if the file is a multiple of the stride # input

   if [ -z "$2" ]; then #If argument returns true is the second input argument is empty

      echo "Removing solution: $line1 "
   
      rm -rf output/*$line1*

  
   else
   
      if [ $line1 -ge $2 ]; then  #Process files starting from file number stored in $2
         
         echo "Removing solution: $line1 "
	
	 rm -rf output/*$line1*


      fi #$c -ge $2

   fi #-z "$2"

fi #$(($c%$1)) == 0 

#Increment the counting variable, c
c=$(($c+1))

done < Extracted_Timestamps.txt


echo 'Program Finished...Ending'

