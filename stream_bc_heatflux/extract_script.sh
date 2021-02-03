#!/usr/bin/env bash

#Set the times that you want to extract below for the extract_times variable. Format is: Start, Step, Stop.
#If you need to extract across different BCs, just change the extract_string variable to suit your needs.

#Script will output one file called qdot_ensemble.dat that contains all of the output data sorted by the first column in increasing order.

extract_times=($(seq 46000 100 66000))
for i in ${extract_times[@]}; do
    echo $i
    #extract_string="-ascii -bc ChamberWalls case ${i} x qdot" 
    extract_string="-ascii -bc BC_4 -bc BC_5 -bc BC_6 case ${i} x qdot" 
    
    #Accumulate all time data into 1 file
    extract ${extract_string} >> qdot_ensemble.dat
    
    #Individual timestep data
    #extract ${extract_string} > qdot_${i}.dat
    #sort -k 1 -g qdot_${i}.dat -o qdot_${i}.dat
done

#For the accumulation option
sort -k 1 -g qdot_ensemble.dat -o qdot_ensemble.dat
