class ParticleBinDomain:
    """A class to combine the methods of computing the extents of the spatial domain over which particle data is collected"""
    
    def __init__(self,x_max=1,x_min=0,y_max=1,y_min=0,num_x_bins=1, num_y_bins=1):
        self.x_max = x_max
        self.x_min = x_min
        self.y_max = y_max
        self.y_min = y_min
        self.num_x_bins = num_x_bins
        self.num_y_bins = num_y_bins

    def compute_dx(self):
        return (self.x_max - self.x_min)/self.num_x_bins

    def compute_dy(self):
        return (self.y_max - self.y_min)/self.num_y_bins

    def compute_x_bin_coords(self):
        import numpy as np
        x_bin_coords = np.zeros((2,self.num_x_bins))
        x_bin_coords[0][0] = self.x_min
        x_bin_coords[1][0] = self.x_min + self.compute_dx()
        for i in range(1,self.num_x_bins):
            x_bin_coords[0][i] = x_bin_coords[1][i-1]
            x_bin_coords[1][i] = x_bin_coords[0][i] + self.compute_dx()
        
        return x_bin_coords

    def print_x_bin_coords(self,non_dimensional_factor=None):
        x_bin_coords = self.compute_x_bin_coords()
        print("\n\nX Bin Coordinates are:")
        table_header = "{:<11} {:<15} {:<15}{:<10}".format('Bin #','Min','Max','Center')
        if non_dimensional_factor is not None:
            table_header = "{}\t{:<}".format(table_header,'Non-Dimensional Center')
        print(table_header)

        for i in range(0,self.num_x_bins):
            center_coord = (x_bin_coords[0][i] + x_bin_coords[1][i])/2.0
            if non_dimensional_factor is None:
                print("  %d \t%10.2E\t%10.2E\t%10.2E"%(i+1,x_bin_coords[0][i],x_bin_coords[1][i],center_coord))
            else:
                print("  %d \t%10.2E\t%10.2E\t%10.2E\t    %8.6f"%(i+1,x_bin_coords[0][i],x_bin_coords[1][i],center_coord,center_coord/non_dimensional_factor))


    def compute_x_bin_center_coords(self):
        import numpy as np
	center_x_coords = np.zeros(self.num_x_bins)
        x_bin_coords = self.compute_x_bin_coords()
	for j in range(0,self.num_x_bins):
            center_x_coords[j] =  0.5*( x_bin_coords[1][j] + x_bin_coords[0][j] )  #Between edges of a bin
        return center_x_coords

    def compute_y_bin_coords(self):
        import numpy as np
        y_bin_coords = np.zeros((2,self.num_y_bins))
        y_bin_coords[0][0] = self.y_min
        y_bin_coords[1][0] = self.y_min + self.compute_dy()
        for i in range(1,self.num_y_bins):
            y_bin_coords[0][i] = y_bin_coords[1][i-1]
            y_bin_coords[1][i] = y_bin_coords[0][i] + self.compute_dy()

        return y_bin_coords

    def print_y_bin_coords(self,non_dimensional_factor=None):
        y_bin_coords = self.compute_y_bin_coords()
        print("\n\nY Bin Coordinates are:")
        table_header = "{:<11} {:<15} {:<15}{:<10}".format('Bin #','Min','Max','Center')
        if non_dimensional_factor is not None:
            table_header = "{}\t{:<}".format(table_header,'Non-Dimensional Center')
        print(table_header)

        for i in range(0,self.num_y_bins):
            center_coord = (y_bin_coords[0][i] + y_bin_coords[1][i])/2.0
            if non_dimensional_factor is None:
                print("  %d \t%10.2E\t%10.2E\t%10.2E"%(i+1,y_bin_coords[0][i],y_bin_coords[1][i],center_coord))
            else:
                print("  %d \t%10.2E\t%10.2E\t%10.2E\t    %8.6f"%(i+1,y_bin_coords[0][i],y_bin_coords[1][i],center_coord,center_coord/non_dimensional_factor))



    def compute_y_bin_center_coords(self):
        import numpy as np
	center_y_coords = np.zeros(self.num_y_bins)
        y_bin_coords = self.compute_y_bin_coords()
	for j in range(0,self.num_y_bins):
            center_y_coords[j] =  0.5*( y_bin_coords[1][j] + y_bin_coords[0][j] )  #Between edges of a bin
        return center_y_coords





class ParticleBinCell:
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
        print("Data set has %d elements. Output below is Nx2 array: Diameter and Particles Per Parcel"%(self.NumElements))
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

        if(self.NumElements>0):	#Only sort if there are actually any elements to sort
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
        #Sorts the particlesPerParcel list in order of low to high - good for summing up values
        from operator import itemgetter

        if(self.NumElements>0): #Only sort if there are actually any elements to sort

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
            #    print("%s\t%s"%(alist[i][0],alist[i][1]))

            #Sorts from low to high based on the ParticlesPerParcel list
            alist.sort(key=itemgetter(2))

            #print("Post-sort list")
            #for i in range(self.NumElements):
            #	 print("%s\t%s"%(alist[i][0],alist[i][1]))

            #Re-distribute the data from the 2D sorted list back into the individual list data sets
            for i in range(self.NumElements):
                self.ParticleDiameters[i] = alist[i][0]
                self.ParticlesPerParcel[i] = alist[i][1]

            #CheckSum for error checking
            CheckSum2 = 0.0
            for i in range(0,self.NumElements):
                CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

            if( abs(CheckSum1 - CheckSum2) >= 1e-7):
                print("ERROR - Sorting of Parcel Data process has lost data!")




    def compress_data(self): #combine repeated entries of diameters in the list to shorten the list length
        import time
        
        if(self.NumElements>0): #Compress data only if there is data present in the dataset
            #CheckSum for error checking
            CheckSum1 = 0.0
            for i in range(0,self.NumElements):
                CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i])

            #For compression metric
            starting_size = self.NumElements

            #Timing
            TimeStart = time.clock()

            NewDiameterList = []
            NewParcelList = []
            j = 0	#Index for new list
            i = 0
            NewCount = 0  #For counting number of entries after the merge
            while(i<self.NumElements):

                if(i == self.NumElements-1):
                    #At end of data set, there is nothing after this, so no more repeats. Add to data set.
                    NewDiameterList.append(self.ParticleDiameters[i])
                    NewParcelList.append(self.ParticlesPerParcel[i])
                    j = j + 1
                    i = i + 1
                    NewCount = NewCount + 1

                elif(self.ParticleDiameters[i] != self.ParticleDiameters[i+1]):
                    NewDiameterList.append(self.ParticleDiameters[i])
                    NewParcelList.append(self.ParticlesPerParcel[i])
                    j = j + 1
                    i = i + 1
                    NewCount = NewCount + 1
                else:
                    end = False
                    NewCount = NewCount + 1
                    count = 1
                    NewDiameterList.append(self.ParticleDiameters[i])
                    NewParcelList.append(self.ParticlesPerParcel[i])
                    while(end == False):
                        if(i+count < self.NumElements):
                            if(self.ParticleDiameters[i+count] == self.ParticleDiameters[i]):
                                NewParcelList[j] = str(float(NewParcelList[j]) + float(self.ParticlesPerParcel[i+count]) )
                                count = count + 1
                            else:
                                end = True
                        else:
                            end=True						
            
                    #Increment counters before exiting else statement
                    j = j + 1
                    i = i + count #Push index of array to position after the section that had repeated entries

            TimeEnd = time.clock()
    
            ending_size = NewCount

            self.ParticleDiameters = NewDiameterList
            self.ParticlesPerParcel = NewParcelList
            self.NumElements = NewCount

            #CheckSum for error checking
            CheckSum2 = 0.0
            for i in range(0,self.NumElements):
                CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

            if( abs(CheckSum1 - CheckSum2) >= 1e-6):
                print("ERROR - Compression process has lost data!")
            else:
                print("Compression efficiency: %4.3f"%(starting_size/ending_size))





    def custom_bins(self,UserDiameterBins):
        #The user wants to re-sort the data into bins of their choosing. The diameter data must be sorted into the bins given. No checks to make sure data will
        #sort nicely into the user defined bins.
        #Input is a 2D list, 2xN with the first and second rows holding the left and right coordinates of the edges of a bin, respectively.

        #if(self.NumElements>0):

            #CheckSum for error checking
            CheckSum1 = 0.0
            for i in range(0,self.NumElements):
                CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i])

            #Create new lists for holding data
            UserDiameters = []
            NumBins = len(UserDiameterBins[0]) #Get number of columns

            for i in range(0,NumBins):
                #Store the center values of the bins
                UserDiameters.append( str(0.5*(float(UserDiameterBins[0][i]) + float(UserDiameterBins[1][i]))) )


            #Initialize the parcel counts in the new bins to be zero
            NewParcelCount = []
            for i in range(0,NumBins):
                NewParcelCount.append( str(0) )

    
            #Loop throught all entries in the local data set and sort into the new bins
            for i in range(0,self.NumElements):
                #Find out which bin the ith diameter belongs in
                Found = False #Flag for marking if the particular value falls into one of the provided bins
                for j in range(0,NumBins):
                    if( (float(self.ParticleDiameters[i]) >= float(UserDiameterBins[0][j]) ) and ( float(self.ParticleDiameters[i]) < float(UserDiameterBins[1][j]) ) ):
                        tmpValue = NewParcelCount[j]
                        NewParcelCount[j] = str( float(NewParcelCount[j]) + float(self.ParticlesPerParcel[i]) )	
                        #print("L: %10.6E \t R: %10.6E \t %s \t %s\n"%(float(UserDiameterBins[0][j]),float(UserDiameterBins[1][j]),self.ParticleDiameters[i],NewParcelCount[j]))
                        Found = True #Value has been placed into the new bin structure
                        break

                if(Found == False):# A value in the original data set was not able to be placed into the bins
                    print("Warning: The value: %10.6E  in the original data set was unable to be placed into the user defined bins"%(float(self.ParticleDiameters[i])))

            self.ParticleDiameters = UserDiameters
            self.ParticlesPerParcel = NewParcelCount
            self.NumElements = NumBins


            #CheckSum for error checking
            CheckSum2 = 0.0
            for i in range(0,self.NumElements):
                CheckSum2 = CheckSum2 + float(self.ParticlesPerParcel[i])

            if( abs(CheckSum1 - CheckSum2) >= 1e-6):
                print("Warning - Customizing Bins process has lost data, which may be due to existing data being outside of user-defined bin values")
                print("Magnitude of Error: %10.6E"%(abs(CheckSum1 - CheckSum2)))


                    

    def __add__(self,other):
        #User wants to combine the data contained in the two instances of the class into a new class

        import time

        if(other.NumElements >0):  #Only add the new data if it actually exists

            #CheckSum for error checking
            CheckSum1 = 0.0
            for i in range(0,self.NumElements):
                CheckSum1 = CheckSum1 + float(self.ParticlesPerParcel[i]) 

            for i in range(0,other.NumElements):
                CheckSum1 = CheckSum1 + float(other.ParticlesPerParcel[i])
    
            #Create object to hold the combined data and initialize to the second argument
            #print("Number of elements in self:%d"%self.NumElements)
            #print("Number of elements in other:%d"%other.NumElements)
            #CombinedData = ParticleBinCell(self.ParticleDiameters,self.ParticlesPerParcel,self.NumElements)
            #print(self.ParticlesPerParcel)
            #print(other.ParticlesPerParcel)

            #The method now needs to add entries to the ParticleDiameters list if they are NOT already in the list. If
            #they are already in the list, then just add the values of the ParticlesPerParcel together


            #Put the two data sets together by concatenating the internal lists
            NewDiameterList = self.ParticleDiameters  + other.ParticleDiameters
            NewParcelList   = self.ParticlesPerParcel + other.ParticlesPerParcel
            NewCount        = self.NumElements        + other.NumElements

            CombinedData = ParticleBinCell(NewDiameterList,NewParcelList,NewCount)

            #Debuggin output
            #print("Total Input Elements: %d"%(self.NumElements + other.NumElements))
            #print("Number of output elements: %d"%CombinedData.NumElements)
    
            #CheckSum for error checking
            CheckSum2 = 0.0
            for i in range(0,CombinedData.NumElements):
                CheckSum2 = CheckSum2 + float(CombinedData.ParticlesPerParcel[i])

            if( abs(CheckSum1 - CheckSum2) >= 1e-9):
                print("ERROR - Addition process has lost data! Discrepancy is: %10.6E"%(abs(CheckSum1 - CheckSum2)))

        else:
            NewDiameterList = self.ParticleDiameters  
            NewParcelList   = self.ParticlesPerParcel 
            NewCount        = self.NumElements        

            CombinedData = ParticleBinCell(NewDiameterList,NewParcelList,NewCount)


        return ParticleBinCell(CombinedData.ParticleDiameters, CombinedData.ParticlesPerParcel, CombinedData.NumElements)




