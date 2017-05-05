#######################################################################################
# The purpose of this module is to define a class definition for a data structure that
# contains information about the particles. The purpose of the class is to simplify the 
# handling and combination of these data sets once they have been read in from a file 
# and stored into a histogram form.
#
# Author: Christopher Neal
#
# Date: 05-18-2016
# Updated: 05-18-2016
#
#######################################################################################
class particle_histogram:
    """A class to combine methods to process data about particle histogram information"""

    def __init__(self):
        self.horizontal_bins = [] 
        self.pdf = [] 
        self.vol_pdf = []
        self.widths = []
        self.cdf = []
        self.num_bins = 0
        self.RadiusAverageFlag = 1  #For averaging over all radius data given in dataset- 0=no, 1=yes
        self.MassWeightedFlag = 0  #For performing mass weighted PDF calculations

    def get_horizontal_bins(self):
        return self.horizontal_bins

    def get_pdf(self):
        return self.pdf

    def get_widths(self):
        if not self.widths:
            self.compute_widths()
        
        return self.widths

    def get_num_bins(self):
        return self.num_bins

    def read_data(self,FilePath,DebugFlag=0):
            import itertools
            import string
            import numpy as np
            import sys

            print("Reading Data From: %s"%(FilePath))
            #Open input file
            try:
                    f = open(FilePath, "r")
            except:
                    print("Failed to Input File!")
                    sys.exit(1)

            #Loop over all lines in input file and parse
            count=0 #Line counter
            print("Reading Data File Contents")
            DataArrayList = [] #Initialize list
            RowCount = 0 #For counting number of data rows in file
            for Line in f:

                    if(count == 0): #First line with x/D coordinate
                            tmp = Line.rstrip() #Remove newline character
                            tmp = tmp.split()
                            xOverD = float(tmp[-1]) #Extract coordinate(Last element in the split list)
                            print("X/D Coordinate is: %f"%(xOverD))

                    elif(count == 5): #Line with r/D coordinates
                            #Remove all non-numeric characters from the string
                            tmp = Line.rstrip()
                            tmp = "".join(c for c in tmp if c in '1234567890.' or c in string.whitespace)
                            tmp = tmp.split()
                            NumRadii = len(tmp)
                            rOverD = tmp
    
                            print("Number of Radii at which particle PDF is measured: %d"%(NumRadii))
                            print("Values of r/D: %s\n"%(rOverD))

                    elif(count >=8): #This is where the raw pdf data is located in the file

                            tmp = Line.rstrip()

                            #Only perform storage on lines that are not blank in the file
                            if(tmp != ''):

                                    tmp = tmp.split()
                                    if(RowCount == 0): #First item in list
                                            DataArrayList.append([])
                                            DataArrayList[RowCount].append(tmp)
                                            RowCount = RowCount + 1
                                    else:
                                            DataArrayList.append([])
                                            DataArrayList[RowCount].append(tmp)
                                            RowCount = RowCount + 1

                    count = count + 1

            f.close()

            #Store number of diameter bins
            print("Number of particle diameter bins: %d"%(RowCount))
            self.num_bins = RowCount

            #Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
            DataArrayList=list(itertools.chain.from_iterable(DataArrayList))

            #For Debugging purposes - print DataArray
            if(DebugFlag == 1):
                    for i in range(0,self.num_bins):
                            print("%s\n"%(str(DataArrayList[i][:])))

            #Now store as a numpy numeric array
            #DataArrayList has the following data
            #diameter       R1-pdf  R2-pdf  R3-pdf  ...RNumRadii-pdf

            #Now store as a numpy numeric array
            DataArray = np.zeros((self.num_bins,NumRadii+1))

            for i in range(0,self.num_bins):
                    for j in range(0,NumRadii+1):
                            DataArray[i][j] = float(DataArrayList[i][j])



            #Compute number weighted diameter PDF
            for i in range(0,self.num_bins):  #Initialize to 0 all elements
                    self.pdf.append(0)

            for i in range(0,self.num_bins):
                    self.horizontal_bins.append(DataArray[i][0]) #Store diameter bins

                    if(self.RadiusAverageFlag == 1):
                            for j in range(0,NumRadii):
                                    if(j==0):
                                            self.pdf[i] = DataArray[i][1]
                                    else:
                                            self.pdf[i] = self.pdf[i] + DataArray[i][j+1]
                                    
                    else:
                            self.pdf[i] = DataArray[i][1] #Store first PDF value



    
    def read_data_csv(self,FilePath,DebugFlag=0):
            import csv
            import itertools
            import string
            import numpy as np

            print("Reading Data From: %s"%(FilePath))
            #Open input file
            try:
                    f = open(FilePath,'r')
                    csv_data = csv.reader(f)
            except:
                    print("Failed to Input File!")

            DataArrayList = []
            count = 0
            for row in csv_data:
                    #Only store the numeric values and not the column header names if present in data file
                    if any( s.isdigit() for s in row):
                            DataArrayList.append([row])
                            
            f.close()

            #Store number of diameter bins
            self.num_bins = len(DataArrayList)
            print("Number of particle diameter bins: %d"%(self.num_bins))

            #Perform list comprehension to un-nest the list that was made(not sure why it is nested, but it is)
            DataArrayList=list(itertools.chain.from_iterable(DataArrayList))

            #For Debugging purposes - print DataArray
            if(DebugFlag == 1):
                    for i in range(0,self.num_bins):
                            print("%s\n"%(str(DataArrayList[i][:])))

            #Now store as a numpy numeric array
            #DataArrayList has the following data
            #diameter       R1-pdf  R2-pdf  R3-pdf  ...RNumRadii-pdf

            #Now store as a numpy numeric array
            DataArray = np.zeros((self.num_bins,len(DataArrayList[0])))

            for i in range(0,self.num_bins):
                    for j in range(0,len(DataArrayList[0])):
                            DataArray[i][j] = float(DataArrayList[i][j])

            #Compute number weighted diameter PDF
            for i in range(0,self.num_bins):  #Initialize to 0 all elements
                    self.pdf.append(0)

            for i in range(0,self.num_bins):
                    self.horizontal_bins.append(DataArray[i][0]) #Store diameter bins

                    if(self.RadiusAverageFlag == 1):
                            for j in range(0,len(DataArrayList[0])-1):
                                    if(j == 0 ):
                                            self.pdf[i] = DataArray[i][1]
                                    else:
                                            self.pdf[i] = self.pdf[i] + DataArray[i][j+1]
                                    
                    else:
                            self.pdf[i] = DataArray[i][1] #Store first PDF value




    def compute_widths(self):
        #Integrate data assuming that points are bin heights and widths are variable
        
        #Make sure to initialize to zero
        if(len(self.widths) > 0 ):
            for i in range(0,self.num_bins):
                self.widths[i] = 0		
        else:
            for i in range(0,self.num_bins):
                self.widths.append(0)

        for i in range(0,self.num_bins):
            if(i == 0):
                self.widths[i] =  0.5*(self.horizontal_bins[i+1] - self.horizontal_bins[i]) 
            elif(i==self.num_bins-1):
                self.widths[i] =  0.5*(self.horizontal_bins[i] - self.horizontal_bins[i-1]) 
            else:
                self.widths[i] = 0.5*(self.horizontal_bins[i+1] - self.horizontal_bins[i]) + 0.5*(self.horizontal_bins[i] - self.horizontal_bins[i-1]) 



    def normalize_pdf(self):
        Area = self.compute_histogram_area()
        for i in range(0,self.num_bins):
            self.pdf[i] = self.pdf[i]/Area


    def compute_histogram_area(self):
        C = 0 #Initialize integral to zero
        self.compute_widths() #Make sure the widths are defined
        for i in range(0,self.num_bins):
            C = C + self.pdf[i]*self.widths[i]

        return C


    def sample_from_pdf(self, NumSamples, RejectionM, show_samples=False, DebugFlag=0):
            import numpy as np
            import random
            import matplotlib.pyplot as plt
            #Generate a new set of samples based on the mass weighted PDF using the rejection sampling method
            print("Generating samples from the loaded distribution data")

            N = NumSamples #Number of samples to generate
            M = RejectionM #Parameter used for rejection sampling

            GeneratedData = []
            g_pdf = self.pdf  #Store the g distribution

            #Generate the empirical CDF of the normalized PDF
            g_cdf = np.zeros(self.num_bins)
            for i in range(1,self.num_bins):
                    g_cdf[i] = g_cdf[i-1] + g_pdf[i]*self.widths[i]

            g_cdf[-1] = 1 #Set the last value to be 1        

            if(DebugFlag == 1):
                    plt.figure()
                    plt.plot(self.horizontal_bins,g_pdf)
                    plt.xlabel(r'$Diameter (\mu meters)$')
                    plt.ylabel('PDF')
                    plt.show()


                    plt.figure()
                    plt.plot(self.horizontal_bins,g_cdf)
                    plt.xlabel(r'$Diameter (\mu meters)$')
                    plt.ylabel('CDF')
                    plt.show()

            count = 0
            while(count < N): #Loop until number of samples have been generated

                    #Generate a random number from the uniform distribution between 0 and 1
                    U_rejection = random.uniform(0, 1)

                    #Use inverse CDF method to sample from the PDF of g
                    U = random.uniform(0, 1)
                    for i in range(0,len(g_cdf)-1):

                            if(i == 0 and U < g_cdf[i]): #Just assume that sample was from the first bin
                                    d_sample = self.horizontal_bins[i]

                            elif(U >= g_cdf[i] and U <= g_cdf[i+1]):
                                    #print("Lower Bound: %10.6E\tUpper Bound: %10.6E"%(g_cdf[i],g_cdf[i+1]))

                                    #Linearly interpolate to obtain the value of the sample
                                    x_1 = self.horizontal_bins[i]
                                    x_2 = self.horizontal_bins[i+1]
                                    y_1 = g_cdf[i]
                                    y_2 = g_cdf[i+1]
                                    y_3 = U
                                    x_3 = x_1 +((y_3-y_1)/(y_2-y_1))*(x_2-x_1)
                                    d_sample = x_3 #Store sample

                    #print(d_sample)
                    #Evaluate the probability of the original distribution at the newly sampled value
                    for i in range(0,len(g_pdf)):
                            if(i == 0 and d_sample < (self.horizontal_bins[i]-0.5*self.widths[i])):
                                    probability_of_d_sample = 0
                            elif( d_sample >=(self.horizontal_bins[i]-0.5*self.widths[i]) and d_sample <(self.horizontal_bins[i]+0.5*self.widths[i]) ): 
                                    #Place sample into this probability range
                                    probability_of_d_sample = g_pdf[i]
                            elif(i == len(g_pdf) and d_sample >= (self.horizontal_bins[i]-0.5*self.widths[i])):
                                    probability_of_d_sample = 0


                    if(probability_of_d_sample == 0):
                            ratio = 0
                    else:
                            ratio = probability_of_d_sample/(M*probability_of_d_sample)
    
                    #print("Rejection Ratio: %10.6E"%(ratio))
                    if(ratio >= U_rejection):
                            GeneratedData.append(d_sample)
                            if(show_samples == True):
                                    print("Sample %d is: %10.6E"%(count+1,d_sample))
                            count = count + 1

            return GeneratedData



    def compute_volume_weighted_pdf(self,overwrite_pdfs= False):
        #Compute Volume Weighted PDF
        #Note that for cases where the density is constant, the mass and volume distributions are the same
        #The diameter histogram must already be defined.
        import math
        

        #To have a mass weighted PDF we scale the vertical axis to be the mass of the particles in that bin
        for i in range(0,self.num_bins):
            self.vol_pdf.append(0)

        C = 0 #Initialize integral to zero
        self.compute_widths() #Make sure the widths are defined
        for i in range(0,self.num_bins):
            C = C + self.pdf[i]*self.widths[i]*self.horizontal_bins[i]**3

        
        for i in range(0,self.num_bins):
            self.vol_pdf[i] = (self.horizontal_bins[i]**3)*self.pdf[i]/(C) #Store mass of particles in bin


        if(overwrite_pdfs == True):
            for i in range(0,self.num_bins):
                self.pdf[i] = self.vol_pdf[i]



    def add_data(self,horizontal_bin_values,pdf_values):
        #User wants to add data
        self.horizontal_bins=horizontal_bin_values[:]
        self.pdf=pdf_values[:]


    def rescale_bin_values(self,scaling_factor):
        #Provide a uniform scaling of the values in the horizontal bins array
        for i in range(0,self.num_bins):
            self.horizontal_bins[i] = self.horizontal_bins[i]*scaling_factor



    def plot_histogram(self):
        import matplotlib.pyplot as plt
        plt.figure()	
        plt.bar(self.horizontal_bins,self.pdf,self.widths, color='blue',fill=False,label="Histogram PDF")
        plt.xlabel(r'$Diameter (\mu meters)$')
        plt.ylabel('PDF')
        plt.show()

        

