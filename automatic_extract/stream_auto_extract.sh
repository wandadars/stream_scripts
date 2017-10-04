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
# 2.) The increment in the timestep that should be used E.g. starting at 1000 with
#     an increment of 50 would result in solutions post processed from timesteps
#     1000, 1050, 1100, 1150, etc. 
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
    echo "  --timesteps                 : tell what the desired range of timesteps to extract is(start,step,stop). Put values in double quotes \"1000 50 2000 \" "
    echo "  --variables                 : tell what variables should be extracted. Put values in double quotes e.g. \"v P r t a \" "
    echo " "
    echo "Optional <options>"
    echo "  --geom_changing             : tell whether the grid changes with each timestep( YES if true. default is NO."
    echo " "
    echo "Example Usage:  "
    echo "./Stream_Auto_Extract --casename supersonicJet --output en --timesteps "1000 50 2000" --variables "v P r t pResidualTT" "
    exit -1
fi


casename=notset
variables=notset
output_format=notset
timesteps=notset
geom_changing=notset
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

         --timesteps)
            timesteps=$2
            shift
            ;;

        --variables)
            variables=$2
            shift
            ;;
        
        --geom_changing)
            geom_changing=$2
            shift
            ;;

        --help)
            echo "usage:"
            echo "./Stream_Auto_Extract <options>"
            echo "Required <options> are"
            echo "  --casename                  : tell what the Loci-Stream casename is"
            echo "  --output                    : tell what the desired output format is (en->ensight)"
            echo "  --timesteps                 : tell what the desired range of timesteps to extract is(start,step,stop). Put values in double quotes \"1000 50 2000 \" "
            echo "  --variables                 : tell what variables should be extracted. Put values in double quotes e.g. \"v P r t a \" "
            echo " "
            echo "Optional <options>"
            echo "  --geom_changing             : tell whether the grid changes with each timestep( YES if true. default is NO."
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

#echo $casename
#echo $output_format
#echo $variables

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

if [ "$geom_changing" == "notset" ]; then
    geom_changing="0"
fi



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

echo "Extracting List of Solution Times From Solution Files"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #Directory of the location of this script
python $DIR/stream_ensight_time_series.py --casename $casename --timesteps $timesteps --extract_path $RunString --extract_variables $variables --extract_format $output_format --geom_changing $geom_changing

echo 'Time Series Solution Extraction Finished'

