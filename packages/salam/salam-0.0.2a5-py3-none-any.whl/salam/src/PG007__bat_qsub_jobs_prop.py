#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 16:05:54 2021

@author: tucy
"""

import subprocess
import os

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--num_serviers', type=int, default=2)
parser.add_argument('--remote_wkdir', type=str, default="project")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")

parser.add_argument('--COMPUTE_RATIO_SERVIER1', type=float, default=0.56)
parser.add_argument('--COMPUTE_RATIO_SERVIER2', type=float, default=0.46)

args = parser.parse_args()


print("num_serviers: ", args.num_serviers, type(args.num_serviers))
NUM_SERVIERS = args.num_serviers

print(args.remote_wkdir, type(args.remote_wkdir))
remote_wkdir = args.remote_wkdir

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

G_num = int( GXXXX[1:] )  
print("G_num = ", G_num)

print(args.COMPUTE_RATIO_SERVIER1, type(args.COMPUTE_RATIO_SERVIER1))
print(args.COMPUTE_RATIO_SERVIER2, type(args.COMPUTE_RATIO_SERVIER2))
COMPUTE_RATIO_SERVIER1 = args.COMPUTE_RATIO_SERVIER1
COMPUTE_RATIO_SERVIER2 = args.COMPUTE_RATIO_SERVIER2



#-------- remote servier working dir ------------------------------------------
remote_base_wkdir = '/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/%s/'%remote_wkdir
remote_GXXXX_prop_jobs_dir = remote_base_wkdir  + GXXXX +  "/prop_jobs/" 

print("The remote_GXXXX_prop_jobs_dir:")
print(remote_GXXXX_prop_jobs_dir)


#------------------------------------------------------------------------------
base_wkdir = os.getcwd()
print("base_wkdir: \n", base_wkdir)

GXXXX_pick_mols_com_files_finished_com_files_dir = './project/' +  GXXXX  + '/pick_mols/com-files/finished/com-files/prop_jobs/'
os.chdir( GXXXX_pick_mols_com_files_finished_com_files_dir )
CWD = os.getcwd()
print("CWD: \n", CWD)


if (NUM_SERVIERS == 2):
    print("NUM_SERVIERS = ", NUM_SERVIERS)
    retcode = subprocess.call('./bat-g16-prop.sh  '  +  str(COMPUTE_RATIO_SERVIER1)    +  '   %d  '%G_num , shell=True)
    #retcode = subprocess.call('./bat-g16-prop.sh ', shell=True)
    print(retcode)
    
    #------ run remote pbs jobs ---------------------------------------------------
    status, output = subprocess.getstatusoutput('ssh    tucy@node130    "cd   '   +   remote_GXXXX_prop_jobs_dir   +  ' ;    ./bat-g16-prop_node130_133.sh     '  +  str(COMPUTE_RATIO_SERVIER2)    +  '   %d  '%G_num   +  '     > /dev/null   2>&1   &  "  ')  
    print("run remote pbs_jobs status. status, output = ", status, output)

else:
    print("NUM_SERVIERS = ", NUM_SERVIERS)
    retcode = subprocess.call('./bat-g16-prop.sh   1 '   +  '   %d  '%G_num  , shell=True)


#status, output = subprocess.getstatusoutput('qstat -u tucy ')
status, output = subprocess.getstatusoutput('  qstat -u tucy  | grep "\<0 R\>"  -C1   ;   echo   "" ;    qstat -u tucy | grep -i "tucy"  -c ;    ')
print("pbs_jobs status. status, output = ", status, output)


os.chdir(base_wkdir)
CWD = os.getcwd()
print("CWD: \n", CWD)
#------------------------------------------------------------------------------


print("\n### End of program: PG007!\n")
