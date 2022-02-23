import os,sys,commands,re,math
import shutil
import fileinput

import optparse
import logging
from termcolor import colored

log = logging.getLogger(__name__)

usage = 'usage: %prog -C cat'
parser = optparse.OptionParser(usage)
parser.add_option('-m', '--mode', dest='mode', action="store_true", default = False, help='Choose your mode:')
parser.add_option('-n', '--dryrun',dest='dryrun', default=False , help='If True, run in dryrun mode')
parser.add_option('-d', '--indirectory', dest='indir', type='string', default = '.', help="The Scan or Classification directory you want to check")


(opt, args) = parser.parse_args()

m1 =opt.mode
dryrun=opt.dryrun
InDir= opt.indir
TmpDir=''
ScDir = ''
ListDir=os.listdir(InDir)

GridDir=[]
BgDir=[]
SamDir=[]


n1=0
n2=0
n3=0
n4 = 0

Scan=False
for f in ListDir:
    #print f
    if not os.path.isdir(InDir + "/" + f):
        continue
    BgDir=os.listdir(InDir + "/" + f)
    for m in BgDir:
        if not os.path.isdir(InDir + "/" + f + "/" + m):
            continue
        SamDir=os.listdir(InDir + "/" + f + "/" + m)
        if(Scan==False):
            for g in SamDir:
                if "grid" in g:
                    GridDir=os.listdir(InDir + "/" + f + "/" + m + "/" + g)
                    #print(f + "/" + g)
                    #for l in GridDir:
                    if "AnalysisOutput" in GridDir:
                        #print(colored(" Both OutDir and AnalysisOutput in grid Folder: ", "yellow"))
                        #print(InDir + "/" + f + "/" + m + "/" + g)
                        n1= n1 +1
                        AnaDir=os.listdir(InDir + "/" + f + "/" + m + "/" + g + "/" + "AnalysisOutput")
                        for fname in AnaDir:
                            if "ECP" in fname:
                                print(fname, "has the keyword")
                                
                    else:
                        print(colored(" No AnalysisOutput in grid Folder:", "red")) 
                        print(InDir + "/" + f + "/" + m + "/" + g)
                        n3= n3 +1
        else:
            if "grid" in m:
                #print(f + "/" + g)
                bit=False
                for l in SamDir:
                    if "Output" in l:
                        n1= n1 +1
                        bit=True
                        break
                if (bit==False):
                    print(colored("No Output  in grid Folder:", "green")) 
                    print(InDir + "/" + f + "/" + m )
                    n2= n2 +1
                else:
                    print(colored(" Both OutDir and AnalysisOutput in grid Folder: ", "yellow"))
                    print(InDir + "/" + f + "/" + m )
                     
            
if(Scan==False):
    n4 = n1 +n2 +n3 +n4
    print("\n  ********  Summary of the Classification Grid Job at this moment  ************  \n ")
    print("  I've found: \n   "      )
    print("  TOTAL JOB SUBMITTED: " ,n4)
    print("  JOB SUCCESFULL (AnalysisOutput IS in the grid folder):   ", n1)
    print("  JOB PARTIAL SUCCESSFULL (Only MusicOutDir IS in the grid folder):    " , n2)
    print("  JOBS FAILED ( NO AnalysisOutput and NO MusicoOutDir are in the grid folder):   " ,n3)
    print("\n  ********  END of the Summary  ************  \n ")
else:
    n4 = n1+ n2+ n4
    print("  I've found: \n   "      )
    print("  TOTAL JOB SUBMITTED: " , n4)
    print("  JOB SUCCESFULL (Output IS in the grid folder):   ", n1)
    print("  JOBS FAILED ( NO Output and in the grid folder):   " ,n2)
    print("\n  ********  END of the Summary  ************  \n ")
