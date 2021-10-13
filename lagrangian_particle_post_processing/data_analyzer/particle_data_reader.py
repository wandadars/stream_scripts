import itertools
import h5py
import logging
import os

logger = logging.getLogger(__name__)

class HDF5ParticleDataReader(object):
    """
    The purpose of this module is to read the particle data that is stored in HDF5 format
    and return an array that is filled with particle data information.
    """
    def __init__(self, case_name, time_stamp):
        self.case_name = case_name
        self.time_stamp = time_stamp
        self.num_parcels = 0

    def read_particle_diameter_data(self):
        file_name = 'ptdia_ptsca.' + str(self.time_stamp) + '_' + self.case_name

        f = h5py.File(file_name, 'r')
        
        #Make sure the group is in the dataset
        if 'ptdia' in f.keys():
            particles = f['ptdia'][:]
        else:
            particles = []

        logger.info('Storing diameter data from file: %s'%(file_name))
        diameter_data = []
        for particle in particles:
            diameter_data.append(particle)

        logger.info("Detected %d parcels in data file"%(len(particles)))
        self.num_parcels = len(particles)

        f.close()
        return diameter_data

    def read_particle_coordinate_data(self):
        file_name = 'particle_pos.' + str(self.time_stamp) + '_' + self.case_name
        
        f = h5py.File(file_name, 'r')
        
        #Make sure the group is in the dataset
        if 'particle position' in f.keys():
            positions = f['particle position'][:]
        else:
            positions = []

        logger.info("Storing parcel coordinate data from file: %s"%(file_name))
        
        #Store data in a 3xN list
        position_data = []
        position_data.append([])
        position_data.append([])
        position_data.append([])

        for position in positions:
            position_data[0].append(position['x'])
            position_data[1].append(position['y'])
            position_data[2].append(position['z'])
        f.close()
        
        logger.info("Number of rows in parcel position data set:%d"%(len(position_data)))
        logger.info("Number of columns in parcel position data set: %d"%(len(position_data[0])))
        return position_data

    def read_particle_parcel_data(self):
        file_name = 'ptnump_ptsca.' + str(self.time_stamp) + '_' + self.case_name
        
        f = h5py.File(file_name, 'r')
        
        #Make sure the group is in the dataset
        if 'ptnump' in f.keys():
            particles_per_parcel_data = f['ptnump'][:]
        else:
            particles_per_parcel_data = [] 

        logger.info("Storing particles per parcel data from file: %s"%(file_name))
        particles_per_parcel = []
        parcel_check_counter = 0 #For checking that all data is actually being read from file
        for parcel in particles_per_parcel_data:
            particles_per_parcel.append(parcel)
        f.close()

        logger.info("Number of particles per parcel data read: %d"%(len(particles_per_parcel)))
        return particles_per_parcel
        
    def read_particle_temperature_data(self):
        file_name = 'pttemp_ptsca.' + str(self.time_stamp) + '_' + self.case_name
        
        f = h5py.File(file_name, 'r')
        
        #Make sure the group is in the dataset
        if 'pttemp' in f.keys():
            temperatures = f['pttemp'][:]
        else:
            temperatures = [] 

        logger.info("Storing temperature data from file: %s"%(file_name))
        temperature_data = []
        ready_to_read = False
        for temperature in temperatures:
            temperature_data.append(temperature)
        f.close()
        return temperature_data


class HDF5ParticlePropertyPlotterDataReader(HDF5ParticleDataReader):
    """
    The purpose of this module is to read the particle data that is stored in HDF5 format
    and return an array to the caller that is filled with particle data information.
    """
    def __init__(self,case_name,time_stamp):
        super(HDF5ParticlePropertyPlotterDataReader, self).__init__(case_name, time_stamp)
    
    def read_hdf_particle_data(self):
        #Store all of the particle data that is currently in a list format into one large list
        diameter_data = self.read_particle_diameter_data()
        particle_temperature_data = self.read_particle_temperature_data()

        particle_data = []
        for i in range(0, self.num_parcels):
            particle_data.append([])
            particle_data[i].append(diameter_data[i])
            particle_data[i].append(particle_temperature_data[i])
        return particle_data


class HDF5ParticlePDFPlotterDataReader(HDF5ParticleDataReader):
    """
    The purpose of this module is to read the particle data that is stored in HDF5 format
    and return an array to the caller that is filled with particle data information.
    """
    def __init__(self,case_name,time_stamp):
        super(HDF5ParticlePDFPlotterDataReader, self).__init__(case_name, time_stamp)
    
    def read_hdf_particle_data(self):
        #Store all of the particle data that is currently in a list format into one large list
        diameter_data = self.read_particle_diameter_data()
        position_data = self.read_particle_coordinate_data()
        particles_per_parcel_data = self.read_particle_parcel_data()

        particle_data = []
        for i in range(0, self.num_parcels):
            entry = {'diameter': diameter_data[i],
                     'x': position_data[0][i],
                     'y': position_data[1][i],
                     'z': position_data[2][i],
                     'particles_per_parcel': particles_per_parcel_data[i]}
            particle_data.append(entry)
        return particle_data


class VOFDataReader(object):
    def __init__(self, case_name, time_stamp):
        self.case_name = case_name
        self.time_stamp = time_stamp

    def read_particle_diameter_data(self):
        file_name = 'dropletSDF_' + str(self.time_stamp) + '.dat'

        try:
            f = open(file_name,'r')
        except IOError as e:
            logger.error('Unable to open file') #Does not exist OR no read permissions
            raise IOError

        logger.info('Storing diameter data from file: %s'%(file_name))
        diameter_data = []
        ready_to_read = False
        num_entries = 0
        for Line in f:
            #Stop when we have been reading data and we encounter a brace character on the line
            if ready_to_read == True  and '}' in Line :
                break

            if ready_to_read == True:
                #Parse line
                LineData = Line.rstrip()
                LineData = LineData.replace(',', ' ')
                LineData = LineData.split()

                diameter_data.append(LineData)

                #Count number of entries on this line
                num_entries += len(LineData)

            if 'DATA {' in Line:    #Real data is on next line. Prepare to read
                ready_to_read = True

        logger.info("Detected %d parcels in data file"%(num_entries))
        self.num_parcels = num_entries

        #Close and delete the data file
        f.close()
        os.remove('tempPythonFile.txt')

        #Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
        diameter_data = list(itertools.chain.from_iterable(diameter_data))
        return diameter_data


class VOFASCIIDataReader(VOFDataReader):
    def __init__(self):
        super(VOFASCIIDataReader, self).__init__()

    def read_particle_data(self):
        diameter_data = self.read_particle_diameter_data()
        position_data = self.read_particle_position_data()
        pass

