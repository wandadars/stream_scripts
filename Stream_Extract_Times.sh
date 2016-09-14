#/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to extract all of the timestamps that are 
#	   present in the solution files that are written to the output directory. 
#
# Author: Christopher Neal
#
# Date: 07-09-2016
# Updated: 07-09-2016
#
#######################################################################################

# This script should be executed in the directory that contains head simulation files. 

echo 'Running Loci-Stream Extract Timestamps '

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

echo 'Program Finished...Ending'

