#######################################################################################
# The purpose of this module is to collect a set of useful statistics functions that
# can be used to analyze lagrangian particle data.
#
# Author: Christopher Neal
#
# Date: 11-20-2015
# Updated: 11-20-2015
#
#######################################################################################

def IQR(DataSet):
        import numpy as np
	
	#DataSet is the form of a 1D vector of information such as observations of an experiment
	q75, q25 = np.percentile(DataSet, [75 ,25])
	return q75 - q25

def Output_SMD_PDF_Data(ParticleData,N_Parcels,BinFlag):

	import numpy as np

	#Note that ParticleData is a 2D array of particle diameters & number of particles
	
	#Check to make sure that more than 1 entry exists, otherwise do nothing and tell user
	if(N_Parcels == 0):
		print("No Particles in Bin. Nothing will be output for this data set")


	ParticleDiameters = np.zeros(N_Parcels)
	#Compute the bin size for the Diameters
	for i in range(0,N_Parcels):
		ParticleDiameters[i] = ParticleData[0][i]
	
	if(BinFlag == 1):  #Use bins for the particle diameters
		#Freedman-Diaconis bin size estimation
		h = 2*IQR(ParticleDiameters)*N_Particles**(-1.0/3.0)

		print("Diameter Bin size is: %10.2E"%(h))

		DMin = np.amin(ParticleDiameters)
		DMax   = np.amax(ParticleDiameters)
		print("Minimum Particle Diameter: %10.2E"%(DMin))
		print("Maximum Particle Diameter: %10.2E"%(DMax))
	

		NBins = 1
		DStart = DMin
		AllBinsFound = 0
		while(AllBinsFound == 0):
			DStart = DStart + h
			if(DStart <= DMax):
				NBins = NBins + 1
			else:
				AllBinsFound = 1
	
		print("Number of diameter bins is: %d"%(NBins))

		#Create vector of particle diameter bin coordinates
		Dia_Bin_Coords = np.zeros((2,NBins))
		Dia_Bin_Coords[0][0] = DMin
		Dia_Bin_Coords[1][0] = DMin + h
		for i in range(1,NBins):
			Dia_Bin_Coords[0][i] = Dia_Bin_Coords[1][i-1]
			Dia_Bin_Coords[1][i] = Dia_Bin_Coords[0][i] + h

		for i in range(0,NBins):
			print("Diameter Bin %d \t%10.2E\t%10.2E\n"%(i+1,Dia_Bin_Coords[0][i],Dia_Bin_Coords[1][i]))

		#Sort the particles into Bins
		Dia_Bins = np.zeros(NBins)
		for i in range(0,N_Parcels):
		
			for j in range(0,NBins):
				if(ParticleDiameters[i] <= Dia_Bin_Coords[1][j] and ParticleDiameters[i] >= Dia_Bin_Coords[0][j]):
					Dia_Bins[j] = Dia_Bins[j] + 1
	
	
		print("Bin Counts:\n"%(Dia_Bins))
		print(Dia_Bins)
		print("Sum of particles in bins: %d\n"%(np.sum(Dia_Bins)))

		#Now tha the bins are constructed we compute the Sauter mean diameter using the bins
		#we use the mean diameter in the bin as the representative value of the diameter for all particles in a bin.

		numerator = 0
		denominator = 0
		for i in range(0,NBins):
			numerator = numerator + Dia_Bins[i]*( 0.5*( Dia_Bin_Coords[1][i] + Dia_Bin_Coords[0][i] ) )**3
			denominator = denominator + Dia_Bins[i]*( 0.5*( Dia_Bin_Coords[1][i] + Dia_Bin_Coords[0][i] ) )**2

		SMD = numerator/denominator

	elif(BinFlag == 0): #do not use bins

		numerator = 0
                denominator = 0
                for i in range(0,N_Parcels):
                	numerator = numerator + ParticleData[1][i]*(ParticleData[0][i]**3)
                        denominator = denominator + ParticleData[1][i]*(ParticleData[0][i]**2)

                SMD = numerator/denominator


	return SMD

