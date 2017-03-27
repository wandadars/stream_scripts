#! /usr/bin/env python
# Purpose:	Parses the contents of the generated .mdl and .tran files that are created from the chemkin-converter
#               utility that Loci-Stream uses. 
#
# Input: 	(1) - Case name that is being used e.g. acetone.mdl  << the casename would be acetone 
#
# Output: 	An updated set of ascii files with chemical species names that can be parsed by Loci utilities without
#               throwing an error. 
#
########################################################################
import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import time #For deubbging
from shutil import copyfile

class Loci_thermo_file_renamer():

    def __init__(self):
        self.case_name = ''
        self.all_species_map = {}

    def translate_files(self,case_name):
        self.case_name = case_name

        detected_species = self.read_species_from_mdl()
        self.clean_up_species_names(detected_species)

        self.update_mdl_file_species_definitions()
        self.update_tran_file_species_definitions()

    def read_species_from_mdl(self):
        try:
            mdl_file = open(self.case_name+'.mdl','r')
        except:
            print("Error Opening mdl file named: "+ self.case_name + ".mdl")
        
        all_species = []
        for Line in mdl_file:
            tmp = Line.rstrip()
            if "= <" in tmp:
                species_name = tmp.split("=")
                all_species.append(species_name[0])
        mdl_file.close()
        return all_species

    def clean_up_species_names(self,all_species):
        for species in all_species:
            self.all_species_map[species] = self.remap_species_name(species)
        
    def remap_species_name(self,species_name):
        name_adjusted = False

        if '-' in species_name:
            species_name = species_name.replace('-','dash')
            name_adjusted = True

        if '*' in species_name:
            species_name = species_name.replace('*','star')
            name_adjusted = True
        
        if 'AR' in species_name:
            species_name = species_name.replace('AR','Ar') 
            name_adjusted = True

        if species_name.startswith('a') and (species_name[1] !='r' or species_name !="R"):
            name_adjusted = True

        if species_name.startswith('i'):
            name_adjusted = True
       
        elif species_name.startswith('o'):
            name_adjusted = True

        elif species_name.startswith('t'):
            name_adjusted = True

        elif species_name.startswith('p'):
            name_adjusted = True

        elif species_name.startswith('s'):
            name_adjusted = True

        elif species_name.startswith('n'):
            name_adjusted = True
        
        elif species_name.startswith('c'):
            name_adjusted = True
        
        elif species_name.startswith('l'):
            name_adjusted = True
        
        if "(" in species_name or ")" in species_name:
            parenthesis_content = (species_name.split("("))[1].split(")")[0]
            parsed_parenthesis_content = self.translate_parenthesis_contents(parenthesis_content)
            species_name = species_name.split("(")[0]+parsed_parenthesis_content
            name_adjusted = True

        if name_adjusted == True:
            species_name = '_'+species_name

        return species_name

    def translate_parenthesis_contents(self,contents):
        translation_key = {"0":"Zero","1":"One", "2":"Two","3":"Three","4":"Four","5":"Five","6":"Six","7":"Seven","8":"Eight","9":"Nine",",":"Comma"}
        new_output = ''
        for letter in list(contents):
            new_output+=translation_key[letter]
        return new_output


    def update_mdl_file_species_definitions(self):
        try:
                    mdl_file = open(self.case_name+".mdl",'r')
        except:
                    print("Error Opening mdl file")

        mdl_file_data = mdl_file.read()
        mdl_file.close()

        for species in self.all_species_map:
            mdl_file_data = mdl_file_data.replace(species,self.all_species_map[species])

        try:
            mdl_file= open(self.case_name+"_new.mdl",'w')
        except:
            print("Error Opening mdl output file")

        mdl_file.write(mdl_file_data)
        mdl_file.close()


    def update_tran_file_species_definitions(self):
        try:
                    tran_file = open(self.case_name+".tran",'r')
        except:
                    print("Error Opening transport file")

        tran_file_data = tran_file.read()
        tran_file.close()

        for species in self.all_species_map:
            tran_file_data = tran_file_data.replace(species,self.all_species_map[species])

        try:
            tran_file= open(self.case_name+"_new.tran",'w')
        except:
            print("Error Opening transport output file")

        tran_file.write(tran_file_data)
        tran_file.close()






#Store user input filename
try:
	case_name = sys.argv[1]
except:
	print("Error reading inputs")


run_case = Loci_thermo_file_renamer()
run_case.translate_files(case_name)


print("Program Finished...")

