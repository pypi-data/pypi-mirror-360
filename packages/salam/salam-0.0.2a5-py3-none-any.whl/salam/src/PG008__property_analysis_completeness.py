#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 10:15:03 2021

@author: tucy
"""

import re
import glob
#import numpy as np
#import pandas as pd

#from rdkit import Chem
#from rdkit.Chem import AllChem
import subprocess
#import shutil
import os
import argparse
import time
#import subprocess
#from sys import exit as sys_exit

parser = argparse.ArgumentParser(description="manual to this script:")
#parser.add_argument('--analyzed_property', type=str, default="tadf")
parser.add_argument('--num_serviers', type=int, default=2)
parser.add_argument('--remote_wkdir', type=str, default="project")
parser.add_argument('--pbs_job_incompleteness_tolerance', type=float, default=0.01)
parser.add_argument('--sleep_seconds', type=int, default=300)
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")

args = parser.parse_args()

#print("opt_property: ", args.analyzed_property, type(args.analyzed_property) )

print("pbs_job_incompleteness_tolerance: ", args.pbs_job_incompleteness_tolerance, type(args.pbs_job_incompleteness_tolerance) )

#analyzed_property = args.analyzed_property
pbs_job_incompleteness_tolerance = args.pbs_job_incompleteness_tolerance

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.sleep_seconds, type(args.sleep_seconds))
SLEEP_SECONDS = args.sleep_seconds

print("num_serviers: ", args.num_serviers, type(args.num_serviers))
NUM_SERVIERS = args.num_serviers

print(args.remote_wkdir, type(args.remote_wkdir))
remote_wkdir = args.remote_wkdir


#-----------------------------------------------------------------------------
def compute_num_total_finished_jobs():
    
    com_filenames = glob.glob(r'./cpd*.com')
    filenames = glob.glob(r'./cpd*.log')
    
    if (len(com_filenames) == 0):
        print("No cpd*.com file exit! SYSTEM EXIT(101) in compute_num_total_finished_jobs() of PG005.")
        exit(101)
    else:
        if (len(filenames) == 0):
            print("No cpd*.log file exit! The ruturn is set to 0.")
            return len(com_filenames), 0
        else:
            failed_compound_idxs = []
            
            idx = 0
            for filename  in  filenames:
                termination_pattern = re.compile(r'Normal(\s*)termination(.*?)', re.MULTILINE|re.DOTALL)
                with open(filename) as fp:
                    fc=fp.read()
                    termination_result = termination_pattern.findall(fc)
                    #print("# ", filename, "", len(termination_result))
                    if len(termination_result) != 1:
                        failed_compound_idxs.append(idx)
                    
                    idx += 1


            com_compoundnames = [x.replace(r'./cpd-', '').replace(r'.com', '')   for  x in com_filenames]
            compoundnames = [x.replace(r'./cpd-', '').replace(r'.log', '')   for  x in filenames]            
            
            if len(failed_compound_idxs) > 0:
                print('-'*60)
                print("failed_compound_names: ")
                for failed_compound_idx in failed_compound_idxs:            
                    print(filenames[failed_compound_idx])
                
                failed_compound_idxs.sort(reverse=True)
                for i  in failed_compound_idxs:
                    compoundnames.pop(i)
            
            # print('-'*60)
            # for name in compoundnames:
            #     print(name)
            
                print("len(com_compoundnames), len(compoundnames) = ", len(com_compoundnames), len(compoundnames) )
                return len(com_compoundnames), len(compoundnames)
            else:
                print("len(com_compoundnames), len(compoundnames) = ", len(com_compoundnames), len(compoundnames) )
                return len(com_compoundnames), len(compoundnames)
                


def compute_pbs_job_completeness(pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                                 project_dir='../../../../../../'):
    os.chdir( pbs_jobs_wkdir ) 
    #CWD = os.getcwd()
    #print("CWD: \n", CWD)
    
    num_total_jobs, num_finished_jobs = compute_num_total_finished_jobs()
    
    job_completeness = 0.
    
    if (num_total_jobs != 0):
        job_completeness = num_finished_jobs / float( num_total_jobs )
    else:
        print("No cpd-*.com files exist!!!")
        exit(100)
    
    os.chdir( project_dir ) 
    #CWD = os.getcwd()
    #print("CWD: \n", CWD)
    
    return job_completeness   
    


def get_normal_lognames(pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                        project_dir='../../../../../../'):
    
    os.chdir( pbs_jobs_wkdir ) 
    
    filenames = glob.glob(r'./cpd*.log')
    
    if (len(filenames) == 0):
        print("No cpd*.log file exit! The ruturn is set to 0.")
        exit(1)
        return 
    else:
        failed_log_idxs = []
        
        idx = 0
        for filename  in  filenames:
            termination_pattern = re.compile(r'Normal(\s*)termination(.*?)', re.MULTILINE|re.DOTALL)
            with open(filename) as fp:
                fc=fp.read()
                termination_result = termination_pattern.findall(fc)
                #print("# ", filename, "", len(termination_result))
                if len(termination_result) != 1:
                    failed_log_idxs.append(idx)
                
                idx += 1
        
        normal_logfile_names = [x.replace(r'./', '').replace(r'.log', '')   for  x in filenames]
        
        if len(failed_log_idxs) > 0:
            print('-'*60)
            print("# failed_compound_names: ")
            for failed_log_idx in failed_log_idxs:            
                print(filenames[failed_log_idx])
        
            
            failed_log_idxs.sort(reverse=True)
            print("# pop failed log names:")
            for i  in failed_log_idxs:
                normal_logfile_names.pop(i)
                print("idx = ", i)
        
        
        print("len(normal_logfile_names) = ", len(normal_logfile_names))
        
        os.chdir( project_dir ) 
    
        return normal_logfile_names



def synchronize_job_dir(GXXXX, 
                        analysis_dir = './project/'  +  GXXXX  +  '/pick_mols/com-files/',
                        GXXXX_opt_jobs_dir =  './project/'  +  GXXXX  +  '/pick_mols/com-files/' + 'opt_jobs/', 
                        remote_GXXXX_opt_jobs_dir = '/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/project/'  + GXXXX +  "/opt_jobs/", 
                        base_wkdir = '../../../../',
                        NUM_SERVIERS = NUM_SERVIERS
                        ):

    print("Begin synchronize_job_dir")
    os.chdir(analysis_dir)
    
    if (NUM_SERVIERS == 2):
        print("NUM_SERVIERS = ", NUM_SERVIERS)
        status, output = subprocess.getstatusoutput(' mkdir   ./remote_prop_jobs/   2>/dev/null  ' )
        status, output = subprocess.getstatusoutput(' scp  -r  tucy@node130:' + remote_GXXXX_opt_jobs_dir  + 'cpd*.log '  +  '    ./remote_prop_jobs/ ' )
        print("scp -r remote_GXXXX_opt_jobs_dir to  ./remote_prop_jobs/. status, output = ", status, output)
    else:
        print("NUM_SERVIERS = ", NUM_SERVIERS)
        
    
    logfilenames = glob.glob(r'./*prop_jobs/cpd*.log')
    
    if (len(logfilenames) == 0):
        print("No cpd*.log file exit!")
    else:
        for logfilename  in  logfilenames:
            termination_pattern = re.compile(r'Normal(\s*)termination(.*?)', re.MULTILINE|re.DOTALL)
            with open(logfilename) as fp:
                fc=fp.read()
                termination_result = termination_pattern.findall(fc)
                #print("# ", filename, "", len(termination_result))
                if len(termination_result) == 1:
                    status, output = subprocess.getstatusoutput(' cp   ' + logfilename +   '  ./    2>/dev/null  ' )
                    print("cp logfile. status, output = ", status, output)

    
    os.chdir( base_wkdir )
    time.sleep(120)
    
    print("End synchronize_job_dir")
    
    return 0 




#-----------------------------------------------------------------------------

#--------main func -----------------------------------------------------------
#-----------------------------------------------------------------------------

base_wkdir = os.getcwd()
print("base_wkdir: \n", base_wkdir)


#-------main loop ------------------------------------------------------------
print('*'*60)
print("# PG008: Begin compute pbs_job_completeness, only when attaining the desired job_completeness, the loop could be stopped and turnned to next step.")


synchronize_job_dir(GXXXX, 
                    analysis_dir = './project/'  +  GXXXX  +  '/pick_mols/com-files/finished/com-files/',
                    GXXXX_opt_jobs_dir =  './project/'  +  GXXXX  +  '/pick_mols/com-files/finished/com-files/' + 'prop_jobs/', 
                    remote_GXXXX_opt_jobs_dir = '/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/%s/'%remote_wkdir  + GXXXX +  "/prop_jobs/", 
                    base_wkdir = base_wkdir,
                    NUM_SERVIERS = NUM_SERVIERS
                    )


GXXXX_pick_mols_com_files_finished_com_files_dir =  './project/'  +   GXXXX  +  '/pick_mols/com-files/finished/com-files/'
job_completeness = compute_pbs_job_completeness(pbs_jobs_wkdir=GXXXX_pick_mols_com_files_finished_com_files_dir,  
                                                project_dir=base_wkdir)

print("The initial job_completeness = ", job_completeness)

job_completeness_summary_file_path = './project/'   +   GXXXX   +   '/pick_mols/com-files/finished/com-files/job_completeness_summary.data'

loop_times = 1
with open(job_completeness_summary_file_path, 'w') as tmp:
    while ( abs( 1. - job_completeness ) >  pbs_job_incompleteness_tolerance ):
        print("The job_completeness is %8.4f." % job_completeness)
        print("loop_times = %d. "%(loop_times) )
        #print("Sleep 1 hour.")
        #time.sleep(3600)
        
        synchronize_job_dir(GXXXX, 
                            analysis_dir = './project/'  +  GXXXX  +  '/pick_mols/com-files/finished/com-files/',
                            GXXXX_opt_jobs_dir =  './project/'  +  GXXXX  +  '/pick_mols/com-files/finished/com-files/' + 'prop_jobs/', 
                            remote_GXXXX_opt_jobs_dir = '/home/tucy/Computation-node131/Gaussian16-jobs/SALAM/%s/'%remote_wkdir  + GXXXX +  "/prop_jobs/", 
                            base_wkdir = base_wkdir,
                            NUM_SERVIERS = NUM_SERVIERS
                            )
        
        print("Sleep %d sec."%SLEEP_SECONDS )
        time.sleep(SLEEP_SECONDS)
        job_completeness = compute_pbs_job_completeness(pbs_jobs_wkdir=GXXXX_pick_mols_com_files_finished_com_files_dir, 
                                                        project_dir=base_wkdir)
        
        tmp.write( "%10d, "%(loop_times) )
        tmp.write( "%15.6f\n"%(job_completeness) )
        loop_times += 1

with open(job_completeness_summary_file_path, 'a+') as tmp:
    tmp.write( "%15.6f\n"%(job_completeness) )
    
    
job_completeness  = compute_pbs_job_completeness(pbs_jobs_wkdir=GXXXX_pick_mols_com_files_finished_com_files_dir, 
                                                 project_dir=base_wkdir
                                                )
    
print("The final job_completeness is %8.4f.\n" % job_completeness)

#-----------------------------------------------------------------------------

os.chdir(base_wkdir)
CWD = os.getcwd()
print("\nCWD: \n", CWD)
#------------------------------------------------------------------------------



print("\n### End of program:  PG008!\n")

