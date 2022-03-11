import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT

### INPUT PATH
directory = '../../../MUSiC-LearningNP_DATAINPUT/Data_MUSNP_Feb22/WToMuNu_M-100_13TeV_P8/' 
subdirs   = [x[0] for x in os.walk(directory)]


### Defining the labels for background MC and data samples
data_labels = [ #'DoubleEG', 'MuonEG', 'EGamma', 
                'DoubleMuon'] #for 4mu final state

mcsig_labels = ['GluGluH','VBF_HToZZTo4L']

mcbkg_labels = ['GluGluToContin', #'VBFToContinToZZTo4l', we ingore it!
                'ZZTo4L_13TeV_powheg','TT_Mtt-1000toInf_13TeV_PH','WWZ_4F_13TeV_AM']


### Encoding processName as integer
code_keys = {
    'DoubleMuon'                 : 0,
    'DYJetsToLL'                 : 1,
    'GluGluToContinToZZTo4L'     : 2,
    'ZZTo4L_13TeV_powheg'        : 3,
    'GluGluHToZZTo4L_M125'       : 4,
    'VBF_HToZZTo4L_M125'         : 5,
    'TT_Mtt-1000toInf_13TeV_PH'  : 6
}

def Create_dataset(dsetName,datasetName,dataName):
    
    dsetName=f.create_dataset(datasetName, data=dataName,chunks=(len(dataName),), maxshape=(None,))
    Set_attributes(dsetName)
    print('')
    print('Shape of '+datasetName+ ' dataset is '+str(dsetName.shape))
    print('Attributes of '+datasetName+' are'+str(dsetName.attrs.items()))
    return

   
def Append_to_dataset(dsetName,datasetName,dataName):

    dsetName=f[datasetName]
    print('')
    print('Shape of '+datasetName+' dataset was '+str(dsetName.shape))
    old_shape=dsetName.shape[0]                                      # ! First integer of shape=(,) for previous dataset
    
    print('We want to extend the dataset by '+str(len(dataName)))
    dsetName.resize((dsetName.shape[0]+len(dataName),))                    # ! Resizing the dataset. This is okay
    new_shape=dsetName.shape[0]                                      # ! First integer of shape=(,) for resized dataset
    entry_point=new_shape-old_shape
    print('The entry point for new data is at position '+str(entry_point))
    dsetName[-entry_point:]=dataName                                  # ! Appending new data to the end of the dataset.
    print('New shape of '+datasetName+' dataset is '+str(dsetName.shape))
    print('------------New dataset is now-----------------')
    print(list(dsetName))
    return


def Set_attributes(dset):
    
    dset.attrs['ProcessName']           = str(pName)
    dset.attrs['TotalEvents']           = tEv
    dset.attrs['evCount']               = evCounts
    dset.attrs['totalEventsUnweighted'] = tEvUnweighted
    dset.attrs['label']                 = label
    return        


def Read_Branches_from_classtree(fileROOT,classtree):

    fileup=uproot.open(fileROOT)
    tree =fileup[classtree] 
    branches=tree.arrays()
    if branches['SumPt'].shape[0]==0:   
        print('Empty file!')
    else:
        return branches       # ! This gives the branches for ONE CLASS. This is okay
                    

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
    return classtree          # ! This gives the class list for each ROOT file. This is okay
    

def Prepare_List_Of_File(FilesList,DirPath):

    for dirpath, dirnames, filenames in os.walk(Dirpath):
        for filename in [f for f in filenames if f.startswith("ECP")]:
            FilesList.append(os.path.jsoin(dirpath, filename))
    return FilesList


#########################################################################################################################


if __name__ == '__main__':

    ###Creating lists for launch the command on multi files
    DirPath = "/user/vigilante/MUSIC_TESTECP_Feb22/mc"
    FilesList = []

    ### Initialize some variables:
    Lumi= 41480.
    
   ######## Looping over all FOLDERS to find MC/data samples ########
    
    for subdir in subdirs:
      
        ###Check if is a MCbkg (background) samples, or data samples
        label = 0
        
        if any(i in subdir for i in data_labels):
            label = 1
        else:
            label = 0
        if len(glob.glob(subdir+"/ECP*")) == 0:
            continue
            
        ######## Looping over all ROOT files inside the subdir ########

        for fileROOT in glob.glob('%s/ECP*'%(subdir)):
            
            fileup=uproot.open(fileROOT)

            # Read the Classes from each ROOT file
            ListTree_classes  = []
            ListTree_classes  = Read_ListTree_from_file(fileROOT)   # ! The function returns classtree 

            # Read attributes from each ROOT file
            inFile            = ROOT.TFile.Open(fileROOT,"READ")
            totalEv           = inFile.Get("TotalEvents")
            processName       = inFile.Get("ProcessName")
            evCount           = inFile.Get("EvCounts")
            totalEvUnweighted = inFile.Get("TotalEventsUnweighted")
            inFile.Close()

            pName         = processName[0]
            tEv           = totalEv[0]
            evCounts      = evCount[0]
            tEvUnweighted = totalEvUnweighted[0]
                
            print('------------------------------------------------------')
            print(fileROOT)
            
            ###  Looping over all classes in the ROOT file

            for i  in range(2):
                
                classtree=ListTree_classes[i]                              # ! Define a specific class
                branches=[]                              
                branches=Read_Branches_from_classtree(fileROOT,classtree)  # ! Read the branches from this class
                entries_SumPt=len(branches['SumPt'])
                #print(branches)                                           # ! Prints the branches for each class. This is okay
                                
                fileH5_name='../../../MUSiC-LearningNP_DATAOUTPUT/Dir_OUT_FILEH5/H5'+classtree+'.h5'

                ### Creating/Cleaning the arrays for the h5 file
                SumPt      = []
                InvMass    = []
                MET        = []
                weights    = []
        
                ### Reading variables from branches to fill arrays above
                for i in range(entries_SumPt):
                    SumPt.append(branches['SumPt'][i])
                    MET.append(branches['MET'][i])
                    InvMass.append(branches['InvMass'][i])
                    weights.append(branches['Weight'][i])
                
                print('')
                print('-------------------------------------------------')
                print('%s loaded. Length: %i'%(classtree.split('/')[-1],len(SumPt))) # ! Prints class name and number of events in that class
                #print(SumPt)                                                        # ! Prints the array with all SumPt values. This is okay
                 
                ### Storing the keys
                #for k in keys:
                    #for c in list(code_keys.keys()):
                        #if c in k: 
                            #keys_int.append(code_keys[c])
                            #continue
                                

                ### Redifining the weight
                for j in weights:
                    new_weight = j * Lumi / tEv
                    if len(weights)%1000==1:
                        print new_weight                                            
                
                ### Create h5 file, or append new variables if the file already exists
                if os.path.exists(fileH5_name)==False:
                    with h5py.File(fileH5_name, 'w') as f:
 
                        Create_dataset('sumpt','SumPt',SumPt)
                        Create_dataset('invmass','InvMass',InvMass)
                        Create_dataset('met','MET',MET)
                        Create_dataset('Weights','weights',weights)
                        
                        #sumpt=f.create_dataset('SumPt', data=SumPt,chunks=(len(SumPt),), maxshape=(None,))
                        #Set_attributes(sumpt)
                        #invmass=f.create_dataset('InvMass', data=InvMass,chunks=(len(InvMass),), maxshape=(None,),compression='gzip')
                        #Set_attributes(invmass)
                        #met=f.create_dataset('MET',data=MET, chunks=(len(MET),), maxshape=(None,),compression='gzip')
                        #Set_attributes(met)
                        #Weights=f.create_dataset('Weights',data=weights,chunks=(len(weights),), maxshape=(None,),compression='gzip')
                        #Set_attributes(Weights)
                        
                        f.close()
                        fileH5_name=''
                        classtree=''
                else:
                    with h5py.File(fileH5_name, 'a') as f:
                       
                        Append_to_dataset('sumpt','SumPt',SumPt)
                        Append_to_dataset('invmass', 'InvMass',InvMass)
                        Append_to_dataset('met','MET',MET)
                        Append_to_dataset('Weights','weights',weights)
                        
                        ##
                        #sumpt=f['SumPt']
                        #print('')
                        #print('sumpt.shape was '+str(sumpt.shape))
                        #old_shape=sumpt.shape[0]                                      # ! First integer of shape=(,) for previous dataset
                        #print('We want to extend its shape by '+str(len(SumPt)))
                        #sumpt.resize((sumpt.shape[0]+len(SumPt),))                    # ! Resizing the dataset. This is okay
                        #new_shape=sumpt.shape[0]                                      # ! First integer of shape=(,) for resized dataset
                        #entry_point=new_shape-old_shape
                        #print('entry point for new data ia at '+str(entry_point))
                        #sumpt[-entry_point:]=SumPt                                  # ! Appending new data to the end of the dataset. 
                        #print('New Shape of sumpt dataset is '+str(sumpt.shape))
                        #print('AAAAAAAAAAAAAAAAAAAAAAAAAAAA')
                        #print(list(sumpt))
                        
                        #invmass=f['InvMass']
                        #print('invmass.shape was '+str(invmass.shape))
                        #print('We want to extend its shape by '+str(len(InvMass)))
                        #invmass.resize((invmass.shape[0]+len(InvMass),))
                        #print('New shape of invmass dataset is '+str(invmass.shape))

                        #met=f['MET']
                        #print('')
                        #print('met.shape was '+str(met.shape))
                        #met.resize((met.shape[0]+len(MET),))
                        #print('New shape of met dataset is '+str(met.shape))
                        

                        #Weights=f['Weights']
                        #Weights.resize((Weights.shape[0]+len(weights),))

                        f.close()
            
                        fileH5_name=''
                        classtree =''
        
    
