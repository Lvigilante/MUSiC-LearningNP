import numpy as np
import h5py, glob, math, uproot, os, ROOT, argparse

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
 #       print('Shape of '+datasetName+' dataset was '+str(dsetName.shape))
        #old_shape=dsetName.shape[0]                            # ! shape=(,) for previous dataset

  #      print('We want to extend the dataset by '+str(len(dataName)))
        dsetName.resize((dsetName.shape[0]+len(dataName),))     # ! Resizing the dataset. This is okay
        new_shape   = dsetName.shape[0]                         # ! shape=(,) for resized dataset
        entry_point = new_shape-len(dataName)

   #     print('The entry point for new data is at position '+str(entry_point))
        dsetName[-len(dataName):] = dataName                    # ! Appending new data to the dataset.
    #    print('New shape of '+datasetName+' dataset is '+str(dsetName.shape))
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
   
    Lumi = 41480.       # Defining the integrated luminosity

    processDirList = [x[0] for x in os.walk(inputDir)]   
    processDir     = []
    select_folders = ["AnalysisOutput"]
    temp_listdir1  = [ item for item in os.listdir(inputDir) if os.path.isdir(os.path.join(inputDir,item))]
    #print temp_listdir1

    processList = []

    for i in temp_listdir1:
        inputdir = os.path.join(inputDir,i)
        for x in os.listdir(inputdir):
            processList.append(x)
   
    print "All processes are :"
    print processList                # This prints a list of strings of ALL process names, which are read directly from the folders inside the directory  


    ########################################################################################################
    ################################## Creating a list with the grid paths #################################
    ########################################################################################################

    for i in range(len(processDirList)):
        if any(j in processDirList[i] for j in select_folders):
            processDir.append(processDirList[i])
            processDir = [x for x in processDir if "Event-lists" not in x]  
        else:
            continue
    
    print('')
    print('ROOT files are collected from the subdirectories ')
    print('')
    print(processDir)     # This prints a list of the complete path to the folder where each ROOT file is stored, e.g. ['DiPhoton/DiPhoton..../grid-0/Analysis-Output', DiPhoton/DiPhoton..../grid-1/Analysis-Output']

    dic_evCounts = {}              # this will become {'Process name' : [evCounts1, evCounts2, ...]}  
    dic_tEv      = {}              # this will become {'Process name' : [totalEvents1, totalEvents2, ...]}  
    dic_tEvUnweighted  = {}        # this will become {'Process name' : [totalEventsUnweighted1, totalEventsUnweighted2, ...]}

    ########################################################################################################
    ####################################### Looping over grid FOLDERS ######################################
    ########################################################################################################
    
    for i in range(len(processDir)):                 
        
        subdir = processDir[i]                         # subdir is a specific string in the processDir list, i.e. we are choosing one grid path to get the ROOT file from
 
        for j in range(len(processList)):
            if processList[j] in subdir:
                processname = processList[j]           # the subdir string contains the processname substring of the ROOT file that is stored inside. we want to extract this substring

        # Checking if is a MC or data sample
        label = 0
        if any(i in subdir for i in data_labels):
            label = 1
        else:
            label = 0
        if len(glob.glob(subdir+"/ECP*")) == 0:
            continue

        print('')
        print('Entering the subdirectory: '+subdir) 
        print('')
        print 'Processname is ' + processname         # this prints the corresponding processname substring to the subdir string

        #####################################################################################################
        ####################### Looping over ROOT FILES to create h5files ###################################
        #####################################################################################################

        #print '  -------------------------- Opening the ROOT file and creating the h5 files -------------------------------------------------'

        
        for fileROOT in glob.glob('%s/ECP*'%(subdir)):    # we are looping over ROOT files inside the subdir (which is only one ROOT file in our case)  
            
            inFile            = ROOT.TFile.Open(fileROOT,"READ")     # we are reading some stuff from the ROOT file
            processName       = inFile.Get("ProcessName")
            evCount           = inFile.Get("EvCounts")               # number of accepted and unaccepted events             
            totalEv           = inFile.Get("TotalEvents")            # sum of total event weight
            totalEvUnweighted = inFile.Get("TotalEventsUnweighted")
            inFile.Close()                               # we are cloasing the ROOT file

            pName         = str(processName[0])
            evCounts      = evCount[0]
            tEv           = totalEv[0]
            tEvUnweighted = totalEvUnweighted[0]
            
            if dic_evCounts.has_key(pName)==False:     # initially our dictionaries are empty, so we create an empty list for each new pName 
                dic_evCounts[pName]      = []
                dic_tEv[pName]           = []          
                dic_tEvUnweighted[pName] = []          

            dic_evCounts[pName].append(evCounts)      # if the key pName already exists in our dictionaries, then we append the corresponding variable to the list
            dic_tEv[pName].append(tEv)
            dic_tEvUnweighted[pName].append(tEvUnweighted)


            ############################################################################################
            ############################## Looping over CLASSES ########################################
            ############################################################################################

            with uproot.open(fileROOT) as fileup:     # We are opening the ROOT file and pass it to the functions which read the classtree and branches
            
                ListTree_classes  = []
                ListTree_classes  = Read_ListTree_from_file(fileup)   # The function returns classtree 
                                             
                ML_Classes = ['_2Ele_1bJet', '_1Ele_1Muon_1MET', '_1Ele_1Muon_1Jet','_1Ele_1Muon_1Jet_1MET']   # these are the only classes we are interested for now

                for i in range(len(ListTree_classes)):
                    
                    classname = ListTree_classes[i]                              # we are choosing a specific class from the classtree
                    
                    if classname not in ML_Classes:                               # we only want to execute the code for the 4 classes above in ML_Classes
                        continue
                    
                    branches = []                              
                    branches = Read_Branches_from_classname(fileup,classname)  # This returns the branches for the corresponding class
                    
                    if branches is not None:
                        entries_SumPt = len(branches['SumPt'])   # this is the number of events
                    else:
                        print('! This file is empty. No entries appended to hdf5 file !')
                        print('')
                    
                        #print(branches)         
                    
                    fileH5_Dir = outputDir+'H5'+classname+'.h5'     # we are defining the H5 file name and output directory 
                    
                    ### Initializing the arrays for the new h5 file
                    SumPt      = []
                    InvMass    = []
                    MET        = []
                    weights    = []
                    PName      = []

                    ### Reading variables from branches to fill arrays
                    for i in range(entries_SumPt):
                        if branches is not None:
                            SumPt.append(branches['SumPt'][i])
                            MET.append(branches['MET'][i])
                            InvMass.append(branches['InvMass'][i])
                            weights.append(branches['Weight'][i])
                            PName.append(pName)                    
                    
                    #print('')
                    #print(' ***** %s loaded. Length: %i ***** '%(classname.split('/')[-1], entries_SumPt)) # ! Prints class name and number of events 
                    #print('')                       

                    #########################################################################################################
                    ################ Creating h5 files (or appending new data if the file already exists) ###################
                    #########################################################################################################

                    # We only create 1 h5 file per class but the data inside is being appended from different processes and root files, at each loop iterations 

                    if os.path.exists(fileH5_Dir)==False:
                        with h5py.File(fileH5_Dir, 'w') as f:
                            Create_dataset('sumpt','SumPt',SumPt)
                            Create_dataset('invmass','InvMass',InvMass)
                            Create_dataset('met','MET',MET)
                            Create_dataset('Weights','weights',weights)
                            Create_dataset('processname','ProcessName', PName)
                            
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
                            
                            #print('')
                            #print('! Sucessfully appended new data to '+fileH5_Dir)
                            #print ('')

                            fileH5_Dir   = ''
                            classname    = ''
    

    #########################################################################################################
    ######################### Calculating N_MC and NewWeights for EACH PROCESS ##############################
    #########################################################################################################    

    print ''
    print ' ---------------------- Calculating NewWeights dataset and appending to the H5 files ------------------------------'

    ## we are now outside of all loops. All H5 files have been created with 5 datasets each (SumPt, InvMass, MET, weights, ProcessName).  

    if label == 0 :

        for classname in ML_Classes:     # we are only interested in 4 classes, i.e. we only want to open 4 H5 files

            fileH5_Dir = outputDir+'H5'+classname+'.h5'    # we are defining the path to the H5 file we want to open

            with h5py.File(fileH5_Dir, 'r+') as f:   # opening the H5 file

                sumpt      = f['SumPt']              # we read these 3 datasets from the H5 file
                weights1   = f['weights']
                procName   = f['ProcessName']
                
                NewWeights = []                      # we create 2 new empty lists which later on will be added as 2 new datasets in the H5 file
                NewWeights_lastweight = []

                for i in range(len(sumpt)):          # we are looping over the events in the dataset
                 
                    if procName[i] in dic_evCounts.keys() : #and sumpt[i]>125. and sumpt[i]<1100. :             # check if the processname for this event is a key in the dictionary

                        N_MC = sum(dic_tEvUnweighted[procName[i]])    # we are accesing the list of tEvUnweighted corresponding to this processname and we are summing it 
                        NewWeights.append(weights1[i] * Lumi / N_MC)  # we are defining the new weight and appending it to our empty list created above

                        N_MC_lastweight = N_MC + dic_tEvUnweighted[procName[i]][-1]                 # this is the same as before, but we are adding the last entry of the list twice
                        NewWeights_lastweight.append(weights1[i] * Lumi / N_MC_lastweight)

                    else:
                        continue
                      #  NewWeights.append(0.)                     # if we want to apply the sumpt cuts above, we should append a value of 0 for the values that fall outside the sumpt range
                      #  NewWeights_lastweight.append(0.)


                Create_dataset('newweights','NewWeights',NewWeights)  # we are storing the NewWeights list as a dataset in the H5 file


        print ' ---------> sum(NewWeights) is :' + str(sum(NewWeights))   # we are printing the sum of all values inside the NewWeights list. This should be the number of MC events 
        print ' ---------> sum(NewWeights_lastweight) is :' + str(sum(NewWeights_lastweight))  

        else : 
            continue  # if label = 1 (i.e. the H5 file corresponds to Data) we do not create the NewWeights list or dataset)
                    


