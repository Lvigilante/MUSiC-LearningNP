#!/bin/env python

from __future__ import print_function

# Built-In libraries.                                                                                                                       

import io 
import os
import sys
import time
import shutil
import math
import configargparser
import ConfigParser
import multiprocessing
import subprocess
import collections
import tarfile
import json
import copy
import logging
import traceback
import uuid
from contextlib import contextmanager
from pprint import pprint


import pickle

# 3rd-party libraries.                                                                                                                     
import numpy as np
import ROOT
from ROOT import *

from ectools.register import ecroot

# MUSiC-Utils   
import roothelpers

#THIS SCRIPT IS INTENTED TO EXTRACT HISTO FROM TO TEVENTCLASS AND SAVE THEM AGAIN AS ROOT FILES
#A BIG PART OF THE CODE COMES FROM MUSiC-RoIScanner/python/scanSubmitter.py. OF COURSE ADJUSTMENTS HAVE BEEN DONE.
def main():

    logger = logging.getLogger("main")
    options = commandline_and_config_parsing()
    roothelpers.root_setup()
    print("Start the main of EClass To ROOT files")

    #if options.data and not os.path.isfile( options.data ):
    #    logger.error( "Data file %s does not exist.", options.data )
    #    return

    #if not os.path.isfile( options.mc ):
    #    logger.error( "Input MC file %s does not exist.", options.mc )
    #    return

    # Open the ROOT file and loop over all objects
    # Use --mc option in the command line to set mc_file and mc_file 
    mc_file = ROOT.TFile.Open( options.mc )

    if options.data:
        data_file = ROOT.TFile.Open( options.data )
        options.Nrounds = 1
    else:
        data_file = None


    # Get a list of all class names.                                                                  
    options.veto.append( "Rec_Empty*" )
    ec_names = ecroot.prepare_class_names( options, mc_file=mc_file )[ 0 ]

    # convert to list and sort class names                                                                           
    ec_names = list(ec_names)
    ec_names.sort(key = lambda s: len(s))

    #Create a dict of a dict
    dict_class_proc={}
    #Start to loop over classes. iclass is the number of the class. name is it's name
    for iclass, name in enumerate( ec_names ) :

        if name.find("X")>0 or name.find("NJ")>0:
            continue

        print("iclass: ", iclass, "name: ", name )
        key = mc_file.GetKey( name )
        logger.info( "Working event class '%s.", name )

        event_class = key.ReadObj()

        if options.distribution not in event_class.getDistTypes():
            logger.debug( "Distribution %s not valid for EC %s, skipping...", options.distribution, name )
            event_class.Delete()
            continue

        if event_class.getTotalEvents() <= 0:
            logger.warning( "Negative integral (<= 0) in event class '%s', skipping..." % name )
            event_class.Delete()
            continue
        #LOR trying to get integrals from distributions
        dicto=calc_integrals(event_class, options.distribution)
        dict_class_proc[ name ] = {
            "dict_int" : dicto
        }

        #Lor trying to get event_info from EventClass
        vec_ev_info= event_class.GetListedEvents(name)

    #Check if there is a data file
    if data_file:
        logger.debug( "Matching data event class..." )
        data_key = data_file.GetKey( name )

        if data_key:
            data_event_class = data_key.ReadObj()
        else:
            logger.debug( "Event class '%s' not found in data.", name )
            data_event_class = None

    # cross-check: find classes that are present only in data (not MC)                                            
    data_ec_names = []
    if data_file:
        data_ec_names = ecroot.prepare_class_names( options, data_file=data_file )[ 0 ]

    for ec_name in data_ec_names:
        if not ec_name in ec_names:
            logger.warning( "Event class with data and without mc: %s" % ec_name )

    #Get the Integral of hist
    #integral = h1_InvMass.Integral()
    
    #for i in h1_InvMass->GetNbinsX():
    #    bin_content = h1_InvMass->GetBinContent(i)
    print("DEBUG")
    #print("Integral %s",integral)

    # Close file now, no references exist anymore.                                                                   
    mc_file.Close()
    if data_file:
        data_file.Close()

    #Check a ROOT file to store the Integrals
    file_exists = os.path.isfile("./output.root")
    if file_exists:
        print("File exits... RECREATE IT ")
        return

    #Open a ROOT file to store the Integrals
    #g= ROOT.Double(4.567)

    b = ROOT.TH1F( "all_signal", "all_signal", 100, 100, 100 )

    a=ROOT.TVectorD()
    a[0]=3.12
    b.Fill(a[0])
    a.SetDirectory(0)
    b.SetDirectory(0)
    outFileName="output.root"
    out_file=ROOT.TFile(outFileName," RECREATE ")
    #integral.Write("mc_integral")
    #out_file.Cd()
    #out_file.WriteObject(dict_class_proc, "dict_class_proc")
    #a.Write("a")
    out_file.cd() 
    b.Write()
    #out_file.WriteTObject(a)
    out_file.Close()
    
    return

def calc_integrals(event_class, distribution):
        
    unweighted_hists = {}
    dict_integral={}
    # Add up MC  hists and errors for all processes
    #getHistoPointer is defined in MUSiC-Utils/include/TEventClass.hh in LINES 172-173,627-628
    for process_name in list( event_class.getProcessList() ):
        unweighted_hists[ process_name ] = {
            "hist_unweight" : event_class.getHistoPointerUnweighted( process_name, distribution ).Clone(),
            "hist_weight" : event_class.getHistoPointer( process_name, distribution ).Clone(),
            "xs"   : event_class.getCrossSection( process_name )
        }

    #LOR START TO WRITE
    #a = list( event_class.getProcessList())
    #proc_name= "Rec_1Ele"
    #integral= unweighted_hists[ a[2] ]["hist"].Integral()
    for process_name in list( event_class.getProcessList() ):
        integral= unweighted_hists[ process_name ]["hist_unweight"].Integral()
        integral_weight=unweighted_hists[ process_name ]["hist_weight"].Integral()
        cross_x=unweighted_hists[ process_name ]["xs"]
        print("Process: ", process_name)
        print("Integral unweighted: %s",integral)
        print("Integral weighted: %s",integral_weight)
        print("**************")
        dict_integral[ process_name ] = {
            "integral_unweight" : event_class.getHistoPointerUnweighted( process_name, distribution ).Clone(),
            "integral_weight" : event_class.getHistoPointer( process_name, distribution ).Clone(),
            "xs"   : event_class.getCrossSection( process_name )
        }

    #h1_InvMass = ROOT.TH1F()
    #h1_InvMass ==  unweighted_hists[ a[2] ]["hist"].Clone()
    #TH1F* h1_InvMass =  unweighted_hists[ proc_name ].get("hist").Clone()
    #TH1F* h1_InvMass =  unweighted_hists[ proc_name ]["hist"].Clone()

    return dict_integral


def commandline_and_config_parsing():
    # Desired resolution order:                                           
    # 1. if provided as command line argument, USE IT                                                                                      
    # 2. elif provided in config file, USE IT                                                                                              
    # 3. else: use default                                                                                                                 
    logger = logging.getLogger()

    parser = configargparser.ArgumentParser(description='Script to extract distribution histo from MUSiC classifications (TEventClass file) ')
    extract_group = parser.add_argument_group(title="Extract Options")
    ecroot.add_ec_standard_options( extract_group )

    #extract_group.add_argument( '--signal', type=str, default="",
    #    help="Signal ROOT file to study (must contain complete signal: BG + BSM model)." )
    extract_group.add_argument( '-v', '--verbose', action="count", dest='verbosity', default=0,
        help="Output verbosity (repeat -v for more verbosity)." )
    # TODO replace "jsontemp" in code with this option (-j used for number of jobs)                                                         
    #parser.add_argument( '--json-out', dest="jsondir", type=str, default='json', help="Directory for JSON files (relative to the main direc\tory)" )                                                                                                                                  
    #extract_group.add_argument( '--scanner-base', default= os.path.expandvars("$SCAN_BASE"), type=str,
    #    help="Base path for the scanner" )
    extract_group.add_argument('--distribution', choices=("SumPt", "InvMass", "MET"), default="SumPt",
        help="Name of the distribution to scan.")
    

    # Parse again. This time for real.                                                                                                
    args = parser.parse_args()

    # Done.               
    logging.debug( "Command line and config file parsing done: %s.", args )
    return args


if __name__=="__main__":
    main()
