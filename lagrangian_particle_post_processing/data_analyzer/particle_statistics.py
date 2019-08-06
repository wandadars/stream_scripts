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


class SauterMeanDiameterCalculatorFactory(object):
    def __init__(self, bin_flag):
        self.bin_flag = bin_flag

    def get_sauter_mean_diameter_class(self):
        if self.bin_flag == 0: #No diameter bins
            logger.debug('Sauter Mean Diameter being computed with no diameter bins')
            return SauterMeanDiameterCalculatorNoBins()
        if self.bin_flag == 1: #Use diameter bins to compute sauter mean diameter
            logger.debug('Sauter Mean Diameter being computed with diameter bins')
            return SauterMeanDiameterCalculatorDiameterBins()


class SauterMeanDiameterCalculator(object):
    def __init__(self):
        pass

    def compute_sauter_mean_diameter(self, particle_bin_cell):
        raise NotImplementedError
    
    def IQR(self, data):
        """
        data is the form of a list of information such as observations of an experiment.
        """
        q75, q25 = np.percentile(data, [75 ,25])
        return q75 - q25


class SauterMeanDiameterCalculatorNoBins(SauterMeanDiameterCalculator):
    def __init__(self):
        super(SauterMeanDiameterCalculatorNoBins, self).__init__()
    
    def compute_sauter_mean_diameter(self, particle_bin_cell):
        if particle_bin_cell.num_parcels == 0:
            logger.debug("No Particles in Bin. Nothing will be output for this data set")
            smd = 0 
            return smd 
        
        numerator = 0
        denominator = 0
        for parcel in particle_bin_cell.parcels:
            numerator += float(parcel['particles_per_parcel']) * (float(parcel['diameter'])**3)
            denominator += float(parcel['particles_per_parcel']) * (float(parcel['diameter'])**2)
        
        smd = numerator/denominator
        return smd

class SauterMeanDiameterCalculatorDiameterBins(SauterMeanDiameterCalculator):
    def __init__(self):
        super(SauterMeanDiameterCalculatorDiameterBins, self).__init__()
        
    def compute_diameter_bins(self, diameters):
        """
        Takes in a list of diameters and returns a list of bin
        min and max coordinates for creating a histogram of
        the diameter data.
        """
        #Freedman-Diaconis bin size estimation
        h = 2 * self.IQR(diameters) * len(diameters)**(-1.0/3.0)
        logger.debug("Diameter Bin size(based on %d samples) is: %10.2E"%(len(diameters), h))

        d_min = np.amin(diameters)
        d_max = np.amax(diameters)
        logger.debug("Minimum Particle Diameter: %10.2E"%(d_min))
        logger.debug("Maximum Particle Diameter: %10.2E"%(d_max))
    

        num_bins = 1
        d_bins = [d_min]
        d_start = d_min
        all_bins_found = False
        while all_bins_found == False:
            d_bins.append(d_bins[-1] + h)
            if d_bins[-1] <= d_max:
                num_bins += 1
            else:
                all_bins_found = True
        logger.debug("Number of diameter bins is: %d"%(num_bins))

        #Create vector of particle diameter bin coordinates
        bin_coords = [{'d_min': d_min, 'd_max': d_min + h}]
        for i in range(1, num_bins):
            entry = {'d_min': bin_coords[-1]['d_max'] , 'd_max': bin_coords[-1]['d_max'] + h}
            bin_coords.append(entry) 

        for i, bin_coord in enumerate(bin_coords):
            logger.debug("Diameter Bin %d \t%10.2E\t%10.2E\n"%(i + 1, bin_coord['d_min'], bin_coord['d_max']))
        
        return bin_coords
        
    def compute_sauter_mean_diameter(self, particle_bin_cell):
        if particle_bin_cell.num_parcels == 0:
            logger.debug("No Particles in Bin. Nothing will be output for this data set")
            smd = 0 
            return smd 
        
        particle_diameters = [float(parcel['diameter']) for parcel in particle_bin_cell.parcels]
        logger.debug('Parcel Diameters')
        logger.debug(particle_diameters)
        diameter_bin_coords = self.compute_diameter_bins(particle_diameters)

        #Sort the particles into Bins
        logger.debug('Sorting parcels into diameter bins')
        dia_bin_counts = np.zeros(len(diameter_bin_coords))
        for parcel in particle_bin_cell.parcels:
            for i, dia_bin in enumerate(diameter_bin_coords):
                if float(parcel['diameter'])  <= dia_bin['d_max'] and float(parcel['diameter']) >= dia_bin['d_min']:
                    dia_bin_counts[i] += 1
    
        logger.debug("Bin Counts:")
        logger.debug(dia_bin_counts)
        logger.debug("Sum of particles in bins: %d\n"%(np.sum(dia_bin_counts)))

        #Now tha the bins are constructed we compute the Sauter mean diameter using the bins
        #we use the mean diameter in the bin as the representative value of the diameter for all particles in a bin.
        numerator = 0
        denominator = 0
        for i, dia_bin in enumerate(diameter_bin_coords):
            numerator +=  dia_bin_counts[i] * (0.5 * (dia_bin['d_max'] + dia_bin['d_min']))**3
            denominator +=  dia_bin_counts[i] * (0.5 * (dia_bin['d_max'] + dia_bin['d_min']))**2
        smd = numerator/denominator
        
        return smd

