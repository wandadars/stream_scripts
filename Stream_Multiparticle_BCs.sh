#/bin/bash
#######################################################################################
# Purpose: The purpose of this script is to generate a file that contains the boundary
#	   conditions for N particles in a domain.
#
# Author: Christopher Neal
#
# Date: 07-31-2015
# Updated: 07-31-2015
#
#######################################################################################
# It takes the following 2 arguments:
# 1.) The number of particles to include in the output file.
# 2.) The exact boundary condition that you want to apply to the boundaries(do not include the - sign) and
#     place the desired boundary condition in single quotes to prevent scrip from crashing due to ()'s.
#
#	Example: script_name 500 slip()

echo 'Running Loci-Stream Boundary Condition Generating Script'

c=1

while [ $c -le $1 ]; do

	if [ "$c" -eq "1" ]; then
		echo " BC_$c=$2, ">streamBCs.dat

	else
		echo " BC_$c=$2, ">>streamBCs.dat
	fi


	c=$(($c+1))

done 


echo 'Program Finished...Ending'

