#######################################################################################
# The purpose of this module is to define a class definition for a data structure that
# contains information about the particles that are present in a particular spatial bin.
# The purpose of the class is to simplify the handling and combination of these data 
# sets over time.
#
# Author: Christopher Neal
#
# Date: 02-23-2016
# Updated: 02-23-2016
#
#######################################################################################


class ParticleBinData:
	"""A class to combine methods to adding to and combining data sets that contain information about particles in a bin"""
	
	def __init__(self,ParticleDiameter=None,PartsPerParcel=None,EleCount=0):
		self.ParticleDiameters = [] if ParticleDiameter is None else  ParticleDiameter[:]
                self.ParticlesPerParcel = [] if PartsPerParcel is None else PartsPerParcel[:]
                self.NumElements = EleCount


	def add_data(self,Diameter,ParticleNumber):
		#User wants to add a single piece of information about a parcel found in a bin
		self.ParticleDiameters.append(Diameter)
		self.ParticlesPerParcel.append(ParticleNumber)
		self.NumElements = self.NumElements + 1

	def print_data(self):

		print("Data set has %d elements with output being an Nx2 format of the diameter and the particles per parcel"%(self.NumElements))
		print("Number of elements in ParticlesPerParcel list: %d"%(len(self.ParticlesPerParcel)))
		for i in range(0,self.NumElements):
			print("%10.6E\t%10.6E"%(float(self.ParticleDiameters[i]),float(self.ParticlesPerParcel[i])))


	def check_data_length(self):
		if(self.NumElements != len(self.ParticleDiameters)):
			print("ERROR: Mis-match between actual amount of data & expected amount of data contained in object")
			print("Object contains %d elements, but thinks it contains %d elements"%(len(self.ParticleDiameters),self.NumElements))

		else:
			print("Data Check Passed. Object has %d elements and thinks it contains %d elements"%(len(self.ParticleDiameters),self.NumElements))

	def sort_diameters(self):
		from operator import itemgetter

		#CheckSum for error checking
                CheckSum1 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i])

		#Combine the two object data lists into a 2D list of dimension NumElements x 2
		alist = []
		for i in range(0,self.NumElements):
			alist.append([])
			alist[i].append(self.ParticleDiameters[i])
			alist[i].append(self.ParticlesPerParcel[i])
			alist[i].append(float(self.ParticleDiameters[i]))

		alist.sort(key=itemgetter(2))

		for i in range(self.NumElements):
			self.ParticleDiameters[i] = alist[i][0]
			self.ParticlesPerParcel[i] = alist[i][1]

		#CheckSum for error checking
                CheckSum2 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

                if( abs(CheckSum1 - CheckSum2) >= 1e-6):
                        print("ERROR - Sorting process has lost data!")


	def sort_particlesPerParcel(self):
		from operator import itemgetter

                #CheckSum for error checking
                CheckSum1 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i])
                
		#Combine the two object data lists into a 2D list of dimension NumElements x 2
                alist = []
                for i in range(0,self.NumElements):
                        alist.append([])
                        alist[i].append(self.ParticleDiameters[i])
                        alist[i].append(self.ParticlesPerParcel[i])
			alist[i].append(float(self.ParticlesPerParcel[i]))

		#print("Pre-sort list")
                #for i in range(self.NumElements):
                #        print("%s\t%s"%(alist[i][0],alist[i][1]))

		#Sorts from low to high based on the ParticlesPerParcel list
                alist.sort(key=itemgetter(2))

		#print("Post-sort list")
		#for i in range(self.NumElements):
		#	print("%s\t%s"%(alist[i][0],alist[i][1]))

		#Re-distribute the data from the 2D sorted list back into the individual list data sets
                for i in range(self.NumElements):
                        self.ParticleDiameters[i] = alist[i][0]
                        self.ParticlesPerParcel[i] = alist[i][1]

                #CheckSum for error checking
                CheckSum2 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

                if( abs(CheckSum1 - CheckSum2) >= 1e-6):
                        print("ERROR - Sorting of Parcel Data process has lost data!")




	def compress_data(self): #combine repeated entries in the list to shorten the list length

		#CheckSum for error checking
		CheckSum1 = 0.0
		for i in range(0,self.NumElements):
			CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i])

		NewDiameterList = []
		NewParcelList = []
		FinishedCompression = False
		Sorted = [] #List to hold values that have already been sorted
		NewCount = 0
		while(FinishedCompression == False):
	
			FinishedCompression = True #Initialize to true. Remaining code will control whether it stays true or goes to false

			if(NewCount == 0):
				NewDiameterList.append( self.ParticleDiameters[NewCount] )
	                        NewParcelList.append( self.ParticlesPerParcel[NewCount] )
				
				MatchIndices = []
				#Go through the rest of the array and locate the indices of the matching elements
				for i in range(1,self.NumElements):
					if(NewDiameterList[NewCount] == self.ParticleDiameters[i]): #A match was found
						MatchIndices.append(i)

				for i in range(0,len(MatchIndices)):
						NewParcelList[NewCount] = str(float(NewParcelList[NewCount]) + float(self.ParticlesPerParcel[MatchIndices[i]]) )
				
				Sorted.append(self.ParticleDiameters[0])
				NewCount = NewCount + 1
				FinishedCompression = False
			else:
	
				#Now we must also check whether the element has already been sorted
				for i in range(0,self.NumElements):
							
					NewElementFound = False		
					for j in range(0,NewCount):
						if(Sorted[j] != self.ParticleDiameters[i]):
							NewElementFound = True


					if(NewElementFound == True):	
						NewDiameterList.append( self.ParticleDiameters[i] )
		                                NewParcelList.append( self.ParticlesPerParcel[i] )
						Sorted.append(self.ParticleDiameters[i])
						StartingIndex = i
						FinishedCompression = False
				
				
				MatchIndices = [] #Initialize to empty
				#Now loop over all elements and find the indices that correspond to the new element
				for i in range(StartingIndex+1,self.NumElements):
                                        if(NewDiameterList[NewCount] == self.ParticleDiameters[i]): #A match was found
                                               MatchIndices.append(i)

				for i in range(0,len(MatchIndices)):
                                                NewParcelList[NewCount] = str(float(NewParcelList[NewCount]) + float(self.ParticlesPerParcel[MatchIndices[i]]) )

                                NewCount = NewCount + 1


		self.ParticleDiameters = NewDiameterList
		self.ParticlesPerParcel = NewParcelList
		self.NumElements = NewCount

		#CheckSum for error checking
                CheckSum2 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

		if( abs(CheckSum1 - CheckSum2) >= 1e-6):
			print("ERROR - Compression process has lost data!")



	def custom_bins(self,UserDiameterBins):
		#The user wants to re-sort the data into bins of their choosing. The diameter data must be sorted into the bins given. No checks to make sure data will
		#sort nicely into the user defined bins.
		#Input is a 2D list, 2xN with the first and second rows holding the left and right coordinates of the edges of a bin, respectively.


		#Create new lists for holding data
		UserDiameters = []
		NumBins = len(UserDiameterBins[0]) #Get number of columns
		for i in range(0,NumBins):
			UserDiameters.append( str(0.5*(float(UserDiameterBins[0][i]) + float(UserDiameterBins[1][i]))) )


		#Loop throught all entries in the local data set and sort into the new bins
		NewParcelCount = []
		for i in range(0,NumBins):
			NewParcelCount.append( str(0) )

		for i in range(0,self.NumElements):

			#Find out which bin the ith diameter belongs in
			for j in range(0,NumBins):
				if(self.ParticleDiameters[i] >= UserDiameterBins[0][j] and self.ParticleDiameters[i] < UserDiameterBins[1][j]):
					NewParcelCount[j] = str( float(NewParcelCount[j]) + float(self.ParticlesPerParcel[i]) )			
					break

		self.ParticleDiameters = UserDiameters
		self.ParticlesPerParcel = NewParcelCount
		self.NumElements = NumBins


	def __add__(self,other):
		#User wants to combine the data contained in the two instances of the class into a new class


		#CheckSum for error checking
		CheckSum1 = 0.0
                for i in range(0,self.NumElements):
                        CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i]) 

		for i in range(0,other.NumElements):
			CheckSum1 = CheckSum1 + float(other.ParticlesPerParcel[i])
		#Create object to hold the combined data and initialize to the second argument

		#print("Number of elements in self:%d"%self.NumElements)
		#print("Number of elements in other:%d"%other.NumElements)
		CombinedData = ParticleBinData(self.ParticleDiameters,self.ParticlesPerParcel,self.NumElements)
		#print(self.ParticlesPerParcel)
		#print(other.ParticlesPerParcel)

		#The method now needs to add entries to the ParticleDiameters list if they are NOT already in the list. If
		#they are already in the list, then just add the values of the ParticlesPerParcel together
		ElementsAdded = 0
		ElementsRemoved = 0
		for i in range(0,other.NumElements):
 
			FoundDiameterMatch = False
			for j in range(0,CombinedData.NumElements):
				if(other.ParticleDiameters[i] == CombinedData.ParticleDiameters[j]): #A match was found for the diameters in the list
					FoundDiameterMatch = True
					MatchLoc = j
					break  #Stop looping through the data set after a match is found

			if(FoundDiameterMatch == True):
				#print("Old Value of ParticlesPerParcel: %s"%(CombinedData.ParticlesPerParcel[MatchLoc]))
				#print("Adding the following number to above: %s"%(other.ParticlesPerParcel[i]))
				#print("New Value of ParticlesPerParcel is: %s"%(str( float(CombinedData.ParticlesPerParcel[MatchLoc]) + float(other.ParticlesPerParcel[i]) )))
				CombinedData.ParticlesPerParcel[MatchLoc] = str( float(CombinedData.ParticlesPerParcel[MatchLoc]) + float(other.ParticlesPerParcel[i]) )
				ElementsRemoved = ElementsRemoved + 1
			else: #Need to append the new entry to the list
				CombinedData.add_data(other.ParticleDiameters[i],other.ParticlesPerParcel[i])	
				ElementsAdded = ElementsAdded + 1

		#Re-sort the data set to preserve efficiency of other algorithms operating on the data set	
		CombinedData.sort_diameters()

		#print(self.ParticlesPerParcel)
		#print(CombinedData.ParticlesPerParcel)
		#Debuggin output
		#print("Total Input Elements: %d"%(self.NumElements + other.NumElements))
		#print("Estimated number of elements after combination: %d"%(self.NumElements + ElementsAdded - ElementsRemoved ))
		#print("Number of output elements: %d"%CombinedData.NumElements)
		
		#CheckSum for error checking
                CheckSum2 = 0.0
                for i in range(0,CombinedData.NumElements):
                        CheckSum2 = CheckSum2 + float(CombinedData.ParticlesPerParcel[i])

                if( abs(CheckSum1 - CheckSum2) >= 1e-7):
                        print("ERROR - Addition process has lost data! Discrepancy is: %10.6E"%(abs(CheckSum1 - CheckSum2)))


		return ParticleBinData(CombinedData.ParticleDiameters, CombinedData.ParticlesPerParcel, CombinedData.NumElements)




