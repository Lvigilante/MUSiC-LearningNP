if __name__ == '__main__':
    # import required libraries
    import h5py as h5
    import numpy as np
    import matplotlib.pyplot as plt
    import argparse
    import sys

    np.set_printoptions(edgeitems=100)

    # Read H5 file
    parser = argparse.ArgumentParser()
    parser.add_argument('-in','--inputDir', type=str, help="Directory of the h5 file to be opened.", required=True)
    parser.add_argument('-dsetName','--dsetName',type=str, help="Dataset to be printed", required=True)
    args = parser.parse_args()

    inputDir  = args.inputDir
    dataset   = args.dsetName
    
    with h5.File(inputDir, 'r') as f:
       
        datasetNames = [n for n in f.keys()]
        print('')
        print('----------------------------------------')
        print('')
        print('This h5 file has '+str(len(datasetNames))+' datasets:')
        print('')
      
        for n in datasetNames:
            print(f[str(n)])
        
        dset    = f.get(dataset)
        array   = np.array(dset)
        process = f.get('ProcessName')        
        pName   = np.array(process)
        

        if dataset == 'NewWeights':
            mc_counts = sum(array)
            print('')
            print('Entries of NewWeights are : ')
            print('')
            print(array)
            print('')
            print('Total MC events are : '+ str(mc_counts))
            print('')

           # for i in range(len(array)):
             #   if array[i]<0.0 or array[i]>50.0:
                    #print('Process name : ' + str(pName[i]) + '   | NewWeights : ' + str(array[i]))                
        else:
            print('')
            print('Entries of '+ dataset +' are :')
            print('')
            print(array)
            print('')
            print('----------------------------------------')
     

