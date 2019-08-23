#! /usr/bin/env python
"""
    Purpose:	Rotates a 2d grid made by AFLR2D into a 3D axisymmetric grid.
    Input: 	Base filename of the grid and the angular resolution of the 3D grid.
    Output: 	A 3D grid.
"""
import os 
import sys 
import re
import time
import subprocess


class InputFileParser(object):
    def __init__(self, file_name):
        self.user_input_data = {}
        self.input_file_name = ''
        self.read_input_file(file_name)

    def read_input_file(self, file_name):
        try:
            with open(file_name):
                pass
        except IOError:
            logger.error('Error: the file ' + file_name + ' could not be found.')

        self.input_file_name = file_name
        with open(file_name) as f:
            for line in f:
                li = line.strip().rstrip()
                li = re.sub(r'\s*#.*', '', li) #Remove comments
                if li:
                    li = li.split(' ', 1)
                    key = li[0].strip()
                    value = li[1].strip()
                    self.user_input_data[key] = value

    @staticmethod
    def print_valid_keywords():
        print('The following keywords can be used in the input file(separate keyword from value using space):')
    	print('grid_base_name: Name of the grid i.e. <name>.vog')
    	print('boundary_1: Name of boundary face that is not rotated on the pie slice')
    	print('boundary_2: Name of boundary face that IS rotated on the pie slice')
    	print('initial_wedge_angle: Angle of initial provided pie-slice sector that was generated')


def create_3d_grid(grid_base_name, boundary_1, boundary_2, initial_wedge_angle):
    """
    grid_base_name: Name of the grid i.e. <name>.vog
    boundary_1: Name of boundary face that is not rotated on the pie slice
    boundary_2: Name of boundary face that IS rotated on the pie slice
    initial_wedge_angle: Angle of initial provided pie-slice sector that was generated from AFLR2d
    """

    run_directory = os.getcwd()
    print('Running in Directory: ', run_directory)
    
    source_path = os.path.dirname(os.path.abspath(__file__))
    shell_script_path = source_path + '/program_operations.sh'
    print('Executing file: ', shell_script_path)
    
    rotation_angles = create_rotation_angles(initial_wedge_angle)
    for i, rotation_angle in enumerate(rotation_angles):
        if i == 0:
            #Rename the left and right boundaries to face1 and face2
            subprocess.call('%s %s %s %s %s' %(shell_script_path, grid_base_name, '0', boundary_1, boundary_2), shell=True)
            
            #Rotate the pie slice
            subprocess.call('%s %s %s %s' % (shell_script_path, grid_base_name, '1', str(rotation_angle)), shell=True)
            
            #Glue the two faces together
            subprocess.call('%s %s %s' % (shell_script_path, grid_base_name, '2'), shell=True)
        elif i == len(rotation_angles) - 1:
            #Rotate the pie slice
            subprocess.call('%s %s %s %s' % (shell_script_path, grid_base_name, '1', str(rotation_angle)), shell=True)

            #Glue the final two faces together
            subprocess.call('%s %s %s' % (shell_script_path, grid_base_name, '4'), shell=True)
        else:
            #Rotate the pie slice to the new position
            subprocess.call('%s %s %s %s' % (shell_script_path, grid_base_name, '1', str(rotation_angle)), shell=True)

            #Glue the touching faces together
            subprocess.call('%s %s %s' % (shell_script_path, grid_base_name, '3'), shell=True)

def create_rotation_angles(initial_wedge_angle):
    epsilon = 1e-6 #Threshold below which is called zero
    
    # Initial angle goes equally into 360 degrees
    a = 360.0 / initial_wedge_angle
    b = a % 1  #Get the decimal remainder from the division

    if abs(b) >= epsilon:
        sys.exit('Error: Grid wedge angle does not go evenly into 360 degrees. Check input, or make a new wedge')
    else:
        num_rotations = int(360.0 / initial_wedge_angle) - 1  #minus 1 because we start with the original pie slice
        print('Rotating pie slice of: ', initial_wedge_angle, ' degrees, ', num_rotations, ' times.')

    rotation_angles = []
    for i in range(num_rotations):
        rotation_angles.append(initial_wedge_angle * (i + 1))

    return rotation_angles



if len(sys.argv) < 2:
    print('Error: Must specify an input file.')
    InputFileParser().print_valid_keywords()
    sys.exit()
else:
    input_filename = sys.argv[1]

input_parser = InputFileParser(input_filename)

#Note: When rotating using the aflr tool to make an axisymmetric pie slice, the boundaries are numbered
#such that the original surface has the higher boundary marker number, and the newer surface that is
#created from the rotation has the lower number.

grid_base_name = input_parser.user_input_data['grid_base_name']
boundary_1 = input_parser.user_input_data['boundary_1']
boundary_2 = input_parser.user_input_data['boundary_2']
initial_wedge_angle = float(input_parser.user_input_data['initial_wedge_angle'])
create_3d_grid(grid_base_name, boundary_1, boundary_2, initial_wedge_angle)

print('\nFinished\n')

 
