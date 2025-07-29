#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 09:20:07 2021

@author: tucy
"""

import subprocess
#import shutil
import os
import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--calc_prop', type=str, default="tadf")
parser.add_argument('--prop_calc_method', type=str, default="wb97xd")
parser.add_argument('--num_serviers', type=int, default=2)
parser.add_argument('--remote_wkdir', type=str, default="project")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")


args = parser.parse_args()

print("num_serviers: ", args.num_serviers, type(args.num_serviers))
NUM_SERVIERS = args.num_serviers

print(args.remote_wkdir, type(args.remote_wkdir))
remote_wkdir = args.remote_wkdir

print(args.calc_prop, type(args.calc_prop))
calc_prop = args.calc_prop

print(args.prop_calc_method, type(args.prop_calc_method))
prop_calc_method = args.prop_calc_method


print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX



#-----------main func --------------------------------------------------------
#-----------------------------------------------------------------------------

#-------- remote servier working dir ------------------------------------------
remote_base_wkdir = 'tucy@node130:/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/%s/'%remote_wkdir
remote_GXXXX_prop_jobs_dir = remote_base_wkdir  + GXXXX +  "/prop_jobs/" 

print("The remote_GXXXX_prop_jobs_dir:")
print(remote_GXXXX_prop_jobs_dir)


call_cp_pg006sh_modelcom_to_GXXXX_pick_mols_com_files_dir =  'cp   ./inputScripts/PG006__bat_g09log_to_propcom.sh   ./inputScripts/copy_com_chk_logs_to_modification_finished.sh   ./inputScripts/bat*.sh   ./inputScripts/g16*.sh  ./inputScripts/*-tadf-model-com    ./inputScripts/*-nlo-model-com   '  +  '  ./project/'  +  GXXXX   +  '/pick_mols/com-files/ '
status, output = subprocess.getstatusoutput( call_cp_pg006sh_modelcom_to_GXXXX_pick_mols_com_files_dir )
print("Copy inputScripts files. status, output = ", status, output)


#------------------------------------------------------------------------------
base_wkdir = os.getcwd()
print("base_wkdir: \n", base_wkdir)


GXXXX_pick_mols_com_files_dir = './project/'   +  GXXXX  + '/pick_mols/com-files/'
os.chdir( GXXXX_pick_mols_com_files_dir )
CWD = os.getcwd()
print("#CWD: \n", CWD)


print("Call ./copy_com_chk_logs_to_modification_finished.sh ")
copy_com_chk_logs_to_modification_finished_script = "./copy_com_chk_logs_to_modification_finished.sh  "
retcode = subprocess.call(copy_com_chk_logs_to_modification_finished_script, shell=True)
print(retcode)


status, output = subprocess.getstatusoutput('cp   ./PG006__bat_g09log_to_propcom.sh   ./*-tadf-model-com  ./*-nlo-model-com   ./bat*.sh   ./g16*.sh    ./finished/  ')
print("Copy pbs script and propcom files. status, output = ", status, output)

os.chdir('./finished/')
CWD = os.getcwd()
print("#CWD: \n", CWD)


print("Run ./PG006__bat_g09log_to_propcom.sh   prop-model-com  \n")

bat_g09log_to_propcom_script = "./PG006__bat_g09log_to_propcom.sh     "

wb97xd_tadf_model_com = "./wb97xd-tadf-model-com"
lcwpbe_tadf_model_com = "./lcwpbe-tadf-model-com"
camb3lyp_tadf_model_com = "./camb3lyp-tadf-model-com"
b3lyp_tadf_model_com = "./b3lyp-tadf-model-com"
cis_tadf_model_com = "./cis-tadf-model-com"

wb97xd_nlo_model_com = "./wb97xd-nlo-model-com"
#lcwpbe_nlo_model_com = "./lcwpbe-nlo-model-com"
camb3lyp_nlo_model_com = "./camb3lyp-nlo-model-com"
b3lyp_nlo_model_com = "./b3lyp-nlo-model-com"


call_bat_g09log_to_propcom_script_cis_tadf = bat_g09log_to_propcom_script + cis_tadf_model_com
call_bat_g09log_to_propcom_script_b3lyp_tadf = bat_g09log_to_propcom_script + b3lyp_tadf_model_com
call_bat_g09log_to_propcom_script_wb97xd_tadf = bat_g09log_to_propcom_script + wb97xd_tadf_model_com
call_bat_g09log_to_propcom_script_lcwpbe_tadf = bat_g09log_to_propcom_script + lcwpbe_tadf_model_com
call_bat_g09log_to_propcom_script_camb3lyp_tadf = bat_g09log_to_propcom_script + camb3lyp_tadf_model_com


call_bat_g09log_to_propcom_script_b3lyp_nlo = bat_g09log_to_propcom_script + b3lyp_nlo_model_com
call_bat_g09log_to_propcom_script_wb97xd_nlo = bat_g09log_to_propcom_script + wb97xd_nlo_model_com
#call_bat_g09log_to_propcom_script_lcwpbe_nlo = bat_g09log_to_propcom_script + lcwpbe_tadf_model_com
call_bat_g09log_to_propcom_script_camb3lyp_nlo = bat_g09log_to_propcom_script + camb3lyp_nlo_model_com


if ( (calc_prop == "tadf") and (prop_calc_method == "wb97xd") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_wb97xd_tadf, shell=True)
    print(retcode)
elif ( (calc_prop == "tadf") and (prop_calc_method == "lcwpbe") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_lcwpbe_tadf, shell=True)
    print(retcode)
elif ( (calc_prop == "tadf") and (prop_calc_method == "camb3lyp") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_camb3lyp_tadf, shell=True)
    print(retcode)
elif ( (calc_prop == "tadf") and (prop_calc_method == "b3lyp") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_b3lyp_tadf, shell=True)
    print(retcode)
elif ( (calc_prop == "tadf") and (prop_calc_method == "cis") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_cis_tadf, shell=True)
    print(retcode)
elif ( (calc_prop == "nlo") and (prop_calc_method == "wb97xd") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_wb97xd_nlo, shell=True)
    print(retcode)
elif ( (calc_prop == "nlo") and (prop_calc_method == "camb3lyp") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_camb3lyp_nlo, shell=True)
    print(retcode)
elif ( (calc_prop == "nlo") and (prop_calc_method == "b3lyp") ):
    retcode = subprocess.call(call_bat_g09log_to_propcom_script_b3lyp_nlo, shell=True)
    print(retcode)
else:
    print("parameter: calc_prop: either tadf or nlo; ") 
    print("           prop_calc_method: either wb97xd, lcwpbe, camb3lyp, b3lyp, or cis.")
    exit(1)

print("calc_prop = ", calc_prop)
print("prop_calc_method = ", prop_calc_method)

status, output = subprocess.getstatusoutput(' cp   ./bat*.sh   ./g16*.sh   ./com-files ')
print("Copy PBS Scripts files. status, output = ", status, output)

os.chdir('./com-files/')
print("Enter ./com-files/")

#-------- copy prop coms to  prop_jobs dir --------------------------------------
status, output = subprocess.getstatusoutput(' mkdir   ./prop_jobs   2>/dev/null ')
print("mkdir prop_jobs. status, output = ", status, output)

status, output = subprocess.getstatusoutput(' cp    ./bat*.sh    ./g16*.sh   ./cpd*.com   ./prop_jobs/   2>/dev/null')
print("Copy PBS Scripts files and cpd*.com to  prop_jobs.  status, output = ", status, output)


if (NUM_SERVIERS == 2):
    print("NUM_SERVIERS = ", NUM_SERVIERS)

    os.chdir('./prop_jobs/')
    print("Enter ./prop_jobs/")
    
    status, output = subprocess.getstatusoutput(' scp  cpd*.com  ' + remote_GXXXX_prop_jobs_dir )
    print("scp cpd*.com to remote_GXXXX_prop_jobs_dir. status, output = ", status, output)

else:
    print("NUM_SERVIERS = ", NUM_SERVIERS)


os.chdir(base_wkdir)
CWD = os.getcwd()
print("#CWD: \n", CWD)
#------------------------------------------------------------------------------


print("\n### End of program: PG006!\n")

