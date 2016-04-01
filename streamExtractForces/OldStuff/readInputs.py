def getBCsFromFile(MainData_filename):
   "Pulls the detected boundary conditions that are present in file and puts into a list."

   BaseString="setting boundary condition " #all BCs have the before the specification
   DetectedFirstEntry = False

   #open file if file exists, oehrwise throw exception
   try:
     f=open(MainData_filename)
   except IOError as e:
     print "I/O error({0}): {1}".format(e.errno, e.strerror)
     raise

   BC=[]
   for Line in f:

     #Check to see if the first matching line has been found
     if (Line.find(BaseString) >=0 and DetectedFirstEntry==False):
       DetectedFirstEntry=True


     #Check to see if next entry does not contain the substring i.e. end of the section
     if( Line.find(BaseString) == -1 and DetectedFirstEntry==True):
        f.close()
        break


     if(DetectedFirstEntry == True):
       Line = Line.rstrip()

       Temp=Line[len(BaseString):]

       #Debug
       #print(Temp)

       #Append the Boundary condition to the BC list
       BC.append(Temp)

   return BC


def getMarkersFromFile(MainData_filename,BCs):
   "Pulls the detected boundary markers that are present in file and puts into a list."

   BaseString="Integrated Boundary Data ("
   DetectedFirstEntry = False
   EndString="R:  "

   #open file if file exists, oehrwise throw exception
   try:
     f=open(MainData_filename)
   except IOError as e:
     print "I/O error({0}): {1}".format(e.errno, e.strerror)
     raise
 
   #Debug
   #print(BCs)

   Markers=[]
   for Line in f:

     #Check to see if the first matching line has been found
     if (Line.find(BaseString) >=0 and DetectedFirstEntry==False):
       DetectedFirstEntry=True


     #Check to see if next entry contains R:  i.e. end of the integrated force datasection
     if( Line.find(EndString) >=0 and DetectedFirstEntry ==True):
        f.close()
        break


     if(DetectedFirstEntry == True and Line.find(BaseString) >=0):

       Line=Line.rstrip() #remove the newline character

       #Trim the basename string off of the line
       Marker=Line[len(BaseString):-1]

       #Only store the entry if it is not in the list of boundary conditions
       if Marker not in BCs:
         #Append the entry to the list of markers
         Markers.append(Marker)

         #Debug
         # print(Marker)

   return [Markers]





