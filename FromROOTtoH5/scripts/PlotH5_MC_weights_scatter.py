import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT
import argparse
import matplotlib as mpl
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

data_labels=['SingleMuon','SingleElectron','SinglePhoton','DoubleMuon','DoubleEG']

if __name__ == '__main__':

    parser    = argparse.ArgumentParser()

    parser.add_argument('-in','--inputDir', type=str, help='Directory of MC H5 file to be plotted.', required=True)
    parser.add_argument('-inData','--inputDirData', type=str, help='Directory of Data H5 file to be plotted.', required=False)
    parser.add_argument('-dsetName','--dsetName', type=str, help='Data set to be plotted. Choose SumPt, InvMass, MET, weights, or NewWeights.', required=True)
    args       = parser.parse_args()    
    
    fileH5     = args.inputDir 
    fileH5Data = args.inputDirData
    
    dset       = args.dsetName
    eventClass = fileH5.replace('ML_Classes_SumPt_cutted_doubleweighted/','')
    evClass    = eventClass.replace('.h5','')

    x_MC       = []
    freq       = []
    pName_MC   = []
    
    with h5py.File(fileH5, 'r') as f:
        freq          = list(f['NewWeights'])
        x_MC          = list(f[dset])
        sumPt         = list(f['SumPt'])
        pNameList_MC  = list(f['ProcessName'])
        f.close()

    print('Shape of freq is ' + str(len(freq)))
    print('Shape of x_MC is ' + str(len(x_MC)))

    freq1 = np.array(freq)
    fulldataset_MC = list(zip(x_MC,pNameList_MC))
    processes_MC   = list(set(pNameList_MC))
    

#    with h5py.File(fileH5Data, 'r') as f:
 #       x_Data     = list(f[dset])
  #      f.close()
    
#    print ''
#    print ('Unique processes in this file are : ' )
#   print processes
#   print ''

    dic_MC = {}
    dic_weights = {}

    for i in range(len(processes_MC)):
        dic_MC[processes_MC[i]]=[]
        dic_weights[processes_MC[i]]=[]
    
        for j in range(len(fulldataset_MC)):
            if processes_MC[i] in fulldataset_MC[j][1]:
                dic_MC[processes_MC[i]].append(fulldataset_MC[j][0])
                dic_weights[processes_MC[i]].append(freq1[j])
    
                

    #print 'The dictionary with process names and dset values has been created succesfully ! '
    #print dic
    
    n_bins = 100
    data   = []
    freq2  = []
    labels = []

    for i in range(len(processes_MC)):
        x = dic_MC[processes_MC[i]]
        w = dic_weights[processes_MC[i]]
        freq2.append(w)
        data.append(x)
        labels.append(processes_MC[i])
    
  #  flat_data    = [val for sublist in data for val in sublist]

    print('Shape of weights is '+ str(len(freq)))
    print('Shape of sumPt is '+ str(len(sumPt)))
    #print data

    #n, bins, patches = plt.hist(data, n_bins, density = False, histtype = 'bar', stacked = True, label = labels)
    plt.scatter(freq,sumPt)
    
  #  bin_counts, bin_edges, patches = plt.hist(data, bins=n_bins, log = True, marker = 'o', fc = 'None', density = False)
#    bin_centres = (bin_edges[:-1] + bin_edges[1:]) / 2
    #plt.xlim()
    plt.xlabel(' New_weights')
    plt.ylabel('SumPt')
    plt.title(evClass)
    plt.legend()

    plt.show('plot_'+evClass+'_'+dset+'.png')

    
    
