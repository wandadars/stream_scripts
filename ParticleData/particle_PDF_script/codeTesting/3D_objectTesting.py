class myClass:
	def __init__(self,ListA=[],ListB=[],ListCount=0):
		self.ListA = ListA
		self.ListB = ListB
		self.ListCount = ListCount

	def add_data(self,ElementA,ElementB):
		self.ListA.append(ElementA)
		self.ListB.append(ElementB)
		self.ListCount = self.ListCount + 1
    
	def check_data(self):
		if(len(self.ListA) != self.ListCount):
			print("Error: Unaccounted for Data in Object!")
			print("Object has %d elements. Thinks it has %d"%(len(self.ListA),self.ListCount))
	

import random


ObjectArray = [[[myClass() for k in range(4)] for j in range(3)] for i in range(2)]
#Print addresses of object array
print("Addresses of the individual object elements in the 3D list ")
for i in range(0,2):
        for j in range(0,3):
                for k in range(0,4):
			print(ObjectArray[i][j][k])
   
#Loop over object array and fill each object with some data
for i in range(0,2):
	for j in range(0,3):
		for k in range(0,4):

			NumData = int(10*random.random())

			for m in range(0,NumData):

				#Generate some junk data to insert into the list of this object
				ListAData = int(10*random.random())
				ListBData = int(10*random.random())

				ObjectArray[i][j][k].check_data()
				ObjectArray[i][j][k].add_data(ListAData,ListBData)
				ObjectArray[i][j][k].check_data()







