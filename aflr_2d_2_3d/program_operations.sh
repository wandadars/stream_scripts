#!/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to take in an argument and execute a command
#	   based on the argument.
#
# Author: Christopher Neal
#
# Date: 07-06-2016
# Updated: 07-06-2016
#
#######################################################################################

# This script takes 2 main argument and various additional arguments based on the first
# argument.
#
# Argument values & dependent arguments
#
#	1 - Casename that describes the <caseName>.vog of the original pie slice
#	2 - Flag for executing different commands
#		Flag Values:
#		0 - Execute renaming of original boundary faces
#			3rd argument -  name of the boundary located at the original location of the pre-rotated 2d lane
#			4th argument - the name of the boundary located at the roated plane for the pie slice
#				example:  BC_15 BC_14  Because of the way aflr2d names boundaries this is what they are called for a sample case that I have
#
#		1 - Execute a user defined rotation of the original pie slice
#			3rd argument - angle to rotate pie slice through
#
#		2 - Merge the first slice with the rotated slice * Only used for the first combination, otherwise use option 3 or 4
#
#		3 - Merge the combined block with the rotated slice
#
#		4 - Merge the combined block with the final pie slice that closes the circle.
#
caseName=$1

echo $@

vogmergePath= which vogmerge
if [ $2 -eq 0 ]; then 
    echo "Using vogmerge found here: $vogmergePath"
	echo "Using Command: vogmerge -g $1.vog -o $1_starting.vog -bc $3,face1 -bc $4,face2"
	vogmerge -g $1.vog -o $1_starting.vog -bc $3,face1 -bc $4,face2
    wait

elif [ $2 -eq 1 ]; then 
	echo "Using Command: vogmerge -g $1_starting.vog -o $1_rotated_1.vog -xrotate $3"
	vogmerge -g $1_starting.vog -o $1_rotated_1.vog -xrotate -$3
    wait

elif [ $2 -eq 2 ]; then
	echo "Using Command: vogmerge -g $1_starting.vog -glue face2 -g $1_rotated_1.vog -glue face1 -o $1_combined.vog"
    vogmerge -g $1_starting.vog -glue face2 -g $1_rotated_1.vog -glue face1 -o $1_combined.vog -tol 1e-6
    wait

elif [ $2 -eq 3 ]; then
	echo "Using Command: vogmerge -g $1_combined.vog -glue face2 -g $1_rotated_1.vog -glue face1 -o $1_combined_2.vog"
    vogmerge -g $1_combined.vog -glue face2 -g $1_rotated_1.vog -glue face1 -o $1_combined_2.vog -tol 1e-6
    wait
    mv $1_combined_2.vog $1_combined.vog

elif [ $2 -eq 4 ]; then
	echo "Using Command: vogmerge -g $1_combined.vog -glue face2,face1 -g $1_rotated_1.vog -glue face1,face2 -o $1_combined_2.vog"
    vogmerge -g $1_combined.vog -glue face2,face1 -g $1_rotated_1.vog -glue face1,face2 -o $1_combined_2.vog -tol 1e-6
	wait
    mv $1_combined_2.vog $1_combined.vog
fi  





