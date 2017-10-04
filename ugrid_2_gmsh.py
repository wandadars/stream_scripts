#! /usr/bin/env python

# Purpose:	Reads a *.ugrid file in the 2D format, and writes out
#               a 2D GMESH formatted .msh file 
#		unique boundary markers. 
#
# Input: 	Name of the UGRID file 
#
# Output: 	A print out of the unique boundary makers in the gird 
#
#	Author: Christopher Neal
#	Date   : 10/03/2017
#	Updated: 09/27/2016
#
########################################################################

import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import time
from collections import namedtuple

class ugrid_2d_mesh(object):

    def __init__(self,input_file_name):

        self.ugrid_filename = ''
        self.num_nodes = 0
        self.num_trias = 0
        self.num_quads = 0
        self.num_edges = 0
        self.nodes = []
        self.tri_elements = []
        self.quad_elements = []
        self.boundary_edges = []
        self.boundary_markers=[]

        self.tags_present = False
        self.tags = {}

        self.read_ugrid_file(input_file_name)

    def add_node(self,node):
        self.nodes.append(node)
    
    def add_tri_element(self,element):
        self.tri_elements.append(element)

    def add_quad_element(self,element):
        self.quad_elements.append(element)
    
    def add_boundary_edge(self,edge):
        self.boundary_edges.append(edge)

    def read_tags_file(self):

        input_tags_filename = self.ugrid_filename.replace('.ugrid','') + '.tags'
        try:
          f=open(input_tags_filename,"r")
          print("Reading boundary tag data from: %s\n"%(input_tags_filename))
        except:
          print("No .tags file detected")
          return False

        for line in f:
            if '#' not in line:
                boundary_line = line.rstrip()
                boundary_line = boundary_line.split()
                self.tags[int(boundary_line[0])] = boundary_line[1]

        f.close()
        self.tags_present = True

    def read_ugrid_file(self,file_name):
        
        #Test to see if the file exists, otherwise throw exception
        try:
          os.path.isfile(input_file_name)
          print("Reading Data From: %s\n"%(input_file_name))
        except IOError as e:
          print "I/O error({0}): {1}".format(e.errno, e.strerror)
          raise

        #open file if file exists, otherwise throw exception
        try:
          f=open(input_file_name,"r")
        except IOError as e:
          print "I/O error({0}): {1}".format(e.errno, e.strerror)
          raise
    
        self.ugrid_filename = file_name 

        #Loop through entire file
        #Data in the file is structured in the following way:
        # See description at: http://www.simcenter.msstate.edu/software/downloads/doc/ug_io/2d_grid_file_type_ugrid.html

        line_count = 0
        #Read file header
        lines = f.readline()
        line = lines.rstrip()
        line = line.split()
                        
        num_nodes = int( line[0] )
        num_trias = int( line[1] )
        num_quads = int( line[2] )
        line_count = line_count + 1
        
        self.num_nodes = num_nodes
        self.num_trias = num_trias
        self.num_quads = num_quads

        self.print_grid_report()

        #loop over the node data
        print "Reading Node Data..."
        vertex = namedtuple("vertex", "id x y z")
        Done = False
        count = 1
        while Done == False:
                lines = f.readline()
                line = lines.rstrip()
                line = line.split()
                line_count = line_count + 1
                temp_vertex = vertex(count,x=line[0],y=line[1],z=line[2])
                self.add_node(temp_vertex)
                count = count + 1
                if line_count > num_nodes : 
                        Done = True


        #loop over the connectivity data
        print "Skimming Connectivity Data..."
        tri_element = namedtuple("triangle", "v1 v2 v3")
        while True:     #Triangle faces loop
          lines = f.readline()
          line = lines.rstrip()
          line = line.split()
          line_count = line_count + 1
          temp_tri = tri_element(v1=line[0], v2=line[1], v3=line[2])
          self.add_tri_element(temp_tri)
          if line_count > num_nodes + num_trias:
            break

        quad_element = namedtuple("quadrilateral", "v1 v2 v3 v4")
        while True:     #Quadrilateral faces loop
          lines = f.readline()
          line = lines.rstrip()
          line = line.split()
          line_count = line_count + 1
          temp_quad = quad_element(v1=line[0], v2=line[1], v3=line[2], v4=line[3])
          self.add_quad_element(temp_quad)
          if line_count > num_nodes + num_trias + num_quads:
            break

        #Skip over face markers
        for i in range(self.num_trias + self.num_quads):
          lines = f.readline()
          line = lines.rstrip()
          line = line.split()

        #loop over the node data, but don't store
        print "Collecting All Boundary Face Markers..."
        line = f.readline()
        line = line.rstrip()
        line = line.split()
        num_edges = int(line[0])
        self.num_edges = num_edges
        boundary_edge = namedtuple("boundary_edge", "v1 v2 marker")
        for i in range(num_edges):
          lines = f.readline()
          line = lines.rstrip()
          line = line.split()
          tmp_boundary_edge = boundary_edge(v1=line[0], v2=line[1], marker=int(line[2]))
          self.add_boundary_edge(tmp_boundary_edge)

        f.close()

        #Collect only the most unique boundary markers
        self.boundary_markers = sorted(list(set([line[-1] for line in self.boundary_edges])))

        #Print the unique boundary marker ids
        print 'Unique Boundary Markers are: ',self.boundary_markers

        self.read_tags_file()


    def print_grid_report(self):
        print "Detected Info In 2D UGRID File:"
        print "Number of Nodes: ", self.num_nodes
        print "Number of Surface Triangle Elements: ", self.num_trias
        print "Number of Surface Quadrilateral Elements: ", self.num_quads



    def write_gmsh_file(self):
        output_file_name = input_file_name.replace('.ugrid','') + '.msh'
        #open file, otherwise throw exception
        try:
            f=open(output_file_name,"w")
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            raise

        f.write('$MeshFormat\n')
        f.write('2.2 0 8 \n')
        f.write('$EndMeshFormat\n')

        f.write('$PhysicalNames\n')
        if self.tags_present == True:
            for marker in self.boundary_markers:
                f.write('1 ' + str(marker) + ' ' + str(self.tags[marker]) +' \n')
        else:
            for i, marker in enumerate(self.boundary_markers):
                f.write('1 ' + str(marker) + ' BC' + str(i+1) + ' \n')

        if self.num_trias > 0:
            f.write('2 ' + str(max(self.boundary_markers) + 1) + ' Interior \n')
        if self.num_quads > 0:
            f.write('3 ' + str(max(self.boundary_markers) + 1) + ' Interior \n')

        f.write('$EndPhysicalNames\n')

        f.write('$Nodes\n')
        f.write(str(ugrid_mesh.num_nodes) + '\n')
        for node in ugrid_mesh.nodes:
            f.write(str(node[0]) + ' ' + " ".join(node[1:]) + '\n')

        f.write('$EndNodes \n')

        f.write('$Elements \n')
        f.write(str(self.num_trias + self.num_quads + self.num_edges)+ ' \n')
        
        count = 1
        for edge in self.boundary_edges:
            f.write(str(count) + ' 1 2 ' + str(edge[-1]) + ' 1 ' + " ".join(edge[:-1]) + ' \n')
            count += 1

        for element in self.tri_elements:
            f.write(str(count) + ' 2 2 ' + str(max(self.boundary_markers) + 1) + ' 1 ' + " ".join(element[:]) + ' \n')
            count += 1
        
        for element in self.quad_elements:
            f.write(str(count) + ' 3 2 ' + str(max(self.boundary_markers) + 1) + ' 1 ' + " ".join(element[:]) + ' \n')
            count += 1
    
        f.write('$EndElements \n')

#Store the name of the file that the user wants to translate.
input_file_name = str(sys.argv[1])
input_case_name = input_file_name.replace('.ugrid','')

ugrid_mesh = ugrid_2d_mesh(input_file_name)


#Write GMSH file
ugrid_mesh.write_gmsh_file()
print("\n Program has finished... \n")

