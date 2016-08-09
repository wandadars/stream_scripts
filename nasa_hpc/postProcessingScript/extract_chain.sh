#!/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to submit several independent post-processing jobs. 
#          The job submission script will be the slighly the same. The only difference
#          will be the timestamp that the executable will be processing.
#
#
# Author: Christopher Neal
#
# Date: 08-08-2016
# Updated: 08-08-2016
#
#######################################################################################

# This script should be executed in the directory that contains the template job 
# submission script. As well as the head simulation directory that contains the
# directories like: output restart and debug
#
# It takes the following 3 arguments:
# 1.) The solution stride that you want to post-process
# 2.) The integer value of the solution that you want to start processing from
#	i.e. if argument 1 is 1 and argument 2 is 6 then the script will process
#	all solution timesteps INCLUDING the 6th one and after in the directory. This feature is 
#	useful for processing additional solutions without re-processing every solution 
#	file in the working directory.
#
# 3.) The maximum number of files to analyze up to in terms of the integer index of the
#       files. The script will submit jobs for timesteps up to and including the one
#       specified by the 3rd argument. If the 3rd argument is left EMPTY, then all 
#       solutions will be processed.
#
#

echo 'Running Stream Post-Processing Chain Submission Script'


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

mv Extracted_Timestamps.txt ..
cd ..

#Remove temporary files
rm -rf temp.txt

###


# Copy the .pbs job script to a temporary file to prevent the template
# from being permanently changed.
cp -rf  job_extract_chain.pbs tempScript.pbs

if [ "$#" -lt 3 ]; then
	MaxJobNum=1000000
else
	MaxJobNum=$3
fi

#Loop over times in the file Extracted_Data_Labels.txt and submit jobs
c=1
while read line1
do


if [ $(($c%$1)) == 0 -a $c -le $MaxJobNum ]; then #Check to see if the file is a multiple of the stride # input

   if [ -z "$2" ]; then #If argument returns true is the second input argument is empty

      echo "Submitting job file $c for post-processing time: $line1 "
   
      #Replace job log file line in submission script with unique identifier
      ReplaceString="#PBS -o job_extract_chain_$c.log"
      sed -i "s/#PBS -o.*/$ReplaceString/" job_extract_chain.pbs

      # The variable $line1 contains the timestamp that we want to run post-processing for
      # Replace the solution_time entry in the job submission template with the actual time
      # and submit job
      ReplaceString="$line1"  

      #sed -i "s/solutionTime.*/$ReplaceString/" job_extract_chain.pbs
      sed -i "s/solutionTime/$ReplaceString/g" job_extract_chain.pbs

      #Submit the job file
      qsub job_extract_chain.pbs

      #Copy over the altered job file with the temporary template tempScript.pbs
      cp -rf  tempScript.pbs job_extract_chain.pbs
  
   else
   
      if [ $line1 -ge $2 ]; then  #Process files starting from file number stored in $2
         echo "Submitting job file $c for post-processing time: $line1 "

         #Replace job log file line in submission script with unique identifier
         ReplaceString="#PBS -o job_extract_chain_$c.log"
         sed -i "s/#PBS -o.*/$ReplaceString/" job_extract_chain.pbs

         # The variable $line1 contains the timestamp that we want to run rflupost for
         # Replace the TimeStamp entry in the job submission template with the actual time
         # and submit job

         ReplaceString="$line1"

         #sed -i "s/solutionTime.*/$ReplaceString/" job_extract_chain.pbs
	 sed -i "s/solutionTime/$ReplaceString/g" job_extract_chain.pbs

         #Submit the job file
	 cat job_extract_chain.pbs
         qsub job_extract_chain.pbs

         #Copy over the altered job file with the temporary template tempScript.pbs
         cp -rf  tempScript.pbs job_extract_chain.pbs
      fi #$c -ge $2

   fi #-z "$2"

fi #$(($c%$1)) == 0 

#Increment the counting variable, c
c=$(($c+1))

done < Extracted_Timestamps.txt

# Write over the altered job_RFLU_postchain.pbs file with the unaltered version
# stored in tempScript.pbs

cp -rf  tempScript.pbs job_extract_chain.pbs

# Delete temporary file
#rm -rf tempScript.pbs

echo 'Program Finished...Ending'

