import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT

### INPUT PATH
directory = '../../../MUSiC-LearningNP_DATAINPUT/Data_MUSNP_Feb22/WToMuNu_M-100_13TeV_P8/' 
subdirs   = [x[0] for x in os.walk(directory)]

data_labels = [
                #'DoubleEG', 
                #'MuonEG',
                #'EGamma', 
                'DoubleMuon' #for 4mu final state
]
mcsig_labels = [
                'GluGluH',
                'VBF_HToZZTo4L'
]
mcbkg_labels = [
                'GluGluToContin', 
                #'VBFToContinToZZTo4l', we ingore it!
                'ZZTo4L_13TeV_powheg',
                'TT_Mtt-1000toInf_13TeV_PH',
                'WWZ_4F_13TeV_AM'
]


# to encode the name of the process
code_keys = {
    'DoubleMuon'                 : 0,
    'DYJetsToLL'                 : 1,
    'GluGluToContinToZZTo4L'     : 2,
    'ZZTo4L_13TeV_powheg'        : 3,
    'GluGluHToZZTo4L_M125'       : 4,
    'VBF_HToZZTo4L_M125'         : 5,
    'TT_Mtt-1000toInf_13TeV_PH'  : 6
}
def Read_Branches_from_classtree(fileROOT,classtree):
    fileup=uproot.open(fileROOT)
    tree =fileup[classtree] 
    branches=tree.arrays()
    if branches['SumPt'].shape[0]==0:   
        print('Empty file!')
    else:
        return branches       # ! This gives the branches for ONE CLASS ! this is okay
                    

def Read_ListTree_from_file(fileROOT):
    fileup   = uproot.open(fileROOT)
    allClasses=fileup.keys()
    nonClasses=["ProcessName","EvCounts","TotalEvents","TotalEventsUnweighted"]
    classtree=[]
    for i in range(len(allClasses)):

        ### Remove Non-events classes
        if any(j in allClasses[i] for j in nonClasses):
            continue

        else:
            classtree.append(allClasses[i].replace(";1",""))
    return classtree
    

def Prepare_List_Of_File(FilesList,DirPath):
    for dirpath, dirnames, filenames in os.walk(Dirpath):
        for filename in [f for f in filenames if f.startswith("ECP")]:
            FilesList.append(os.path.join(dirpath, filename))
    return FilesList


#def Collect_from_file(fileROOT, classtree, y_label, subdir, SumPt, InvMass, MET, labels, weights, key_process):
    '''
    label: 0 if MC bkg
           1 if data
           2 if MC sig (not needed for searches, maybe used to set limits)
    key_process : string ID for the process (in subdir)

    cosThetaStar, cosTheta1, cosTheta2, PHI, PHI1 : for theta and phi definition see AN
    '''
 #   print("DEB2.5")

    ### Opening  the root file 
   # fileup   = uproot.open(fileROOT)
  #  print("DEB3")
        
   # print('%s loaded. Length: %i'%(fileROOT.split('/')[-1], len(SumPt)))
   # return

if __name__ == '__main__':

    ###Creating lists for launch the command on multi files
    DirPath = "/user/vigilante/MUSIC_TESTECP_Feb22/mc"
    FilesList = []

    ### Initialize some variables:
    Lumi= 41480.
    
    ######## Looping over all FOLDERS to find MC/data samples ########
    
    for subdir in subdirs:
        #print('DEB1.1 printing    subdir: ')
        #print(subdir)
        label = 0
        ###Check if is a MCbkg samples, a MC signal or a data samples
        #for ext in mcbkg_labels:
            #print('mcbkg_label is: ')
            #print ext
        #if any(ext in subdir for ext in mcbkg_labels):
        #    label = 0
        #elif any(ext in subdir for ext in data_labels):
        #    label = 1    
        #elif any(ext in subdir for ext in mcsig_labels):
        #    label = 2
        #else: continue
        
        if any(ext in subdir for ext in data_labels):
            label = 1
        else:
            label = 0
        #print glob.glob(subdir+"/ECP*")
        if len(glob.glob(subdir+"/ECP*")) == 0:
            continue
            
        ######## Looping over all ROOT files inside the subdir ########

        for fileROOT in glob.glob('%s/ECP*'%(subdir)):
            
            # Read the Classes from each ROOT file
            ListTree_classes=[]
            ListTree_classes = Read_ListTree_from_file(fileROOT)   # ! The function returns classtree 

            # Read nEventsUnweighted from each ROOT file
            inFile = ROOT.TFile.Open(fileROOT,"READ")
            evWeights =  inFile.Get("TotalEvents")
            inFile.Close()
            nEv = evWeights[0]
            print fileROOT

            fileup=uproot.open(fileROOT)

            ########   Looping over all classes in the ROOT file ########

            for i  in range(len(ListTree_classes)):
                
                classtree=ListTree_classes[i]            # ! Define the class

                branches=[]                              # ! Read the branches from this specific class
                branches=Read_Branches_from_classtree(fileROOT,classtree)
                entries_SumPt=len(branches['SumPt'])
                print("--------------------------------------------------------------------------------------------")
                #print(branches)                          # ! This prints the branches for each class. This is okay
                                
                fileH5_name='../../../MUSiC-LearningNP_DATAOUTPUT/Dir_OUT_FILEH5/H5'+classtree+'.h5'

                ### Cleaning list variables
                SumPt      = []
                InvMass    = []
                MET        = []
                labels     = []
                weights    = []
                keys       = []
                keys_int   = []

               
                ### Get variables to fill lists above
 
                for i in range(entries_SumPt):
                    #key_process.append(subdir.split('/')[-1])
                    #labels.append(label)
                    weights.append(branches['Weight'][i])
                    SumPt.append(branches['SumPt'][i])
                    InvMass.append(branches['InvMass'][i])
                    MET.append(branches['MET'][i])
                            
                print('%s loaded. Length: %i'%(classtree.split('/')[-1],len(SumPt)))
                print(SumPt)    
                            
                for k in keys:
                    for c in list(code_keys.keys()):
                        if c in k: 
                            keys_int.append(code_keys[c])
                            continue
                                

                ### Evaluating the weight
                for j in weights:
                    new_weight = j * Lumi / nEv
                    if len(weights)%1000==1:
                        print new_weight
                
                ### Create h5 file, or append new variables if the file already exists
                if os.path.exists(fileH5_name)==False:
                    with h5py.File(fileH5_name, 'w') as f:
                        sumpt=f.create_dataset('SumPt', data=SumPt, maxshape=(None))
                        print('Shape of SumPt is '+str(sumpt.shape))
                        invmass=f.create_dataset('InvMass', data=InvMass, maxshape=(None))
                        print('Shape of InvMass is '+str(invmass.shape))
                        met=f.create_dataset('MET',data=MET, maxshape=(None))
                        weights=f.create_dataset('Weights',data=weights,maxshape=(None))
                        f.close()
                        fileH5_name=''
                        classtree=''
                else:
                    with h5py.File(fileH5_name, 'a') as f:
                        #sumpt=f['SumPt']
                        #sumpt.resize(sumpt.shape[0]+1, axis=0)
                        #print('NEW Shape of SumPt is '+str(sumpt.shape))
                        f.close()
            
                        fileH5_name=''
                        classtree =''
        
    
