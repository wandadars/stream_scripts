def compute_filename_numbers(start, stop, step):
    num_files = (stop - start)/step
    file_indicies = []
    iterate=start
    for i in range(0,num_files):   #make list of timestamps
        file_indicies.append(iterate)
        iterate = iterate + step
    return file_indicies



def write_output_data(AVG_PDF,PDF_X_Coords,PDF_Y_Coords):
    print("Writing Output Data")

    #Create output directory and enter the directory
    FilePathBase =os.getcwd()
    OutPutDir = FilePathBase +"/particle_PDF_data"
    if not os.path.exists(OutPutDir):
        os.makedirs(OutPutDir)
        os.chdir(OutPutDir)
    else:
        os.chdir(OutPutDir)

    #Write the output so that all of the Y data for a particular X bin is contained within 1 file. The file will match in essence the
    #format used for the experimental data file so that post-processing the data will be made faster.
    for i in range(0,nXBins):
        print "Writing data for X bin ",i+1," located at: ",PDF_X_Coords[i]

        OutputFileName = CaseName + "_PDF_" + '%s_%4.2f_Data'%('XOverD',PDF_X_Coords[i]/Dl) + ".txt"
        f_output = open(OutputFileName,"w")

        f_output.write("%s\t%s %10.6E\n"%("X Coordinate","X/D = ",PDF_X_Coords[i]/Dl))
        
        f_output.write("\n")
        f_output.write("\n")
        f_output.write("\n")
        f_output.write("\n")
        
        f_output.write("%s\t%s\t"%("Radial Coordinate","r/D = ") )
        
        for j in range(0,len(PDF_Y_Coords)):
            f_output.write("%10.6E\t"%(PDF_Y_Coords[j]/Dl))

        f_output.write("\n")
        f_output.write("\n")
        f_output.write("\n")
        f_output.write("\n")	

        if(BinFlag == 1):
            for m in range(0,nDBins):
                f_output.write("%10.6E\t"%( 0.5*(float(UserDefinedBins[0][m]) + float(UserDefinedBins[1][m]) ) ) )
                for j in range(0,nYBins):   #used to be nYBins
                    #print "\tWriting data for Transverse bin ",j+1," located at: ",PDF_Y_Coords[j]
                    f_output.write("%10.6E\t"%( float(AVG_PDF[i][j].ParticlesPerParcel[m]) ))
        
                f_output.write("\n")
                f_output.write("\n")

        f_output.close()
