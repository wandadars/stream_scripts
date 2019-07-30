#######################################################################################
# The purpose of this module is to collect a set of useful statistics functions that
# can be used to analyze lagrangian particle data.
#
# Author: Christopher Neal
#
# Date: 11-20-2015
# Updated: 07-21-2019
#
#######################################################################################
import logging
import numpy as np

logger = logging.getLogger(__name__)

def IQR(DataSet):
    #DataSet is the form of a 1D vector of information such as observations of an experiment
    q75, q25 = np.percentile(DataSet, [75 ,25])
    return q75 - q25

def compute_sauter_mean_diameter(particle_bin_cell, BinFlag):
    #Note that ParticleData is a 2D array of particle diameters & number of particles
    #Check to make sure that more than 1 entry exists, otherwise do nothing and tell user
    if particle_bin_cell.NumElements == 0:
        logger.info("No Particles in Bin. Nothing will be output for this data set")
        smd = 0 
        return smd 

    if BinFlag == 1:  #Use bins for the particle diameters
        particle_diameters = [float(entry) for entry in particle_bin_cell.ParticleDiameters]
        logger.debug(particle_diameters)
        #Freedman-Diaconis bin size estimation
        h = 2*IQR(particle_diameters)*particle_bin_cell.NumElements**(-1.0/3.0)

        logger.info("Diameter Bin size is: %10.2E"%(h))

        d_min = np.amin(particle_diameters)
        d_max   = np.amax(particle_diameters)
        logger.info("Minimum Particle Diameter: %10.2E"%(d_min))
        logger.info("Maximum Particle Diameter: %10.2E"%(d_max))
    

        num_bins = 1
        d_start = d_min
        all_bins_found = False
        while all_bins_found == False:
            d_start = d_start + h
            if d_start <= d_max:
                num_bins = num_bins + 1
            else:
                all_bins_found = True
    
        logger.info("Number of diameter bins is: %d"%(num_bins))

        #Create vector of particle diameter bin coordinates
        dia_bin_coords = np.zeros((2, num_bins))
        dia_bin_coords[0][0] = d_min
        dia_bin_coords[1][0] = d_min + h
        for i in range(1, num_bins):
            dia_bin_coords[0][i] = dia_bin_coords[1][i-1]
            dia_bin_coords[1][i] = dia_bin_coords[0][i] + h

        for i in range(0, num_bins):
            logger.info("Diameter Bin %d \t%10.2E\t%10.2E\n"%(i+1, dia_bin_coords[0][i], dia_bin_coords[1][i]))

        #Sort the particles into Bins
        dia_bins = np.zeros(num_bins)
        for i in range(0, particle_bin_cell.NumElements):
            for j in range(0, num_bins):
                if particle_diameters[i] <= dia_bin_coords[1][j] and particle_diameters[i] >= dia_bin_coords[0][j]:
                    dia_bins[j] = dia_bins[j] + 1
    
        logger.info("Bin Counts:\n"%(dia_bins))
        logger.info(dia_bins)
        logger.info("Sum of particles in bins: %d\n"%(np.sum(dia_bins)))

        #Now tha the bins are constructed we compute the Sauter mean diameter using the bins
        #we use the mean diameter in the bin as the representative value of the diameter for all particles in a bin.
        numerator = 0
        denominator = 0
        for i in range(0, num_bins):
            numerator = numerator + dia_bins[i]*( 0.5*( dia_bin_coords[1][i] + dia_bin_coords[0][i] ) )**3
            denominator = denominator + dia_bins[i]*( 0.5*( dia_bin_coords[1][i] + dia_bin_coords[0][i] ) )**2
        SMD = numerator/denominator

    elif BinFlag == 0: #do not use bins
        numerator = 0
        denominator = 0
        for i in range(0, particle_bin_cell.NumElements):
            numerator = numerator + float(particle_bin_cell.ParticlesPerParcel[i]) * (float(particle_bin_cell.ParticleDiameters[i])**3)
            denominator = denominator + float(particle_bin_cell.ParticlesPerParcel[i]) * (float(particle_bin_cell.ParticleDiameters[i])**2)
        SMD = numerator/denominator

    return SMD

