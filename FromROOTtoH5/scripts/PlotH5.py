import numpy as np
import h5py, glob
import math
import uproot
import os
import ROOT
import argparse
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt



if __name__ == '__main__':

    parser    = argparse.ArgumentParser()

    parser.add_argument('-in','--inputDir', type=str, help='Directory with h5 files to be plotted.', required=True)
    parser.add_argument('-dsetName','--dsetName', type=str, help='Data set to be plotted.', required=True)

    args       = parser.parse_args()
    
    inputDir   = args.inputDir 
    dset       = args.dsetName

    Files      = os.listdir(inputDir)

    FileList   = []   
    y          = []
    y_values   = []
    x          = []
    classnames = []

    for i in range(len(Files)):
        
        fileH5 = inputDir+Files[i]                    #h5file where data will be extracted
        name=Files[i].strip('.h5')

        FileList.append(Files[i])                     #list with all h5 files names
        classnames.append(name)                       #list with all class names
        x.append(i)                                   #array with the class indice [0,1,...,i] 0 = 1st file name, 1 = second file name, etc.

        print('')
        print('Opening the file : ' + fileH5)
        print('')

        with h5py.File(fileH5, 'r') as f:
            data=list(f[dset])
            y.append(data)                            #array with the data, e.g. 'SumPt' array
            #y_values.append(y[i])
            f.close()
            fileH5 = ''                               #clean the directory name

    print('')
    print('Plotted classes are : ')
    print(classnames)
    print('')
    print('Class indices are : ')
    print(x)
    print('')
    print(dset + ' y data is ')
    print('')
    print(y)

    for xe, ye in zip(x, y):
        plt.scatter([xe]*len(ye), ye)
 
    plt.xticks(x)
    plt.axes().set_xticklabels(classnames)
    plt.savefig('H5_test_plot.png')
    
    

