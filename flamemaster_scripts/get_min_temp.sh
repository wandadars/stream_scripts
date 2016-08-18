#!/bin/bash

#Extract all names of files in directory
ls | grep st > min_temperature_tempfile.txt

#Strip away all text except the stoichiometric temperature at the end of each filename
sed -i 's/.*st//' min_temperature_tempfile.txt


#Sort from low to high
sort -n min_temperature_tempfile.txt -o min_temperature_tempfile.txt

#Extract the first line i.e. the lowest temperature

line=$(head -n 1 min_temperature_tempfile.txt)

echo "Min value of temperature is: " $line

#Delete temporary file
rm -rf min_temperature_tempfile.txt


#
