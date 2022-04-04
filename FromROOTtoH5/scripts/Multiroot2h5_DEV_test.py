import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT
import argparse

# Defining the labels for background MC and data samples
data_labels = ['SingleMuon', 'SingleElectron', 'SinglePhoton', 'DoubleMuon','DoubleEG'] 

def Create_dataset(dsetName,datasetName,dataName):
    if len(dataName)!=0:
        dsetName=f.create_dataset(datasetName, data=dataName,chunks=(len(dataName),), maxshape=(None,))
        Set_attributes(dsetName)
        print('')
        print('Shape of '+datasetName+ ' dataset is '+str(dsetName.shape))
        #print('Attributes of '+datasetName+' are'+str(dsetName.attrs.items()))
        return
    else:
        return

   
def Append_to_dataset(dsetName,datasetName,dataName):
    if len(dataName)!=0:
        dsetName=f[datasetName]
        print('')
        print('Shape of '+datasetName+' dataset was '+str(dsetName.shape))
        #old_shape=dsetName.shape[0]                                                  # ! shape=(,) for previous dataset

        print('We want to extend the dataset by '+str(len(dataName)))
        dsetName.resize((dsetName.shape[0]+len(dataName),))                          # ! Resizing the dataset. This is okay
        new_shape=dsetName.shape[0]                                                  # ! shape=(,) for resized dataset
        entry_point=new_shape-len(dataName)

        print('The entry point for new data is at position '+str(entry_point))
        dsetName[-len(dataName):]=dataName                                             # ! Appending new data to the end of the dataset.
        print('New shape of '+datasetName+' dataset is '+str(dsetName.shape))
        return
    else:
        return


def Set_attributes(dset):
    
    dset.attrs['ProcessName']           = str(pName)
    dset.attrs['TotalEvents']           = tEv
    dset.attrs['evCount']               = evCounts
    dset.attrs['totalEventsUnweighted'] = tEvUnweighted
    dset.attrs['label']                 = label
    return        


def Read_Branches_from_classtree(fileup,classtree):

    tree =fileup[classtree] 
    branches=tree.arrays()
    if branches['SumPt'].shape[0]==0:   
        print('Empty file!')
    else:
        return branches                                        # ! Returns the branches for ONE CLASS
                    

def Read_ListTree_from_file(fileup):

    allClasses=fileup.keys()
    nonClasses=["ProcessName","EvCounts","TotalEvents","TotalEventsUnweighted"]
    classtree=[]

    for i in range(len(allClasses)):
        if any(j in allClasses[i] for j in nonClasses):         # ! Removes non-events classes
            continue
        else:
            classtree.append(allClasses[i].replace(";1",""))
    return classtree                                            # ! Returns the class list for each ROOT file
    

#--------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    
    # Defining the input and output directories
    parser = argparse.ArgumentParser()   
    parser.add_argument('-in','--inputDir',     type=str, help="Directory where the process folders are stored.", required=True)
    parser.add_argument('-out','--outputDir',   type=str, help="Directory to store the h5 files.", required=True)
    #parser.add_argument('-h','--dryrun',   type=int,default=0, help="Launch a dryrun.", required=False)
    args = parser.parse_args()
    
    inputDir  = args.inputDir
    #dryo  = args.dryrun
    outputDir = args.outputDir
   
    # Initializing some variables
    Lumi = 41480.
    
    # Looping over all FOLDERS to find MC/data samples 
    processDirList = [x[0] for x in os.walk(inputDir)]
    processDir     = []
    select_folders = ["AnalysisOutput"]
    #print('')
    #print('All possible directories are ')
    #print(processDirList)
    
    for i in range(len(processDirList)):
        if any(j in processDirList[i] for j in select_folders):
            processDir.append(processDirList[i])                           # ! Defines all AnalysisOutput folders for all processes
        else:
            continue

    print('')
    print('ROOT files are collected from directories ')
    print('')
    print(processDir)                                                  

    # Looping over all AnalysisOutput folders
    
    for i in range(len(processDir)):                 # for each folder of processDir we do:
        
        subdir=processDir[i]                         # define the subdirectories to get ROOT files from
        print('')
        print('---------------------------------------------------------------------------------')
        print('')
        print('')
        print('Entering the subdirectory: '+subdir)
        print('')

        # Checking if is a MCbkg (background) samples, or data samples
        label = 0
        if any(i in subdir for i in data_labels):
            label = 1
        else:
            label = 0
        if len(glob.glob(subdir+"/ECP*")) == 0:
            continue
            
        # Looping over all ROOT files inside the subdir 

        for fileROOT in glob.glob('%s/ECP*'%(subdir)):   # get the ROOT files from the subdirectory
            
 
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
            
            with uproot.open(fileROOT) as fileup:
            
                # Read the Classes from each ROOT file
                ListTree_classes  = []
                ListTree_classes  = Read_ListTree_from_file(fileup)   # ! The function returns classtree 
                                 
                print('')    
                print('------------------------------------------------------------------------------------------------------------')          
                print('')
                print('')
                print('Loading ROOT file: '+fileROOT)
                print('')
            
                ###  Looping over all classes in the ROOT file
            
                for i  in range(len(ListTree_classes)):
                    
                    classtree=ListTree_classes[i]                              # ! Define a specific class
                    branches=[]                              
                    branches=Read_Branches_from_classtree(fileup,classtree)  # ! Read the branches from this class
                    if branches is not None:
                        entries_SumPt=len(branches['SumPt'])
                    else:
                        print('! This file is empty. No entries appended to hdf5 file !')
                        print('')
                    #print(branches)                                           # ! Prints the branches for each class. This is okay
                
                
                    fileH5_Dir = outputDir+'/H5'+classtree+'.h5'
                                 
                    ### Creating/Cleaning the arrays for the h5 file
                    SumPt      = []
                    InvMass    = []
                    MET        = []
                    weights    = []
        
                    ### Reading variables from branches to fill arrays above
                    for i in range(entries_SumPt):
                        if branches is not None:
                            SumPt.append(branches['SumPt'][i])
                            MET.append(branches['MET'][i])
                            InvMass.append(branches['InvMass'][i])
                            weights.append(branches['Weight'][i])
                
                    print('')
                    print('------------------------------------------------------------------')
                    print('')
                    print('%s loaded. Length: %i'%(classtree.split('/')[-1],len(SumPt))) # ! Prints class name and number of events 
                    print('')                       
                 
                    # Redifining the weight
                    for j in weights:
                        new_weight = j * Lumi / tEv
                        if len(weights)%1000==1:
                            print new_weight                                            
                
                    # Creating h5 files, or appending new data if the file already exists
                
                    # ! We want 1 single h5 file per classes (even if the data is coming from different process folders!) ! #
              

                

                    print('')
                    print(" ! The following ROOT file has been closed !")
                    print(fileROOT)
                    print('')
                    print("fileH5_Dir : ")
                    print(fileH5_Dir)
                    print('')
                    print('-------------------------------------------------------------------------')

                    if os.path.exists(fileH5_Dir)==False:
                        with h5py.File(fileH5_Dir, 'w') as f:
                        
                            Create_dataset('sumpt','SumPt',SumPt)
                            Create_dataset('invmass','InvMass',InvMass)
                            Create_dataset('met','MET',MET)
                            Create_dataset('Weights','weights',weights)
                            f.close()
                            print('')
                            print('! Sucessfully created '+fileH5_Dir)
                            print ('')
                        
                            fileH5_Dir   = ''
                            classtree    = ''
                
                    else:
                        with h5py.File(fileH5_Dir, 'a') as f:
                            #if(dryo!=0):
                            Append_to_dataset('sumpt','SumPt',SumPt)
                            Append_to_dataset('invmass', 'InvMass',InvMass)
                            Append_to_dataset('met','MET',MET)
                            Append_to_dataset('Weights','weights',weights)
                            f.close()
                        print('')
                        print('! Sucessfully appended new data to '+fileH5_Dir)
                        print ('')

                        fileH5_Dir   = ''
                        classtree    = ''
              
