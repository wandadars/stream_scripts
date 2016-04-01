class myClass:
	
	def __init__(self,ListA=None,ListB=None,ListCount=0):
		self.ListA=[] if ListA is None else ListA[:]
		self.ListB=[] if ListB is None else ListB[:]
		self.ListCount = ListCount

	def add_data(self,ElementA,ElementB):
		self.ListA.append(ElementA)
		self.ListB.append(ElementB)
		self.ListCount = self.ListCount + 1
    
	def print_data(self):
		print("Number of elements in this object is: %d"%self.ListCount)
		print("List A contents\n%s"%self.ListA)
		print("List B contents\n%s\n"%self.ListB)
	
	def addTogether(self,other):
		TestData = myClass(self.ListA,self.ListB,self.ListCount)

		for i in range(0,other.ListCount):
			TestData.add_data(other.ListA[i],other.ListB[i])

		return(myClass(TestData.ListA,TestData.ListB,TestData.ListCount))

import random

ObjectArray = [myClass() for i in range(2)]
#Loop over object array and fill each object with some data
for i in range(0,2):

	NumData = int(10*random.random())
	for m in range(0,NumData):
		#Generate some junk data to insert into the list of this object
		ListAData = int(10*random.random())
		ListBData = int(10*random.random())

		ObjectArray[i].add_data(ListAData,ListBData)

ObjectArray[0].print_data()
ObjectArray[1].print_data()

NewData = ObjectArray[0].addTogether(ObjectArray[1])
NewData.print_data()

ObjectArray[0].print_data()
ObjectArray[1].print_data()

