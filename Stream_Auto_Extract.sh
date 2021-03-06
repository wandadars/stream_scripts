#/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to make several calls to a loci-stream post-
# 	   processing script. The calls will loop over the timestamps of the files that
#	   the user wants to post process. 
#
# Author: Christopher Neal
#
# Date: 07-09-2015
# Updated: 09-19-2017
#
#######################################################################################

# This script should be executed in the directory that contains the main simulation files. 
# In addition to generating post-procesed files, it will move all files into a directory
# called ensight(or paraview)_data to quicken access to the solution files and to prevent 
# solution clutter in the main directory.
#
# It takes the following 5 arguments:
# 1.) The starting timestep number that the extraction process should begin with. 
# 2.) The increment in the timestep that should be used E.g. Using a step of 1 and
#     starting at 1000 would process all timesteps after and including the 1000th. 
#     an increment of 50 would result in solutions post processed from timesteps
#	i.e. if argument 1 is 1 and argument 2 is 6 then the script will process
#	all solutions INCLUDING and after the 6th one in the directory. This feature is 
#	useful for processing additional solutions without re-processing every solution 
#	file in the working directory.
#

#set +e
#set -u
#set -f

find_extract() {
    RETURN_VALUE=0
    for i in ${PATH//:/ }; do
    if [ -e $i/"extract" ]; then
        RETURN_VALUE=$i
        break ;
    fi
    done
}


#Check for case when no arguments are given
if [ $# -eq 0 ]; then
    echo "usage:"
    echo "./Stream_Auto_Extract <options>"
    echo "Required <options> are"
    echo "  --casename                  : tell what the Loci-Stream casename is"
    echo "  --output                    : tell what the desired output format is (en-ensight)"
    echo "  --timesteps                 : tell what the desired range of timesteps to extract is(step, start). Put in double quotes \"1 50 \" "
    echo "  --variables                 : tell what variables should be extracted. Put values in double quotes e.g. \"v P r t a \" "
    echo " "
    echo "Example Usage:  "
    echo "./Stream_Auto_Extract --casename supersonicJet --output en --variables "v P r t pResidualTT" "
    exit -1
fi


casename=notset
variables=notset
output_format=notset
timesteps=notset
while [ $# -ne 0 ]; do
    case "$1" in
        --casename)
            casename=$2
            shift
            ;;

        --output)
            output_format=$2
            shift
            ;;

        --variables)
            variables=$2
            shift
            ;;
        
        --timesteps)
            timesteps=$2
            shift
            ;;

        --help)
            echo "usage:"
            echo "./Stream_Auto_Extract <options>"
            echo "Required <options> are"
            echo "  --casename                  : tell what the Loci-Stream casename is"
            echo "  --output                    : tell what the desired output format is (en-ensight)"
            echo "  --timesteps                 : tell what the desired range of timesteps to extract is(step, start). Put in double quotes \"1 50 \" "
            echo "  --variables                 : tell what variables should be extracted. Put values in double quotes e.g. \"v P r t a \" "
            echo " "
            echo "Example Usage:  "

            echo "./Stream_Auto_Extract --casename supersonicJet --output en --timesteps "1000 50 2000" --variables "v P r t pResidualTT" "
            exit -1
            ;;

        *)
            echo configure option \'$1\' not understood!
            echo use ./Stream_Auto_Extract --help to see correct usage!
            exit -1
            break
            ;;
    esac
    shift
done

echo $casename
echo $output_format
echo $variables
echo $timesteps

if [ $casename == "notset" ]; then
    echo "Case name must be specified. Use --help for proper usage."
    exit -1
fi
if [ $output_format == "notset" ]; then
    echo "Output format must be specified. Use --help for proper usage."
    exit -1
fi
if [ "$variables" == "notset" ]; then
    echo "Variables must be specified. Use --help for proper usage."
    exit -1
fi
if [ "$timesteps" == "notset" ]; then
    echo "Timestep range must be specified. Use --help for proper usage."
    exit -1
fi


ExtractString=$variables
CaseName=$casename
OutputFormat=$output_format
TimeSteps=$timesteps

find_extract
if [ $RETURN_VALUE != 0 ]; then
    RunString="$RETURN_VALUE/extract"
    echo $RunString 
else
    echo "Unable to find Loci extract utility needed to run script"
    echo "Make sure it is in your PATH. If all else fails, manually"
    echo "change the "RunString" variable in this script to the proper path"
    exit -1
fi


echo 'Running Loci-Stream Post-Processing Chain Submission Script'

##Extract Solution Times####
echo "Extracting List of Solution Times From Solution Files"

cd output
echo "$PWD"
#Put all files in current directory into a text file
ls r_sca.* > temp_sni.txt

#Trim filenames up the first underscore.
sed -n -i "s/[^_]*_//p" temp_sni.txt

#Trim filenames up to the first period.
sed  -i 's/^[^.]*.//' temp_sni.txt

#Flip Lines
sed -i '/\n/!G;s/\(.\)\(.*\n\)/&\2\1/;//D;s/.//' temp_sni.txt

#Trim filename up the first underscore.
sed -n -i "s/[^_]*_//p" temp_sni.txt

#Reverse lines back to orginal orientation
sed  -i '/\n/!G;s/\(.\)\(.*\n\)/&\2\1/;//D;s/.//' temp_sni.txt


#At this point we have all of the unordered timestamps.
#Sort the times and store them in the file Extracted_Timestamps.txt
sort -k1g temp_sni.txt > Extracted_Timestamps.txt

#Remove temporary files
#rm -rf temp_sni.txt

mv Extracted_Timestamps.txt ..
cd ..



### Extract Phase ###
echo "Extracting Variables: $ExtractString"

#Loop over times in the file Extracted_Timestamps.txt and extract
Step="$(cut -d' ' -f1 <<<$TimeSteps)"
Start="$(cut -d' ' -f2 <<<$TimeSteps)"

echo $Start
echo $Step

c=1
while read line1
do

if [ $(($c%$Step)) == 0 ]; then #Check to see if the file is a multiple of the stride # input

   if [ -z "$Start" ]; then #Start extracting from beginning 

      echo "Running extract on file $c for post-processing timestamp: $line1 "
      $RunString -$OutputFormat $CaseName $line1 $ExtractString
  
   else
   
      if [ $line1 -ge $Start ]; then  #Process files starting from starting file number stored in $Start
         
         echo "Running extract on file $c for post-processing timestamp: $line1 "
         $RunString -$OutputFormat $CaseName $line1 $ExtractString

      fi #$c -ge $Start

   fi #-z "$Start"

fi #$(($c%$Step)) == 0 

#Increment the counting variable, c
c=$(($c+1))

done < Extracted_Timestamps.txt

echo 'Solution Extraction Finished'

