#! /bin/bash

#The purpose of this script is to get around issues that arise when compiling Paraview on OpenSuse13.2

for i in ../tempbin/*; do
	ln -s $i
done
