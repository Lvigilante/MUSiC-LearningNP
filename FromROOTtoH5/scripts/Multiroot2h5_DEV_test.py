import numpy as np
import h5py, glob, math, uproot, os, ROOT, argparse


#############################################################################################################

#############################################################################################################


# Defining the labels for background MC and data samples
data_labels = ['SingleMuon', 'SingleElectron', 'SinglePhoton', 'DoubleMuon','DoubleEG'] 

def Create_dataset(dsetName,datasetName,dataName):
    if len(dataName)!=0:
        dsetName = f.create_dataset(datasetName, data=dataName,chunks=(len(dataName),), maxshape=(None,))
#        print('')
#        print('Shape of '+datasetName+ ' dataset is '+str(dsetName.shape))
        return
    else:
        return

   
def Append_to_dataset(dsetName,datasetName,dataName):
    if len(dataName)!=0:
        dsetName = f[datasetName]
#        print('')
#        print('Shape of '+datasetName+' dataset was '+str(dsetName.shape))
#        old_shape=dsetName.shape[0]                            # ! shape=(,) for previous dataset

#        print('We want to extend the dataset by '+str(len(dataName)))
        dsetName.resize((dsetName.shape[0]+len(dataName),))     # ! Resizing the dataset. This is okay
        new_shape   = dsetName.shape[0]                         # ! shape=(,) for resized dataset
        entry_point = new_shape-len(dataName)

#        print('The entry point for new data is at position '+str(entry_point))
        dsetName[-len(dataName):] = dataName                    # ! Appending new data to the dataset.
#        print('New shape of '+datasetName+' dataset is '+str(dsetName.shape))
        return
    else:
        return


def Read_Branches_from_classname(fileup,classname):

    tree     = fileup[classname] 
    branches = tree.arrays()
    if branches['SumPt'].shape[0]==0:   
        print('Empty file!')
    else:
        return branches           # ! Returns the branches for ONE CLASS
                    

def Read_ListTree_from_file(fileup):

    allClasses  = fileup.keys()
    nonClasses  = ["ProcessName","EvCounts","TotalEvents","TotalEventsUnweighted"]
    classtree   = []

    for i in range(len(allClasses)):
        if any(j in allClasses[i] for j in nonClasses):         # ! Removes non-events classes
            continue
        else:
            classtree.append(allClasses[i].replace(";1",""))
    return classtree                                            # ! Returns the class list for each ROOT file
    

#############################################################################################################

#############################################################################################################


if __name__ == '__main__':
    
    # Defining the input and output directories
    parser = argparse.ArgumentParser()   
    parser.add_argument('-in','--inputDir',     type=str, help="Directory where the process folders are stored.", required=True)
    parser.add_argument('-out','--outputDir',   type=str, help="Directory to store the h5 files.", required=True)
#   parser.add_argument('-h','--dryrun',   type=int,default=0, help="Launch a dryrun.", required=False)

    args = parser.parse_args()

#   dryo  = args.dryrun
    inputDir  = args.inputDir
    outputDir = args.outputDir
   
    Lumi = 41480.       # Defining the integrated luminosity

    processDirList = [x[0] for x in os.walk(inputDir)]   
    processDir     = []
    select_folders = ["AnalysisOutput"]
    temp_listdir1= [ item for item in os.listdir(inputDir) if os.path.isdir(os.path.join(inputDir,item))]
#   print temp_listdir1

    processList = []
    for i in temp_listdir1:
        inputdir = os.path.join(inputDir,i)
        for x in os.listdir(inputdir):
            processList.append(x)

#    print "All processes are :"
#    print processList


    ########################################################################################################
    ################################## Looping over PROCESS FOLDERS ########################################
    ########################################################################################################

    for i in range(len(processDirList)):
        if any(j in processDirList[i] for j in select_folders):
            processDir.append(processDirList[i])
            processDir = [x for x in processDir if "Event-lists" not in x]  # processDir returns all AnalysisOutput grid subfolders 
        else:
            continue
    
#    print('')
#    print('ROOT files are collected from the subdirectories ')
#    print('')
#    print(processDir)     

    N_MC_dic = {}    # Dictionary of Process names and the corresponding N_MC denominators to be used in Eq. (2) 

    ########################################################################################################
    ################################ Looping over grid-i/ANALYSIS OUTPUT FOLDERS ###########################
    ########################################################################################################
    
    for i in range(len(processDir)):                 
        
        subdir = processDir[i]                         # define the subdirectories to get ROOT files from

#        print('')
#        print('Entering the subdirectory: '+subdir)
#        print('')

        for j in range(len(processList)):
            if processList[j] in subdir:
                processname = processList[j]
#        print 'Processname is ' + processname         # ! GETTING PROCESSNAME FROM THE SUBDIR 
        
        #for h in range(len(temp_listdir1)):
         #   if temp_listdir1[h] in subdir:
          #      aggregated_process = temp_listdir1[h]
        #print 'This process belongs to the Aggregated group : ' + aggregated_process         # ! GETTING AGGREGATED PROCESS GROUP FROM THE SUBDIR

        
        if N_MC_dic.has_key(processname)==False:
            N_MC_dic[processname]=[]

        # Checking if is a MCbkg (background) samples, or data samples
        label = 0
        if any(i in subdir for i in data_labels):
            label = 1
        else:
            label = 0
        if len(glob.glob(subdir+"/ECP*")) == 0:
            continue

                    
        #####################################################################################################
        ################# Looping over ROOT FILES to calculate sum(tEvUnweighted) ###########################
        #####################################################################################################
        
        print ''
        print (' Looping over all ROOT file in ' + processname + ' to calcualte sum(tEvUnweighted) ')
        print ''
        
        for fileROOT in glob.glob('%s/ECP*'%(subdir)):   # open the ROOT file 

            inFile            = ROOT.TFile.Open(fileROOT,"READ")
            totalEvUnweighted = inFile.Get("TotalEventsUnweighted")   
            inFile.Close()
            tEvUnweighted = totalEvUnweighted[0]
            N_MC_dic[processname].append(tEvUnweighted)
    
#        print ('The final values of tEvUnweighted for are :')
#        print(N_MC_dic[processname])
#        print ''
        tot_processname = sum(N_MC_dic[processname])                        
        print ( '  ' processname + '            | N_MC = sum(tEvUnweighted) : ' + str(tot_processname))
        print ''
        
        
        #####################################################################################################
        ####################### Looping over ROOT FILES to create h5files ###################################
        #####################################################################################################

        #        print '  -------------------------- Writing into the h5 files -------------------------------------------------'

        
        for fileROOT in glob.glob('%s/ECP*'%(subdir)):   # open the ROOT file 
            
        #    print('')    
        #    print('  ------------>   Reading ROOT file: '+ fileROOT)
        #    print('')

            inFile            = ROOT.TFile.Open(fileROOT,"READ")
            processName       = inFile.Get("ProcessName")
            evCount           = inFile.Get("EvCounts")               # number of accepted and unaccepted events             
            totalEv           = inFile.Get("TotalEvents")            # sum of total event weight (no use here)
            totalEvUnweighted = inFile.Get("TotalEventsUnweighted")  # N_MC : denominator factor for Eq. (2) 
            inFile.Close()

            pName         = str(processName[0])
            evCounts      = evCount[0]
            tEv           = totalEv[0]
            tEvUnweighted = totalEvUnweighted[0]
            
            with uproot.open(fileROOT) as fileup:
            
                # Read the Classes from each ROOT file
                ListTree_classes  = []
                ListTree_classes  = Read_ListTree_from_file(fileup)   # ! The function returns classtree 
                                             
                ############################################################################################
                ############################## Looping over CLASSES ########################################
                ############################################################################################

                ML_Classes = ['_2Ele_1bJet','_1Ele_1Muon_1MET', '_1Ele_1Muon_1Jet','_1Ele_1Muon_1Jet_1MET'] 

                for i in range(len(ListTree_classes)):
                    
                    classname = ListTree_classes[i]                              # ! Define a specific class
                    
                    if classname not in ML_Classes:
                        continue
                    
                    branches = []                              
                    branches = Read_Branches_from_classname(fileup,classname)  # ! Read the branches from this class
                    
                    if branches is not None:
                        entries_SumPt = len(branches['SumPt'])    # length on dataset SumPt
                    else:
                        print('! This file is empty. No entries appended to hdf5 file !')
                        print('')
                    
                        #print(branches)                                      # ! Prints the branches for each class 
                    
                    ### Defining the H5 file output name and directory 
                    fileH5_Dir = outputDir+'H5'+classname+'.h5'
                    #print('')
                    #print("The directory of the H5 file is :"+ fileH5_Dir) 
                    #print('')
                    
                    ### Initializing the arrays for the new h5 file
                    SumPt      = []
                    InvMass    = []
                    MET        = []
                    weights    = []
                    PName      = []
                    NewWeights = []

                    ### Reading variables from branches to fill arrays
                    for i in range(entries_SumPt):
                        if branches is not None:
                            SumPt.append(branches['SumPt'][i])
                            MET.append(branches['MET'][i])
                            InvMass.append(branches['InvMass'][i])
                            weights.append(branches['Weight'][i])
                            PName.append(pName)                    
                            if label==1:
                                NewWeights = weights
                            else:
                                NewWeights = np.array(weights) * Lumi / tot_processname
                            
                    #print('')
                    #print(' ***** %s loaded. Length: %i ***** '%(classname.split('/')[-1], entries_SumPt)) # ! Prints class name and number of events 
                    #print('')                       


                    #########################################################################################################
                    ################ Creating h5 files (or appending new data if the file already exists)####################
                    #########################################################################################################

                    # ! We want 1 single h5 file per classes (even if the data is coming from different processes and root files ! 

                    if os.path.exists(fileH5_Dir)==False:
                        with h5py.File(fileH5_Dir, 'w') as f:
                            Create_dataset('sumpt','SumPt',SumPt)
                            Create_dataset('invmass','InvMass',InvMass)
                            Create_dataset('met','MET',MET)
                            Create_dataset('Weights','weights',weights)
                            Create_dataset('processname','ProcessName', PName)
                            Create_dataset('newweights','NewWeights',NewWeights)
                            f.close()
                            #print('')
                            #print('! Sucessfully created '+fileH5_Dir)
                            #print ('')
                        
                            fileH5_Dir   = ''
                            classname    = ''
                
                    else:
                        with h5py.File(fileH5_Dir, 'a') as f:
                            Append_to_dataset('sumpt','SumPt',SumPt)
                            Append_to_dataset('invmass', 'InvMass',InvMass)
                            Append_to_dataset('met','MET',MET)
                            Append_to_dataset('Weights','weights',weights)
                            Append_to_dataset('processname','ProcessName',PName)
                            Append_to_dataset('newweights','NewWeights',NewWeights)
                            f.close()
                            
                        #print('')
                        #print('! Sucessfully appended new data to '+fileH5_Dir)
                        #print ('')

                        fileH5_Dir   = ''
                        classname    = ''

    print ''
    print 'The dictionary for N_MC = sum(tEvUnweighted) for each process is :'
    print N_MC_dic
