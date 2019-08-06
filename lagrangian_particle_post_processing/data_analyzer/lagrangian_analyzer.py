#! /usr/bin/env python

# Purpose:  Reads the output files from Loci-Stream and parses the contents to extract the
#       particle positions and diameters & averages over time to generate particle
#       diameter PDF plots.
#
#
# Input:    Base filename where particle data is stored.
#
# Output:   A data file containing the particle diameter PDF data for the positions and bin widths
#       specified.
#
#
#   Author: Christopher Neal
#   Date   : 11/20/2015
#   Updated: 05/11/2016
#
########################################################################
import logging
import os #OS specific commands forreading and writing files
import sys #For parsing user input to the script
import math
import numpy as np
import time #For deubbging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import particle_statistics
import particle_data_reader 
import particle_bins
import utilities
import input_parser as ip

logger = logging.getLogger(__name__)

class LagrangianParticleDataAnalyzer(object):
    def __init__(self, input_parser):
        self.user_input_data = input_parser.user_input_data
    
    def process_data(self):
        raise NotImplementedError

    def get_file_indices(self):
        try:
            i_start = int(self.user_input_data['i_start'])
        except KeyError:
            logger.error('i_start missing from input file. Needed for reading time series of files.')
            raise KeyError
        
        try:
            i_end = int(self.user_input_data['i_end'])
        except KeyError:
            logger.error('i_end missing from input file. Needed for reading time series of files.')
            raise KeyError
        
        try:
            i_step = int(self.user_input_data['i_step'])
        except KeyError:
            logger.error('i_step missing from input file. Needed for reading time series of files.')
            raise KeyError

        return utilities.compute_filename_numbers(i_start, i_end, i_step)

    def create_particle_bin_domain(self):
        try:
            x_min = float(self.user_input_data['x_min'])
        except KeyError:
            logger.error('x_min missing from input file. Needed to define x range for bins.')
            raise KeyError
        
        try:
            x_max = float(self.user_input_data['x_max'])
        except KeyError:
            logger.error('x_max missing from input file. Needed to define x range for bins.')
            raise KeyError
        
        try:
            num_x_bins = int(self.user_input_data['num_x_bins'])
        except KeyError:
            logger.error('num_x_bins missing from input file. Needed to define x range for bins.')
            raise KeyError
        
        try:
            y_min = float(self.user_input_data['y_min'])
        except KeyError:
            logger.error('y_min missing from input file. Needed to define y range for bins.')
            raise KeyError
        
        try:
            y_max = float(self.user_input_data['y_max'])
        except KeyError:
            logger.error('y_max missing from input file. Needed to define y range for bins.')
            raise KeyError
        
        try:
            num_y_bins = int(self.user_input_data['num_y_bins'])
        except KeyError:
            logger.error('num_y_bins missing from input file. Needed to define y range for bins.')
            raise KeyError

        return particle_bins.ParticleBinDomain(x_max, x_min, y_max, y_min, num_x_bins, num_y_bins)

    def create_hdf5_reader(self, time_stamp):
        try:
            script_path = self.user_input_data['script_path']
        except KeyError:
            logger.error('script_path missing from input file. Just a reference to the location of this script on the system(full path).')
            raise KeyError

        try:
            case_name = self.user_input_data['case_name']
        except KeyError:
            logger.error('case_name missing from input file. The prefix on the lagrangian files that signify the case name that generated them.')
            raise KeyError
        
        return particle_data_reader.HDF5ParticlePDFPlotterDataReader(case_name, time_stamp, script_path)

    def initialize_particle_data_structure(self):
        file_indices = self.get_file_indices()
        num_x_bins = self.particle_bin_domain.num_x_bins
        num_y_bins = self.particle_bin_domain.num_y_bins
        #Initialize 3D array of objects to hold particle data for all bins in each data file. Creates NumFiles x nXBins x nYBins array
        data = [[[particle_bins.ParticleBinCell() for k in range(num_y_bins)] for j in range(num_x_bins)] for i in range(len(file_indices))]
        """
        #Check to make sure data structure is initialized correctly
        count_i = 0
        count_j = 0
        count_k = 0
        for i in range(0, len(file_indices)):
           count_i += 1
           for j in range(0,num_x_bins):
               if i==0:
                   count_j += 1
               for k in range(0, num_y_bins):
                   if i==0 and j == 0:
                       count_k += 1
                   data[i][j][k].print_data()
        logger.debug(count_i, count_j, count_k)
        """
        return data

    def convert_particle_data_to_floating_point(self, particle_data):
        #Compute size of ParticleData 2D list
        numrows = len(particle_data)  
        numcols = len(particle_data[0])
        #Allocate a numpy array to store the floating point data & copy into array
        real_particle_data = np.zeros((numrows, numcols))
        for i in range(0, numrows):
            for j in range(0, numcols):
                real_particle_data[i][j] = float(particle_data[i][j])
        return real_particle_data

    def remap_particle_diameters_to_custom_bins(self, particle_data):
        logger.info("Re-Mapping Particle Diameter data to user-defined bins")
        user_defined_bins = self.compute_user_defined_bins()
        #Re-Bin all of the diameter data using the newly defined diameters
        for i in range(0, len(particle_data)):
            for j in range(0, len(particle_data[0])):
                particle_data[i][j].sort_particles_per_parcel()
                particle_data[i][j].custom_bins(user_defined_bins)
                particle_data[i][j].sort_diameters()

    def inplace_sort_particle_data_by_diameter(self, particle_data):
        logger.info("Performing a Sort on the particle diameter data to improve performance")
        #Sort diameter data in the data structure to speed up the merging process
        num_files = len(particle_data)
        num_x_bins = self.particle_bin_domain.num_x_bins 
        num_y_bins = self.particle_bin_domain.num_y_bins 
        for i in range(0, num_files):
            for j in range(0, num_x_bins):
                logger.info("\nSorting X Bin: %d"%(j + 1))
                for k in range(0, num_y_bins):
                    logger.info("\tSorting Y Bin: %d"%(k + 1))
                    particle_data[i][j][k].sort_diameters()
    
    def inplace_compression_of_particle_data(self, particle_data):
        logger.info("Performing a compression on the particle diameter data to improve performance")
        #Sort diameter data in the data structure to speed up the merging process
        num_files = len(particle_data)
        num_x_bins = self.particle_bin_domain.num_x_bins 
        num_y_bins = self.particle_bin_domain.num_y_bins 
        for i in range(0, num_files):
            for j in range(0, num_x_bins):
                logger.info("\nSorting X Bin: %d"%(j + 1))
                for k in range(0, num_y_bins):
                    logger.info("\tSorting Y Bin: %d"%(k + 1))
                    particle_data[i][j][k].compress_data()
    
    def inplace_merge_particle_data_over_all_files(self, particle_data):
        logger.info("Merging data over all files")
        num_files = len(particle_data)
        num_x_bins = self.particle_bin_domain.num_x_bins 
        num_y_bins = self.particle_bin_domain.num_y_bins
        #Compute a time averaged PDF by averaging over all time entries
        avg = [[particle_bins.ParticleBinCell() for j in range(num_y_bins) ]for i in range(num_x_bins)]
        for i in range(0, num_files):
            logger.info("Merging Data from File: %d"%(i + 1))
            for j in range(0, num_x_bins):
                logger.info("\tMerging X Bin: %d"%(j + 1))
                for k in range(0, num_y_bins):
                    logger.info("\t\tMerging Y Bin: %d"%(k + 1))
                    if i == 0:
                        avg[j][k] = particle_data[i][j][k]
                    else:
                        avg[j][k] =  avg[j][k] + particle_data[i][j][k]
                        #Sort and compress the new output
                        avg[j][k].sort_diameters()
            logger.info("Data file %d successfully merged\n"%(i+1))
        #Debugging 
        #for i in range(0, num_x_bins):
        #   for j in range(0, num_y_bins):
        #       avg[i][j].print_data()
        return avg
    
    def compute_user_defined_bins(self):
        """Compute the user defined bin coordinates"""
        try:
            d_max = float(self.user_input_data['d_max'])
        except KeyError:
            logger.error('d_max missing from input file. Maximum diameter for binning parcels.')
            raise KeyError
        
        try:
            d_min = float(self.user_input_data['d_min'])
        except KeyError:
            logger.error('d_min missing from input file. Minimum diameter for binning parcels.')
            raise KeyError
        
        try:
            num_dia_bins = int(self.user_input_data['num_dia_bins'])
        except KeyError:
            logger.error('num_dia_bins missing from input file. Number of parcel diameter bins to create.')
            raise KeyError

        #Store the Delta-D bin spacing
        delta_d = float(d_max - d_min) / float(num_dia_bins)
        logger.info("Using diameter bin width of: %10.6E"%(delta_d))
        logger.info("Bin #\t\tLeft Bin Coord\t\tRight Bin Coord")
        user_defined_bins = [{'d_min': str(d_min), 'd_max': str(d_min + delta_d)}]
        for i in range(0, num_dia_bins):
            entry = {'d_min': user_defined_bins[-1]['d_max'], 'd_max': str(float(user_defined_bins[-1]['d_max']) + delta_d)}
            user_defined_bins.append(entry)
            logger.info("%d\t\t%s\t\t\t%s"%(i + 1, user_defined_bins[i]['d_min'], user_defined_bins[i]['d_max']))
        return user_defined_bins


class LagrangianParticleSMDDataAnalyzer(LagrangianParticleDataAnalyzer):
    def __init__(self, input_parser):
        super(LagrangianParticleSMDDataAnalyzer, self).__init__(input_parser)
        self.particle_bin_domain = None

    def process_data(self):
        self.particle_bin_domain = self.create_particle_bin_domain()
        try:
            d_liq = float(self.user_input_data['d_liq'])
        except KeyError:
            logger.error('d_liq missing from input file. Needed to nondimensionalize data.')
            raise KeyError
            
        self.particle_bin_domain.print_x_bin_coords(d_liq)
        self.particle_bin_domain.print_y_bin_coords(d_liq)

        #Initialize 3D array of objects to hold particle data for all bins in each data file. Creates NumFiles x nXBins x nYBins array
        pdf_data = self.initialize_particle_data_structure() 
        file_indices = self.get_file_indices()
        for i, time_stamp in enumerate(file_indices):
            #Read particle data from HDF5 data files
            logger.info("Reading Data from file: %d"%(i + 1))
            hdf5_data_reader = self.create_hdf5_reader(time_stamp)
            particle_data = hdf5_data_reader.read_hdf_particle_data()
            logger.info("Number of parcels in dataset %d :\t%d"%(i + 1, len(particle_data)))
            real_particle_data = self.convert_particle_data_to_floating_point(particle_data) 

            #Store particle radius in the y and z positions of the data array
            try:
                radial_bin_flag = int(self.user_input_data['radial_bin_flag'])
            except KeyError:
                logger.error('radial_bin_flag missing from input file. 0 for cartesian y bins, 1 for cylindrical R bins. If 1, treats y variable as r in code. Defaulting to 0 .')
                radial_bin_flag = 0
            
            if radial_bin_flag == 1:
                for k in range(0, len(particle_data)):
                    real_particle_data[k][2] = math.sqrt(real_particle_data[k][2]**2 + real_particle_data[k][3]**2)
                    real_particle_data[k][3] = real_particle_data[k][2]

            #Loop over all bins and store data about particles within the bin
            x_bin_coords = self.particle_bin_domain.compute_x_bin_coords() 
            y_bin_coords = self.particle_bin_domain.compute_y_bin_coords()
            
            #Loop over Y bins & sweep over the X bins and store particle information
            logger.info("Counting Particles for File: %d"%(i + 1))
            num_parcels = len(particle_data)
            num_x_bins = self.particle_bin_domain.num_x_bins 
            num_y_bins = self.particle_bin_domain.num_y_bins
            for j in range(0, num_x_bins):
                logger.info("Placing parcels into X-bin:\t%d"%(j + 1))
                for k in range(0, num_y_bins):
                    logger.info("\tPlacing parcels into Y-bin:\t%d"%(k + 1))
                    parcels_in_bin = 0
                    for m in range(0, num_parcels):  #Loop over all parcels to find which are in the current bin
                        if real_particle_data[m][1] < x_bin_coords[1][j] and real_particle_data[m][1] >= x_bin_coords[0][j] and real_particle_data[m][2] < y_bin_coords[1][k] and real_particle_data[m][2] >= y_bin_coords[0][k]:
                                #logger.debug("i = %d\tj = %d\tk = %d\n"%(i+1,m+1,k+1))
                                pdf_data[i][j][k].add_data(particle_data[m][0], particle_data[m][4])
                                parcels_in_bin += 1
                    logger.info("\t\tNumber of Parcels in X Bin(%d) & Y Bin(%d) is:\t %d"%(j + 1, k + 1, parcels_in_bin))
                    

        self.inplace_sort_particle_data_by_diameter(pdf_data)
        self.inplace_compression_of_particle_data(pdf_data)
        avg_pdf = self.inplace_merge_particle_data_over_all_files(pdf_data)
        
        try:
            diameter_bin_flag = int(self.user_input_data['diameter_bin_flag'])
        except KeyError:
            logger.error('diameter_bin_flag missing from input file. #1 for using diameter bins and 0 for no diameter bins. Defaulting to 0 .')
            diameter_bin_flag = 0
        
        if diameter_bin_flag == 1: #Use the user defined bins
            self.remap_particle_diameters_to_custom_bins(avg_pdf)
        self.write_output(diameter_bin_flag, avg_pdf)
        logger.info("\n Program has finished... \n")

    def compute_sauter_mean_diameter(self, avg_pdf, bin_flag):
        num_x_bins = self.particle_bin_domain.num_x_bins
        num_y_bins = self.particle_bin_domain.num_y_bins
        smd = np.zeros((num_x_bins, num_y_bins))
        smd_calculator_factory = particle_statistics.SauterMeanDiameterCalculatorFactory(bin_flag)
        smd_calculator = smd_calculator_factory.get_sauter_mean_diameter_class()
        for i in range(num_x_bins):
            for j in range(num_y_bins):
                smd[i][j] = smd_calculator.compute_sauter_mean_diameter(avg_pdf[i][j])
        return smd

    def write_output(self, BinFlag, avg_pdf):
        logger.info("Writing Output Data")

        #Create output directory and enter the directory
        file_base_path = os.getcwd()
        output_dir = file_base_path + '/particle_smd_data'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.chdir(output_dir)
        else:
            os.chdir(output_dir)
        
        self.write_smd_data()

    def write_smd_data(self):
        try:
            case_name = self.user_input_data['case_name']
        except KeyError:
            logger.error('case_name missing from input file. The prefix on the lagrangian files that signify the case name that generated them.')
            raise KeyError
        
        try:
            d_liq = float(self.user_input_data['d_liq'])
        except KeyError:
            logger.error('d_liq missing from input file. Needed to nondimensionalize data.')
            raise KeyError
        #Write the Average SMD to a file of the same basename as the particle data file
        pdf_x_coords = self.particle_bin_domain.compute_x_bin_center_coords() 
        pdf_y_coords = self.particle_bin_domain.compute_y_bin_center_coords()
        num_x_bins = self.particle_bin_domain.num_x_bins
        num_y_bins = self.particle_bin_domain.num_y_bins
        smd = self.compute_sauter_mean_diameter(avg_pdf, BinFlag)
        for m in range(0, num_y_bins):
            output_file_name = case_name + "_SMD_" + '%s_%4.2f_Data'%('Y', pdf_y_coords[m] / d_liq) + ".txt"
            f_output = open(output_file_name,"w")
            for k in range(0, num_x_bins):
                f_output.write("%10.6E\t"%(pdf_x_coords[k]))
                f_output.write("%10.6E\t"%(smd[k][m]))
                f_output.write("\n\n")
            f_output.close()

        self.write_smd_plots(smd_data)

    def write_smd_plots(self, smd_data):
        try:
            case_name = self.user_input_data['case_name']
        except KeyError:
            logger.error('case_name missing from input file. The prefix on the lagrangian files that signify the case name that generated them.')
            raise KeyError
        
        try:
            d_liq = float(self.user_input_data['d_liq'])
        except KeyError:
            logger.error('d_liq missing from input file. Needed to nondimensionalize data.')
            raise KeyError
        #Write the Average SMD to a file of the same basename as the particle data file
        pdf_x_coords = self.particle_bin_domain.compute_x_bin_center_coords() 
        pdf_y_coords = self.particle_bin_domain.compute_y_bin_center_coords()
        num_x_bins = self.particle_bin_domain.num_x_bins
        num_y_bins = self.particle_bin_domain.num_y_bins
        
        #Create output directory and enter the directory
        file_path_base = os.getcwd()
        output_dir = file_path_base + "/SMDPlots"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.chdir(output_dir)
        else:
            os.chdir(output_dir)

        #Plot SMD variable over space
        DiameterFactor = 1e6 #For expressing diameters in micrometers
        for m in range(0, num_y_bins):
            #Find the maximum value of the variable about to be plotted so that the 
            #plot vertical axis can be scaled appropriately
            max_val = np.amax(smd_data[:,m]) * DiameterFactor
            min_val = np.amin(smd_data[:,m]) * DiameterFactor

            #Change the min and max values a little bit so that all data lies within the bounds of the plots
            max_val = max_val + 0.05*abs(max_val)
            min_val = min_val - 0.05*abs(min_val)

            plt.plot(pdf_x_coords / d_liq, smd_data[:, m] * DiameterFactor, marker='o')
            plt.xlabel('Non-Dimensional X Coordinate (X/DL)')
            plt.ylabel('Sauter Mean Diameter D32(micrometers)')
            plt.ylim([min_val, max_val])

            output_file_name = case_name + "_SMD_" + '%s%4.2f'%('Y',pdf_y_coords[m] / d_liq) + ".png"
            logger.info("Saving a figure to:%s\n"%(output_file_name))
            plt.savefig(output_file_name, bbox_inches='tight')
            plt.close()

        #Go back to the original data directory
        os.chdir("..")



class LagrangianParticlePDFDataAnalyzer(LagrangianParticleDataAnalyzer):
    def __init__(self, input_parser):
        super(LagrangianParticlePDFDataAnalyzer, self).__init__(input_parser)
        self.particle_bin_domain = None

    def process_data(self):
        self.particle_bin_domain = self.create_particle_bin_domain()
        try:
            d_liq = float(self.user_input_data['d_liq'])
        except KeyError:
            logger.error('d_liq missing from input file. Needed to nondimensionalize data.')
            raise KeyError

        self.particle_bin_domain.print_x_bin_coords(d_liq)
        self.particle_bin_domain.print_y_bin_coords(d_liq)

        #Initialize 3D array of objects to hold particle data for all bins in each data file. Creates NumFiles x nXBins x nYBins array
        pdf_data = self.initialize_particle_data_structure() 
        file_indices = self.get_file_indices()
        for i, time_stamp in enumerate(file_indices):
            #Read particle data from HDF5 data files
            logger.info("Reading Data from file: %d"%(i + 1))
            hdf5_data_reader = self.create_hdf5_reader(time_stamp)
            particle_data = hdf5_data_reader.read_hdf_particle_data()
            logger.info("Number of parcels in dataset %d :\t%d"%(i + 1, len(particle_data)))
            
            real_particle_data = self.convert_particle_data_to_floating_point(particle_data) 

            #Store particle radius in the y and z positions of the data array
            try:
                radial_bin_flag = int(self.user_input_data['radial_bin_flag'])
            except KeyError:
                logger.error('radial_bin_flag missing from input file. 0 for cartesian y bins, 1 for cylindrical R bins. If 1, treats y variable as r in code. Defaulting to 0 .')
                radial_bin_flag = 0
            
            if radial_bin_flag == 1:
                for k in range(0, len(particle_data)):
                    real_particle_data[k][2] = math.sqrt(real_particle_data[k][2]**2 + real_particle_data[k][3]**2)
                    real_particle_data[k][3] = real_particle_data[k][2]

            #Loop over all bins and store data about particles within the bin
            x_bin_coords = self.particle_bin_domain.compute_x_bin_coords() 
            y_bin_coords = self.particle_bin_domain.compute_y_bin_coords()
            
            #Loop over Y bins & sweep over the X bins and store particle information
            logger.info("Counting Particles for File: %d"%(i + 1))
            num_parcels = len(particle_data)
            num_x_bins = self.particle_bin_domain.num_x_bins 
            num_y_bins = self.particle_bin_domain.num_y_bins
            for j in range(0, num_x_bins):
                logger.info("Placing parcels into X-bin:\t%d"%(j + 1))
                for k in range(0, num_y_bins):
                    logger.info("\tPlacing parcels into Y-bin:\t%d"%(k + 1))
                    parcels_in_bin = 0
                    for m in range(0, num_parcels):  #Loop over all parcels to find which are in the current bin
                        if real_particle_data[m][1] < x_bin_coords[1][j] and real_particle_data[m][1] >= x_bin_coords[0][j] and real_particle_data[m][2] < y_bin_coords[1][k] and real_particle_data[m][2] >= y_bin_coords[0][k]:
                                #logger.debug("i = %d\tj = %d\tk = %d\n"%(i+1,m+1,k+1))
                                pdf_data[i][j][k].add_data(particle_data[m][0], particle_data[m][4])
                                parcels_in_bin += 1
                    logger.info("\t\tNumber of Parcels in X Bin(%d) & Y Bin(%d) is:\t %d"%(j + 1, k + 1, parcels_in_bin))
                    

        self.inplace_sort_particle_data_by_diameter(pdf_data)
        avg_pdf = self.inplace_merge_particle_data_over_all_files(pdf_data)
        
        try:
            diameter_bin_flag = int(self.user_input_data['diameter_bin_flag'])
        except KeyError:
            logger.error('diameter_bin_flag missing from input file. #1 for using diameter bins and 0 for no diameter bins. Defaulting to 0 .')
            diameter_bin_flag = 0
        
        if diameter_bin_flag == 1: #Use the user defined bins
            self.remap_particle_diameters_to_custom_bins(avg_pdf)
        self.write_output(diameter_bin_flag, avg_pdf)
        logger.info("\n Program has finished... \n")

    def write_output(self, BinFlag, avg_pdf):
        logger.info("Writing Output Data")
        #Create output directory and enter the directory
        file_base_path = os.getcwd()
        output_dir = file_base_path + '/particle_PDF_data'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.chdir(output_dir)
        else:
            os.chdir(output_dir)

        try:
            case_name = self.user_input_data['case_name']
        except KeyError:
            logger.error('case_name missing from input file. The prefix on the lagrangian files that signify the case name that generated them.')
            raise KeyError
        
        #Write the output so that all of the Y data for a particular X bin is contained within 1 file. The file will match in essence the
        #format used for the experimental data file so that post-processing the data will be made faster.
        pdf_x_coords = self.particle_bin_domain.compute_x_bin_center_coords() 
        pdf_y_coords = self.particle_bin_domain.compute_y_bin_center_coords()
        try:
            d_liq = float(self.user_input_data['d_liq'])
        except KeyError:
            logger.error('d_liq missing from input file. Needed to nondimensionalize data.')
            raise KeyError
        for i in range(0, len(pdf_x_coords)):
            logger.info("Writing data for X bin %d  located at: %4.2f "%(i + 1, pdf_x_coords[i]))

            output_filename = case_name + "_PDF_" + '%s_%4.2f_Data'%('XOverD', pdf_x_coords[i] / d_liq) + ".txt"
            f_output = open(output_filename, "w")

            f_output.write("%s\t%s %10.6E\n"%("X Coordinate", "X/D = ", pdf_x_coords[i] / d_liq))
            
            f_output.write("\n")
            f_output.write("\n")
            f_output.write("\n")
            f_output.write("\n")
            
            f_output.write("%s\t%s\t"%("Radial Coordinate", "r/D = ") )
            
            for j in range(0, len(pdf_y_coords)):
                f_output.write("%10.6E\t"%(pdf_y_coords[j] / d_liq))

            f_output.write("\n")
            f_output.write("\n")
            f_output.write("\n")
            f_output.write("\n")    

            if BinFlag == 1:
                try:
                    num_dia_bins = int(self.user_input_data['num_dia_bins'])
                except KeyError:
                    logger.error('num_dia_bins missing from input file. Number of parcel diameter bins to create.')
                    raise KeyError

                user_defined_bins = self.compute_user_defined_bins()
                num_y_bins = self.particle_bin_domain.num_y_bins
                for m in range(0, num_dia_bins):
                    f_output.write("%10.6E\t"%( 0.5*(float(user_defined_bins[m]['d_min']) + float(user_defined_bins[m]['d_max']))))
                    for j in range(0, num_y_bins):   #used to be nYBins
                        #logger.debug("\tWriting data for Transverse bin ",j+1," located at: ",PDF_Y_Coords[j])
                        f_output.write("%10.6E\t"%( float(avg_pdf[i][j].ParticlesPerParcel[m]) ))
                    f_output.write("\n")
                    f_output.write("\n")
            f_output.close()



        #####Plot output data##########
        #Create output directory and enter the directory
        file_path_base =os.getcwd()
        output_dir = file_path_base +"/PDFPlots"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            os.chdir(output_dir)
        else:
            os.chdir(output_dir)


        #Plot PDF variable over diameter space. That is, for a given x value, make plots of D Versus N at the different values of the radial coordinate.
        DiameterFactor = 1e6

        #Plot data about radial distribution of particles at each X coordinate
        num_x_bins = self.particle_bin_domain.num_x_bins
        num_y_bins = self.particle_bin_domain.num_y_bins
        for i in range(0, num_x_bins):
            for j in range(0, num_y_bins):
                #Find the maximum value of the variable about to be plotted so that the 
                #plot vertical axis can be scaled appropriately
                MaxVal = 0
                MinVal = 0
                for k, parcel in enumerate(avg_pdf[i][j].parcels):
                    if k == 0:
                        MaxVal = float(parcel['particles_per_parcel'])
                        MinVal = float(parcel['particles_per_parcel'])
                    elif float(parcel['particles_per_parcel']) > MaxVal:
                        MaxVal = float(parcel['particles_per_parcel'])
                    elif float(parcel['particles_per_parcel']) < MinVal:
                        MinVal = float(parcel['particles_per_parcel'])
                        
                #Change the min and max values a little bit so that all data lies within the bounds of the plots
                MaxVal = MaxVal + 0.05*abs(MaxVal)
                MinVal = MinVal - 0.05*abs(MinVal)

                xValues = np.asarray([parcel['diameter'] for parcel in avg_pdf[i][j].parcels])
                for m in range(0, avg_pdf[i][j].num_parcels):
                    xValues[m] = float(xValues[m]) * float(DiameterFactor)
                
                yValues = np.asarray([parcel['particles_per_parcel'] for parcel in avg_pdf[i][j].parcels])

                plt.plot(xValues,yValues, marker='o', linestyle='None')
                plt.xlabel('Parcel Diameter, D micrometer')
                plt.ylabel('Parcel Count, N')
                plt.ylim([MinVal, MaxVal])

                try:
                    radial_bin_flag = int(self.user_input_data['radial_bin_flag'])
                except KeyError:
                    logger.error('radial_bin_flag missing from input file. 0 for cartesian y bins, 1 for cylindrical R bins. If 1, treats y variable as r in code. Defaulting to 0 .')
                    radial_bin_flag = 0
                
                if radial_bin_flag == 1:
                    dimension_name = 'R'
                else:
                    dimension_name = 'Y'

                outputFileName = case_name + '_PDF_' + '%s%4.2f%s'%('XoverD', pdf_x_coords[i] / d_liq,'_') + '%soverD%4.2f'%(dimension_name, pdf_y_coords[j] / d_liq) + ".png"
                logger.info("Saving a figure to:%s\n"%(outputFileName))
                plt.savefig(outputFileName, bbox_inches='tight')
                plt.close()


        #Go back to the original data directory
        os.chdir("../..")





