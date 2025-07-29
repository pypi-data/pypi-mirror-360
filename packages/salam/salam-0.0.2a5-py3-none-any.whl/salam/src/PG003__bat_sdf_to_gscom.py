#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 09:20:07 2021

@author: tucy
"""


from rdkit import Chem
#from rdkit.Chem import AllChem
import subprocess
#import shutil
import os

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--gs_opt_method', type=str, default="b3lyp")
parser.add_argument('--num_serviers', type=int, default=2)
parser.add_argument('--remote_wkdir', type=str, default="project")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")

args = parser.parse_args()

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX


print(args.gs_opt_method, type(args.gs_opt_method))
gs_opt_method = args.gs_opt_method

print("num_serviers: ", args.num_serviers, type(args.num_serviers))
NUM_SERVIERS = args.num_serviers

print(args.remote_wkdir, type(args.remote_wkdir))
remote_wkdir = args.remote_wkdir


#-------- remote servier working dir ------------------------------------------
remote_base_wkdir = 'tucy@node130:/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/%s/'%remote_wkdir
remote_GXXXX_opt_jobs_dir = remote_base_wkdir  + GXXXX +  "/opt_jobs/" 

print("The remote_GXXXX_opt_jobs_dir:")
print(remote_GXXXX_opt_jobs_dir)


base_wkdir = './project/'  + GXXXX  + '/'
picmols_sdffile_path = base_wkdir +  PXXXX  + '.sdf'

ms = [x for x in Chem.SDMolSupplier(picmols_sdffile_path)]

print("1st len(ms) = ", len(ms))

while ms.count(None): 
    ms.remove(None)

print("2nd len(ms) = ", len(ms))

call_cp_pg003_sh_modelcom_to_pick_mols_dir = 'cp   ./inputScripts/PG003__bat_sdf_to_gscom.sh   ./inputScripts/bat*.sh    ./inputScripts/g16*.sh    ./inputScripts/*-com  '  +  '   ./project/'  +  GXXXX  + '/pick_mols/  '
status, output = subprocess.getstatusoutput( call_cp_pg003_sh_modelcom_to_pick_mols_dir )
print("Copy inputScripts files. status, output = ", status, output)

# res = subprocess.check_output(["echo", "Hello World!"])
# print(res)


#------------------------------------------------------------------------------
base_wkdir = os.getcwd()
print("base_wkdir: \n", base_wkdir)

GXXXX_pick_mols_dir = './project/'  +  GXXXX +  '/pick_mols/'
os.chdir( GXXXX_pick_mols_dir )
CWD = os.getcwd()
print("CWD: \n", CWD)


status, output = subprocess.getstatusoutput(' cp   ./sdf-files/cpd-*.sdf   ./ ')
print("Copy sdf files. status, output = ", status, output)


print("Run ./PG003__bat_sdf_to_gscom.sh   gs-opt-model-com \n")

bat_sdf_to_gscom_script = "./PG003__bat_sdf_to_gscom.sh    "
b3lyp_gs_opt_model_com = "./b3lyp-gs-opt-model-com"
pm6d3_gs_opt_model_com = "./pm6d3-gs-opt-model-com"
pm7_gs_opt_model_com = "./pm7-gs-opt-model-com"


call_bat_sdf_to_gscom_script_b3lyp = bat_sdf_to_gscom_script + b3lyp_gs_opt_model_com
call_bat_sdf_to_gscom_script_pm6d3 = bat_sdf_to_gscom_script + pm6d3_gs_opt_model_com
call_bat_sdf_to_gscom_script_pm7 = bat_sdf_to_gscom_script + pm7_gs_opt_model_com

if gs_opt_method == "b3lyp":
    retcode = subprocess.call(call_bat_sdf_to_gscom_script_b3lyp, shell=True)
    print(retcode)
elif gs_opt_method == "pm6d3":
    retcode = subprocess.call(call_bat_sdf_to_gscom_script_pm6d3, shell=True)
    print(retcode)
elif gs_opt_method == "pm7":
    retcode = subprocess.call(call_bat_sdf_to_gscom_script_pm7, shell=True)
    print(retcode)
else:
    print("parameter: gs_opt_method, must be either b3lyp, pm6d3 or pm7")
    exit(1)

status, output = subprocess.getstatusoutput(' cp   ./bat*.sh   ./g16*.sh   ./*-com    ./com-files ')
print("Copy PBS Scripts files. status, output = ", status, output)


os.chdir('./com-files/')
print("Enter ./com-files/")

#-------- copy opt coms to  opt_jobs dir --------------------------------------
status, output = subprocess.getstatusoutput(' mkdir   ./opt_jobs   2>/dev/null ')
print("mkdir opt_jobs. status, output = ", status, output)

status, output = subprocess.getstatusoutput(' cp    ./bat*.sh    ./g16*.sh   ./cpd*.com    ./*-com   ./opt_jobs/   2>/dev/null')
print("Copy PBS Scripts files and cpd*.com to  opt_jobs.  status, output = ", status, output)


if (NUM_SERVIERS == 2):
    print("NUM_SERVIERS = ", NUM_SERVIERS)
    os.chdir('./opt_jobs/')
    print("Enter ./opt_jobs/")
    
    status, output = subprocess.getstatusoutput(' scp  cpd*.com  ' + remote_GXXXX_opt_jobs_dir )
    print("scp cpd*.com to remote_GXXXX_opt_jobs_dir. status, output = ", status, output)
else:
    print("NUM_SERVIERS = ", NUM_SERVIERS)

os.chdir(base_wkdir)
#os.chdir(script_call_path)
CWD = os.getcwd()
print("CWD: \n", CWD)
#------------------------------------------------------------------------------


print("\n### End of program: PG003!\n")

