#/bin/bash
#######################################################################################
# Purpose: The purpose of this script is call the h5dump command on a designated fil
#
# Author: Christopher Neal
#
# Date: 11-27-2015
# Updated: 11-27-2015
#
#######################################################################################

# This script should be executed by the python program that calls it only
# It takes the following argument:
# 1.) The name of the file that needs to be h5dumped to a temporary file for reading
#     by the Python program


h5dump --noindex $1 > tempPythonFile.txt


