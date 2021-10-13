import logging
import time
from operator import itemgetter
import numpy as np

logger = logging.getLogger(__name__)


class ParticleBinDomain:
    """A class to represent the spatial domain over which parcel data is collected."""
    def __init__(self, x_max=1, x_min=0, y_max=1, y_min=0, num_x_bins=1, num_y_bins=1):
        self.x_max = x_max
        self.x_min = x_min
        self.y_max = y_max
        self.y_min = y_min
        self.num_x_bins = num_x_bins
        self.num_y_bins = num_y_bins

    def compute_dx(self):
        return (self.x_max - self.x_min) / self.num_x_bins

    def compute_dy(self):
        return (self.y_max - self.y_min) / self.num_y_bins

    def compute_x_bin_coords(self):
        x_bin_coords = np.zeros((2, self.num_x_bins))
        x_bin_coords[0][0] = self.x_min
        x_bin_coords[1][0] = self.x_min + (1.0/2.0)*self.compute_dx()
        for i in range(1,self.num_x_bins):
            if i == self.num_x_bins - 1:
                x_bin_coords[0][i] = x_bin_coords[1][i-1]
                x_bin_coords[1][i] = x_bin_coords[0][i] + (1.0/2.0)*self.compute_dx()
            else:
                x_bin_coords[0][i] = x_bin_coords[1][i-1]
                x_bin_coords[1][i] = x_bin_coords[0][i] + self.compute_dx()
        return x_bin_coords

    def print_x_bin_coords(self, non_dimensional_factor=None):
        x_bin_coords = self.compute_x_bin_coords()
        logger.debug("\n\nX Bin Coordinates are:")
        table_header = "{:<11} {:<15} {:<15}{:<10}".format('Bin #','Min','Max','Center')
        if non_dimensional_factor is not None:
            table_header = "{}\t{:<}".format(table_header,'Non-Dimensional Center')
        logger.debug(table_header)

        for i in range(0, self.num_x_bins):
            center_coord = (x_bin_coords[0][i] + x_bin_coords[1][i]) / 2.0
            if non_dimensional_factor is None:
                logger.debug("  %d \t%10.2E\t%10.2E\t%10.2E"%(i+1, x_bin_coords[0][i], x_bin_coords[1][i], center_coord))
            else:
                logger.debug("  %d \t%10.2E\t%10.2E\t%10.2E\t    %8.6f"%(i+1, x_bin_coords[0][i], x_bin_coords[1][i], center_coord, center_coord/non_dimensional_factor))

    def compute_x_bin_center_coords(self):
        center_x_coords = np.zeros(self.num_x_bins)
        x_bin_coords = self.compute_x_bin_coords()
        for j in range(0,self.num_x_bins):
            center_x_coords[j] =  0.5*( x_bin_coords[1][j] + x_bin_coords[0][j] )  #Between edges of a bin
        return center_x_coords

    def compute_y_bin_coords(self):
        y_bin_coords = np.zeros((2, self.num_y_bins))
        y_bin_coords[0][0] = self.y_min
        y_bin_coords[1][0] = self.y_min + (1.0/2.0)*self.compute_dy()
        for i in range(1,self.num_y_bins):
            if i == self.num_y_bins-1:
                y_bin_coords[0][i] = y_bin_coords[1][i-1]
                y_bin_coords[1][i] = y_bin_coords[0][i] + (1.0/2.0)*self.compute_dy()
            else:
                y_bin_coords[0][i] = y_bin_coords[1][i-1]
                y_bin_coords[1][i] = y_bin_coords[0][i] + self.compute_dy()
        return y_bin_coords

    def print_y_bin_coords(self, non_dimensional_factor=None):
        y_bin_coords = self.compute_y_bin_coords()
        logger.debug("\n\nY Bin Coordinates are:")
        table_header = "{:<11} {:<15} {:<15}{:<10}".format('Bin #','Min','Max','Center')
        if non_dimensional_factor is not None:
            table_header = "{}\t{:<}".format(table_header,'Non-Dimensional Center')
        logger.debug(table_header)

        for i in range(0,self.num_y_bins):
            center_coord = (y_bin_coords[0][i] + y_bin_coords[1][i])/2.0
            if non_dimensional_factor is None:
                logger.debug("  %d \t%10.2E\t%10.2E\t%10.2E"%(i+1,y_bin_coords[0][i],y_bin_coords[1][i],center_coord))
            else:
                logger.debug("  %d \t%10.2E\t%10.2E\t%10.2E\t    %8.6f"%(i+1,y_bin_coords[0][i],y_bin_coords[1][i],center_coord,center_coord/non_dimensional_factor))

    def compute_y_bin_center_coords(self):
        center_y_coords = np.zeros(self.num_y_bins)
        y_bin_coords = self.compute_y_bin_coords()
        for j in range(0, self.num_y_bins):
            center_y_coords[j] =  0.5*( y_bin_coords[1][j] + y_bin_coords[0][j] )  #Between edges of a bin
        return center_y_coords


class ParticleBinCell:
    """A class to combine methods to adding to and combining data sets that contain information about particles in a bin"""
    def __init__(self, parcels=None):
        self.parcels = [] if parcels is None else parcels[:] #List of dictionaries with string keys and string values
        self.num_parcels = len(self.parcels)

    def add_data(self, diameter, particles_per_parcel):
        #User wants to add a single piece of information about a parcel found in a bin
        new_parcel = {'diameter': diameter, 'particles_per_parcel': particles_per_parcel}
        self.parcels.append(new_parcel)
        self.num_parcels += 1

    def print_data(self):
        logger.info("Data set has %d elements."%(self.num_parcels))
        logger.info('Diameter  ->  Particles Per Parcel')
        for i in range(0, self.num_parcels):
            logger.info("%10.6E\t%10.6E"%(float(self.parcels[i]['diameter']), float(self.parcels[i]['particles_per_parcel'])))

    def sort_diameters(self):
        if self.num_parcels > 0: #Only sort if there are actually any elements to sort
            #CheckSum for error checking
            check_sum_1 = 0.0
            for parcel in self.parcels:
                check_sum_1 += float(parcel['particles_per_parcel'])

            self.parcels.sort(key = lambda parcel: parcel['diameter'])

            #CheckSum for error checking
            check_sum_2 = 0.0
            for parcel in self.parcels:
                check_sum_2 += float(parcel['particles_per_parcel'])

            if abs(check_sum_1 - check_sum_2) >= 1e-6:
                logger.error("ERROR - Sorting process has lost data!")

    def sort_particles_per_parcel(self):
        if self.num_parcels > 0: #Only sort if there are actually any elements to sort
            #CheckSum for error checking
            check_sum_1 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])

            self.parcels.sort(key = lambda parcel: float(parcel['particles_per_parcel']))

            #CheckSum for error checking
            check_sum_2 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])
            if abs(check_sum_1 - check_sum_2) >= 1e-7:
                logger.error("ERROR - Sorting by parcels process has lost data!")

    def compress_data(self):
        """
        Combine repeated entries of diameters in the list to shorten the list length.
        Assumes that the parcel list is sorted according to increasing diameters.
        """
        if self.num_parcels > 0: 
            check_sum_1 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])

            #Timing
            start_time = time.clock()

            new_parcel_list = []
            i = 0
            while i < self.num_parcels:
                if i == self.num_parcels - 1:
                    #At end of data set, there is nothing after this, so no more repeats. Add to data set.
                    new_parcel_list.append(self.parcels[i])
                    i += 1
                elif self.parcels[i]['diameter'] != self.parcels[i+1]['diameter']:
                    new_parcel_list.append(self.parcels[i]) 
                    i += 1
                else:
                    count = 1
                    new_parcel_list.append(self.parcels[i]) 
                    end = False
                    while end == False:
                        if i + count < self.num_parcels:
                            if self.parcels[i+count]['diameter'] == self.parcels[i]['diameter']:
                                new_parcel_list[-1]['particles_per_parcel'] = str(float(new_parcel_list[-1]['particles_per_parcel']) + float(self.parcels[i+count]['particles_per_parcel']))
                                count += 1
                            else:
                                end = True
                        else:
                            end=True                        
                    i += count #Push index of array to position after the section that had repeated entries

            end_time = time.clock()
    
            #For compression metric
            starting_size = len(self.parcels)
            ending_size = len(new_parcel_list)
            
            self.parcels = new_parcel_list
            self.num_parcels = len(new_parcel_list) 

            check_sum_2 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])
            if abs(check_sum_1 - check_sum_2) >= 1e-6:
                logger.error("ERROR - Compression process has lost data!")
            else:
                logger.info("Compression efficiency: %4.3f"%(starting_size / ending_size))
                logger.info("Compression time: %4.3f"%(start_time - end_time))


    def custom_bins(self, custom_diameter_bins):
        """
        Re-sorts the data into specified diameter. The diameter data must be sorted into the bins given.
        No checks to make sure data will sort nicely into the user defined bins.
        
        Args:
            custom_diameter_bins: list of dictionaries with keys 'd_min' and 'd_max'. List is assumed to be sorted
                                  by increasing values of 'd_min'. And values are strings.
        """ 
        check_sum_1 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])
        #Create new lists for holding data
        new_parcels = []
        for i, dia_bin in enumerate(custom_diameter_bins):
            #Store the center values of the bins
            entry = {'diameter':str(0.5*(float(custom_diameter_bins[i]['d_min']) + float(custom_diameter_bins[i]['d_max']))),
                     'particles_per_parcel': str(0)}
            new_parcels.append(entry) 

        #sort into the new bins
        for parcel in self.parcels:
            #Find out which bin the ith diameter belongs in
            found = False #Flag for marking if the particular value falls into one of the provided bins
            for j, dia_bin in enumerate(custom_diameter_bins):
                if (float(parcel['diameter']) >= float(dia_bin['d_min'])) and (float(parcel['diameter']) < float(dia_bin['d_max'])):
                    new_parcels[j]['particles_per_parcel'] = str(float(new_parcels[j]['particles_per_parcel']) + float(parcel['particles_per_parcel'])) 
                    logger.debug("L: %10.6E \t R: %10.6E \t D: %s \t PPC: %s"%(float(dia_bin['d_min']), float(dia_bin['d_max']), parcel['diameter'], parcel['particles_per_parcel']))
                    found = True #Value has been placed into the new bin structure
                    break

            if found == False:# A value in the original data set was not able to be placed into the bins
                logger.warning("Warning: The value: %10.6E  in the original data set was unable to be placed into the user defined bins"%(float(parcel['diameter'])))

        self.parcels = new_parcels
        self.num_parcels = len(new_parcels) 

        check_sum_2 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels])
        if abs(check_sum_1 - check_sum_2) >= 1e-6:
            logger.warning("Warning - Customizing Bins process has lost data, which may be due to existing data being outside of user-defined bin values")
            logger.warning("Magnitude of Error: %10.6E"%(abs(check_sum_1 - check_sum_2)))

    def __add__(self, other):
        """
        Combine the data contained in two instances of the class into a new class
        """
        if len(other.parcels) > 0:  #Only add the new data if it actually exists
            self.sort_particles_per_parcel()
            other.sort_particles_per_parcel()
            check_sum_1 = sum([float(parcel['particles_per_parcel']) for parcel in self.parcels] + [float(parcel['particles_per_parcel']) for parcel in other.parcels])
    
            new_parcels = self.parcels + other.parcels #concatenate the internal lists
            combined_data = ParticleBinCell(new_parcels)
            combined_data.sort_particles_per_parcel()

            check_sum_2 = sum([float(parcel['particles_per_parcel']) for parcel in combined_data.parcels])
            if abs(check_sum_1 - check_sum_2) >= 1e-9:
                logger.error("ERROR - Addition process has lost data! Discrepancy is: %10.6E"%(abs(check_sum_1 - check_sum_2)))
                logger.error("Input Sum of particles_per_parcel: %10.6E"%(check_sum_1))
                logger.error("Output Sum of particles_per_parcel: %10.6E"%(check_sum_2))
        else:
            combined_data = ParticleBinCell(self.parcels)

        return ParticleBinCell(combined_data.parcels)




