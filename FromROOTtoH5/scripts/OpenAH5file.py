if __name__ == '__main__':
    # import required libraries
    import h5py as h5
    import numpy as np
    import matplotlib.pyplot as plt
    
    # Read H5 file
    #f = h5.File("../../../MUSiC-LearningNP_DATAOUTPUT/Dir_OUT_FILEH5/H5_1Ele_1Muon.h5", "r")
    f = h5.File("../../../MUSiC-LearningNP_DATAOUTPUT/Dir_OUT_FILEH5/H5_1Muon_2Jet.h5", "r")
    #f = h5.File("../../../MUSiC-LearningNP_DATATEST/FromROOTtoH5/data/Dir_OUTH5_Files/H5_2Muon_1MET.h5", "r")
    # Get and print list of datasets within the H5 file
    datasetNames = [n for n in f.keys()]
    for n in datasetNames:
        print(n)
    dSumPt= f["SumPt"]
    weight=f["weights"]
    print dSumPt
    #print dSumPt[1]
    #for x in xrange(dSumPt.shape[0]):
    #    print x
    #for d in dSumPt:
    #    print d
    print "************ SumPt Shape ***********"
    print dSumPt.shape[0]
    print "************ Weight Shape ***********"
    print weight.shape[0]
