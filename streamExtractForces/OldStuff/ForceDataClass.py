class MarkerForce():
   """A class to hold force data for all times on a boundary"""

   def __init__(self,Name='Nothing'):
      self.Name=Name

      self.ForceData=[]
      for i in xrange(9):
         self.ForceData.append([])

   def AddForces(self,AllForce):
      for i in xrange(9):
             self.ForceData[i].append(AllForce[i])

   def SetName(self,UserName):
      self.Name=UserName

   def GetForceDims(self)
      numrows = len(self.ForceData)  
      numcols = len(self.ForceData[0])


