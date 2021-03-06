import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT

#directory = './Output_hzz4l' # specify your directory path
directory = './DirROOTFiles' # specify your directory path
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

def Read_ListTree_from_file(fileROOT):
    #print("****** Entro in Read_ListTree_from_file   ********")
    fileup   = uproot.open(fileROOT)
    #tree     = fileup['_1Ele']
    listoftree=fileup.keys()
    listoftree.remove("ProcessName;1")
    listoftree.remove("EvCounts;1")
    listoftree.remove("TotalEvents;1")
    listoftree.remove("TotalEventsUnweighted;1")
    #print listoftree
    for j in listoftree:
        tree   = fileup[j]
        #print j
        branches = tree.arrays(namedecode='utf-8')
        #print branches
        if branches['SumPt'].shape[0]==0:
            # empty file
            print('empty file')
            return
    #print("******     ESCO DA       Read_ListTree_from_file   ********")
    return listoftree

def Prepare_List_Of_File(DirPath):
    for dirpath, dirnames, filenames in os.walk(Dirpath):
        for filename in [f for f in filenames if f.startswith("ECP")]:
            Filespath.append(os.path.join(dirpath, filename))

def Collect_from_file(fileROOT, t, y_label, subdir,
                      SumPt, InvMass, MET, labels, weights, key_process):
    '''
    label: 0 if MC bkg
           1 if data
           2 if MC sig (not needed for searches, maybe used to set limits)
    key_process : string ID for the process (in subdir)

    cosThetaStar, cosTheta1, cosTheta2, PHI, PHI1 : for theta and phi definition see AN
    '''
    print("DEB2.5")
    UnwEv      = []
    ### Opening  the root file 
    fileup   = uproot.open(fileROOT)
    #tree     = fileup['_1Ele']
    tree     = fileup[t]
    branches = tree.arrays(namedecode='utf-8')
    print("DEB3")
    ### Check if the file is empty 
    if branches['SumPt'].shape[0]==0:
        # empty file
        print('empty file')
        return
        
    #SumPt.append(branches['SumPt'])
    #InvMass.append(branches['InvMass'])
    #MET.append(branches['MET'])
    #weights.append(branches['Weight'])
    
    ### Appending the branches
    for i in range(len(branches['SumPt'])):
        print("DEB4")
        key_process.append(subdir.split('/')[-1])
        labels.append(label)
        weights.append(branches['Weight'][i])
        SumPt.append(branches['SumPt'][i])
        InvMass.append(branches['InvMass'][i])
        MET.append(branches['MET'][i])
        print("Entry, SumPt values: %i , %f , %f , %f , %f"%(i,SumPt[i], InvMass[i], MET[i], weights[i]) )

        '''    
        # ZZ -> 4mu
        if branches['is4m'][i]:
            pt1.append(branches['Muon_pt'][i][branches['iLepton1'][i]])
            pt2.append(branches['Muon_pt'][i][branches['iLepton2'][i]])
            pt3.append(branches['Muon_pt'][i][branches['iLepton3'][i]])
            pt4.append(branches['Muon_pt'][i][branches['iLepton4'][i]])
            eta1.append(branches['Muon_eta'][i][branches['iLepton1'][i]])
            eta2.append(branches['Muon_eta'][i][branches['iLepton2'][i]])
            eta3.append(branches['Muon_eta'][i][branches['iLepton3'][i]])
            eta4.append(branches['Muon_eta'][i][branches['iLepton4'][i]])
            phi1.append(branches['Muon_phi'][i][branches['iLepton1'][i]])
            phi2.append(branches['Muon_phi'][i][branches['iLepton2'][i]])
            phi3.append(branches['Muon_phi'][i][branches['iLepton3'][i]])
            phi4.append(branches['Muon_phi'][i][branches['iLepton4'][i]])
        
        # ZZ -> 4e
        elif branches['is4e'][i]:
            continue
        '''
        '''
            pt1.append(branches['Electron_pt'][i][branches['iLepton1'][i]])
            pt2.append(branches['Electron_pt'][i][branches['iLepton2'][i]])
            pt3.append(branches['Electron_pt'][i][branches['iLepton3'][i]])
            pt4.append(branches['Electron_pt'][i][branches['iLepton4'][i]])
            eta1.append(branches['Electron_eta'][i][branches['iLepton1'][i]])
            eta2.append(branches['Electron_eta'][i][branches['iLepton2'][i]])
            eta3.append(branches['Electron_eta'][i][branches['iLepton3'][i]])
            eta4.append(branches['Electron_eta'][i][branches['iLepton4'][i]])
            phi1.append(branches['Electron_phi'][i][branches['iLepton1'][i]])
            phi2.append(branches['Electron_phi'][i][branches['iLepton2'][i]])
            phi3.append(branches['Electron_phi'][i][branches['iLepton3'][i]])
            phi4.append(branches['Electron_phi'][i][branches['iLepton4'][i]])
        '''
        '''
        # ZZ -> 2e2m
        elif branches['is2e2m'][i]:
            continue
        '''
        '''
            if branches['Muon_eta'][i][branches['iLepton1'][i]]-branches['Muon_eta'][i][branches['iLepton2'][i]] == branches['Z1_dEta'][i]:
                # Z1 from muons
                pt1.append(branches['Muon_pt'][i][branches['iLepton1'][i]])
                pt2.append(branches['Muon_pt'][i][branches['iLepton2'][i]])
                pt3.append(branches['Electron_pt'][i][branches['iLepton3'][i]])
                pt4.append(branches['Electron_pt'][i][branches['iLepton4'][i]])
                eta1.append(branches['Muon_eta'][i][branches['iLepton1'][i]])
                eta2.append(branches['Muon_eta'][i][branches['iLepton2'][i]])
                eta3.append(branches['Electron_eta'][i][branches['iLepton3'][i]])
                eta4.append(branches['Electron_eta'][i][branches['iLepton4'][i]])
                phi1.append(branches['Muon_phi'][i][branches['iLepton1'][i]])
                phi2.append(branches['Muon_phi'][i][branches['iLepton2'][i]])
                phi3.append(branches['Electron_phi'][i][branches['iLepton3'][i]])
                phi4.append(branches['Electron_phi'][i][branches['iLepton4'][i]])
            else:
                # Z1 from electrons
                pt1.append(branches['Electron_pt'][i][branches['iLepton1'][i]])
                pt2.append(branches['Electron_pt'][i][branches['iLepton2'][i]])
                pt3.append(branches['Muon_pt'][i][branches['iLepton3'][i]])
                pt4.append(branches['Muon_pt'][i][branches['iLepton4'][i]])
                eta1.append(branches['Electron_eta'][i][branches['iLepton1'][i]])
                eta2.append(branches['Electron_eta'][i][branches['iLepton2'][i]])
                eta3.append(branches['Muon_eta'][i][branches['iLepton3'][i]])
                eta4.append(branches['Muon_eta'][i][branches['iLepton4'][i]])
                phi1.append(branches['Electron_phi'][i][branches['iLepton1'][i]])
                phi2.append(branches['Electron_phi'][i][branches['iLepton2'][i]])
                phi3.append(branches['Muon_phi'][i][branches['iLepton3'][i]])
                phi4.append(branches['Muon_phi'][i][branches['iLepton4'][i]])
        '''
        
    print('%s loaded. Length: %i'%(fileROOT.split('/')[-1], len(SumPt)))
    return

if __name__ == '__main__':

    ###Creating lists to store in the h5 file
    SumPt      = []
    InvMass    = []
    MET        = []
    
    labels       = []
    weights      = []
    keys         = []

    ###Initialize some variables:
    Lumi= 41480.
    ListTree     = []

    ###Loop over folders to find MC/data samples
    #print('DEB1 ')
    for subdir in subdirs:
        print('DEB1.1 printing    subdir: ')
        print(subdir)
        label = 0
        ###Check if is a MCbkg samples, a MC signal or a data samples
        for ext in mcbkg_labels:
            print('mcbkg_label is: ')
            print ext
        if any(ext in subdir for ext in mcbkg_labels):
            label = 0
        elif any(ext in subdir for ext in data_labels):
            label = 1    
        elif any(ext in subdir for ext in mcsig_labels):
            label = 2
        else: continue

        ###Looping over the root files that are inside the subdir
        for fileROOT in glob.glob('%s/*.root'%(subdir)):
            ListTree=[]
            #del ListTree[:]
            ListTree=Read_ListTree_from_file(fileROOT)
            ### Open File just to take nEventsUnweighted
            inFile = ROOT.TFile.Open(fileROOT,"READ")
            evUnWeights =  inFile.Get("TotalEventsUnweighted")
            inFile.Close()
            print "evUnweights"
            print evUnWeights
            nEvUnv = evUnWeights[0]
                
            for t in ListTree:
                #print t
                ###Cleaning list variables
                SumPt      = []
                InvMass    = []
                MET        = []
                
                labels       = []
                weights      = []
                keys         = []

                #del SumPt[:]
                #del InvMass[:]
                #del MET[:]
                
                #del labels[:]
                #del weights[:]
                #del keys[:]

                # skip bad files
                if 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17/5C8B9676-1B82-E911-9C8A-1418774121A1_Skim.root' in fileROOT: continue
                ### Run the function to get variables from the root file. Defined above. 
                Collect_from_file(fileROOT,t, label, subdir,
                                  SumPt, InvMass, MET, labels, weights, keys)
                keys_int = []
                #print('DEB2')
                for k in keys:
                    for c in list(code_keys.keys()):
                        if c in k: 
                            keys_int.append(code_keys[c])
                            continue
                ###Evaluating the weight
                for j in weights:
                    new_weight = j * Lumi / nEvUnv
                    print new_weight

                ### Creating numpy array from the variables. 
                SumPt      = np.array(SumPt)
                InvMass    = np.array(InvMass)
                MET        = np.array(MET)
    
                labels   = np.array(labels)
                weights  = np.array(weights)
                keys     = np.array(keys)
                keys_int = np.array(keys_int) 
    
                ### Save array  on h5 files
                t1=t
                t2=t1.replace(";1","")
                fileH5_name= './Dir_OUTH5_Files/H5'+t2+'.h5'
                print fileH5_name
                #if not fileH5_name.exists():
                f  = h5py.File(fileH5_name, 'a')
                f.create_dataset('SumPt', data=SumPt, compression='gzip')
                f.create_dataset('InvMass', data=InvMass, compression='gzip')
                f.create_dataset('MET', data=MET, compression='gzip')
                
                f.create_dataset('labels', data=labels, compression='gzip')
                f.create_dataset('weights', data=weights, compression='gzip')
                f.create_dataset('process', data=keys_int, compression='gzip')
                
                f.close()
                fileH5_name= '' 
                t1 =""
                t2=""
                #else: 
