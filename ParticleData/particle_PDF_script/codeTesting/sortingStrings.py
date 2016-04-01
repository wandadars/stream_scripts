
from operator import itemgetter

ListA = ["5.0e-0","2.0E+0", "3.0E+0", "4.0", "1"]
ListB = [1.0E+0,2.0E+0, 3.0E+0, 4.0, 5.0E+0]


ListA = ["5.0e-1","2.0E-1", "3.0E-1", ".40", "0.1"]
ListB = [3.0e-1,2.0E-01, 5.0E-1, .10,0.4]

print(ListA)
print(ListB)

print(type(ListA[0]))
print(type(ListB[0]))

NumElements = len(ListA)

#CheckSum for error checking
CheckSum1 = 0.0
for i in range(0,NumElements):
	CheckSum1 = CheckSum1 + float(ListA[i])

#Combine the two object data lists into a 2D list of dimension NumElements x 2
alist = []
for i in range(0,NumElements):
	alist.append([])
	alist[i].append(ListA[i])
	alist[i].append(ListB[i])
	alist[i].append(float(ListA[i]))

print("Pre-sort list")
for i in range(NumElements):
	print("%s\t%s\t%f"%(alist[i][0],alist[i][1],alist[i][2]))

#Sorts from low to high based on the ParticlesPerParcel list
#alist.sort(key=itemgetter(0), reverse=True) #sort based on first column
#alist.sort(key=itemgetter(1), reverse=False) #sort based on second column
alist.sort(key=itemgetter(2), reverse=False) #sort based on third column

print("Post-sort list")
for i in range(NumElements):
	print("%s\t%s"%(alist[i][0],alist[i][1]))

#Re-distribute the data from the 2D sorted list back into the individual list data sets
for i in range(NumElements):
	ListA[i] = alist[i][0]
	ListB[i] = alist[i][1]


print(ListA)
print(ListB)

print(type(ListA[0]))
print(type(ListB[0]))

#CheckSum for error checking
CheckSum2 = 0.0
for i in range(0,NumElements):
	CheckSum2 = CheckSum2 + float(ListA[i])

if( abs(CheckSum1 - CheckSum2) >= 1e-6):
	print("ERROR - Sorting of Parcel Data process has lost data! Discrepancy is: %10.6E"%(abs(CheckSum1 - CheckSum2)))

