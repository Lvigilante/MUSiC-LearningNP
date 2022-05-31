import h5py, glob
import math
import uproot
import os



objty=["Ele", "Muon", "Jet","bjet","GammaEB"]
MaxOB=[2,2,2,2,2]
base="Rec"
f=";"


#m=['{x}Ele_{x}Muon_{x}Jet_{x}bjet_{x}GammaEB']


#Creating the list
r=['{}Ele_{}Muon_{}GammaEB_{}Jet_{}bjet'.format(x,y,z,a,b) for x in range(3) for y in range(3) for z in range(3) for a in range(3) for b in range(3)]
#for x in range(2):
#    m.format(x)
print r
#print m
p=["0Ele","0Muon","0Jet","0bJet","0GammaEB"]
t=[]
#removing the 0Object from classes of the list
temp1=""
temp2=""
for cla in r:
    temp1=cla
    for s in p:
        if s in temp1:
            print "ma"
            temp1=temp1.replace(s,"")
            print temp1
    if "__" in temp1:
        temp1= temp1.replace("__","_")
    if temp1.endswith("_"):
        temp1= temp1.replace("_","")
    print temp1
    t.append(temp1)
    temp1=""

print "after**********************"
print t
