#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 10:15:03 2021

@author: tucy
"""

import re
import glob
#import numpy as np
import pandas as pd

#from rdkit import Chem
#from rdkit.Chem import AllChem
#import subprocess
#import shutil
import os
import argparse
#import time
import subprocess

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--analyzed_property', type=str, default="tadf")
parser.add_argument('--pbs_job_incompleteness_tolerance', type=float, default=0.01)
parser.add_argument('--sleep_seconds', type=int, default=300)
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")

args = parser.parse_args()

print("analyzed_property: ", args.analyzed_property, type(args.analyzed_property) )
print("pbs_job_incompleteness_tolerance: ", args.pbs_job_incompleteness_tolerance, type(args.pbs_job_incompleteness_tolerance) )

analyzed_property = args.analyzed_property
pbs_job_incompleteness_tolerance = args.pbs_job_incompleteness_tolerance

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.sleep_seconds, type(args.sleep_seconds))
SLEEP_SECONDS = args.sleep_seconds


 
    
#--------------------------------------------------------------------------------------------------
def get_normal_lognames(pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                        project_dir='../../../../../../'):
    
    os.chdir( pbs_jobs_wkdir ) 
    
    filenames = glob.glob(r'./cpd*.log')
    
    if (len(filenames) == 0):
        print("No cpd*.log file exit! The ruturn is set to 0.")
        exit(1)
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
        
        os.chdir( project_dir ) 
        
        #normal_logfile_names = [x.replace(r'./', '').replace(r'.log', '')   for  x in filenames]
        normal_logfile_names = [x  for x in filenames if not None]
        
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
            return normal_logfile_names
        else:
            print("len(normal_logfile_names) = ", len(normal_logfile_names))
            return normal_logfile_names



def analysis_property_tadf(normal_logfile_names, 
                           pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                           project_dir='../../../../../../'):
    
    print("Hello in func: analysis_property_tadf")
    
    os.chdir( pbs_jobs_wkdir ) 
    
    filenames = normal_logfile_names

    tadf_results = []
    
    for filename  in  filenames:
        tadf_pattern = re.compile(r'Excitation(\s*)energies(\s*)and(\s*)oscillator(\s*)strengths(.*?)Population(\s*)analysis(\s*)using', re.MULTILINE|re.DOTALL)
        with open(filename) as fp:
            fc=fp.read()
            tadf_result = tadf_pattern.findall(fc)
            print("# ", filename, "", len(tadf_result))
            tadf_results.append(tadf_result)           
      
    #------------------- extract data from strings, and store data in pd.DataFrame 
    
    all_T1_energies = []
    all_S1_energies = []
    all_S1_frequencies = []
    
    all_TEn_SEn_SFrs = []
    
    for tadf_result  in  tadf_results:
        tadf_result = str(tadf_result)
        
        # print('-'*60)
        # print("The original string is: \n",  tadf_result )
        
        tadf_result = tadf_result.split(r'\n')
        # print('-'*60)
        # print("The splitted string is: \n",  tadf_result )
        
        excited_state_pattern = re.compile(r'^(\s*)Excited(\s*)State(.*?)<S\*\*2>=(\S*?)', re.DOTALL) 
        tadf_result_new = []
        for ele in tadf_result:
            ele_new = excited_state_pattern.findall(ele)
            if len(ele_new) > 0:
                tadf_result_new.append(ele_new[0])
        
        # print('-'*60)
        # print("The transformed tadf_result_new string is: \n", tadf_result_new)
        
        
        # if (len(tadf_result_new) > 0):
        #     print('-'*60)
        #     for  i  in range(len(tadf_result_new)):
        #         print(i, "   ",  tadf_result_new[i])
        
        
        tadf_result_new1 = [ele[2].strip() for ele in   tadf_result_new]
        # print('-'*60)
        # print("The transformed tadf_result_new1 is:")
        # for ele in tadf_result_new1:
        #     print(ele)
        
        # print("len is : ", len(tadf_result_new1) )
        
        triplet_state_pattern = re.compile(r'(\s*)Triplet-\w(.*?)$', re.DOTALL) 
        singlet_state_pattern = re.compile(r'(\s*)Singlet-\w(.*?)$', re.DOTALL) 
        
        triplet_states = []
        for ele in tadf_result_new1:
            ele_new = triplet_state_pattern.findall(ele)
            if len(ele_new) > 0:
                triplet_states.append(ele_new[0])
        
        singlet_states = []
        for ele in tadf_result_new1:
            ele_new = singlet_state_pattern.findall(ele)
            if len(ele_new) > 0:
                singlet_states.append(ele_new[0])
          
        
        # print('-'*60)
        # print("The transformed triplet_states is:")
        # for ele in triplet_states:
        #     print(ele)
            
        # print('-'*60)
        # print("The transformed singlet_states is:")
        # for ele in singlet_states:
        #     print(ele)
        
        T1_energies = [ele[-1].strip().split()[0] for ele in triplet_states]
        S1_energies = [ele[-1].strip().split()[0] for ele in singlet_states]
        S1_frequencies = [ele[-1].strip().split()[4].split("=")[1] for ele in singlet_states]
        
        TEn_SEn_SFrs = []
        for ele1, ele2, ele3 in zip(T1_energies, S1_energies, S1_frequencies):
            #print(ele1, ele2, ele3)
            TEn_SEn_SFrs.append(ele1)
            TEn_SEn_SFrs.append(ele2)
            TEn_SEn_SFrs.append(ele3)
        
           
        print('-'*60)
        print(len(T1_energies), len(S1_energies), len(S1_frequencies))
    
        
        #print('-'*60)
        print("len(TEn_SEn_SFrs) is ", len(TEn_SEn_SFrs))
        
        
        all_TEn_SEn_SFrs.append(TEn_SEn_SFrs)
        all_T1_energies.append(T1_energies)
        all_S1_energies.append(S1_energies)
        all_S1_frequencies.append(S1_frequencies)
        
    
    
    compoundnames = [x.replace(r'./', '').replace(r'.log', '')   for  x in filenames]
    
    # for name in compoundnames:
    #     print(name)
    
    datanames = []
    for i in range(len(all_TEn_SEn_SFrs[0][:])//3) :
        datanames.append('T%d_en'%(i+1) )
        datanames.append('S%d_en'%(i+1)  )
        datanames.append('S%d_freq'%(i+1) )
           
       
    df = pd.DataFrame(data=all_TEn_SEn_SFrs, columns=datanames)
    df["compound"] = compoundnames
    df.set_index("compound", inplace=True)
    
    print(df.shape)
    print(df)

    os.chdir( project_dir ) 
    
    return df


def analysis_property_nlo(normal_logfile_names, 
                          pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                          project_dir='../../../../../../'):
    
    print("Hello in func: analysis_property_nlo")
    
    os.chdir( pbs_jobs_wkdir ) 
    
    filenames = normal_logfile_names

    nlo_results = []
    
    for filename  in  filenames:
        nlo_pattern = re.compile(r'\\V(.*?)\\@$', re.MULTILINE|re.DOTALL)
        with open(filename) as fp:
            fc=fp.read()
            nlo_result = nlo_pattern.findall(fc)
            print("# ", filename, "", len(nlo_result))
            nlo_results.append(nlo_result)

            
    #------------------- extract data from strings, and store data in pd.DataFrame 
    HFs = []
    polars = []
    hyperpolars = []
    HF_polar_hyperpolars = []
    
    for nlo_result  in  nlo_results:
        nlo_result = str(nlo_result)
        
        #print("The original sting is: \n",  nlo_result )
        
        nlo_result = nlo_result.replace('\n', '').replace('\r', '').replace(' ', '').split('=')    
        #print('-'*60)
        #print("The transformed sting is: \n", nlo_result)
        
        print("len is : ", len( nlo_result ))
        
        HF = nlo_result[3].strip().replace(r'\n', '').replace('\r', '').replace(' ', '').split(r'\\')[0].replace(' ', '')
        polar = nlo_result[6].strip().replace(r'\n', '').replace('\r', '').replace(' ', '').split(r'\\')[0].replace(' ', '')
        hyperpolar = nlo_result[7].strip().replace(r'\n', '').replace('\r', '').replace(' ', '').split(r'\\')[0].replace(' ', '')
            
        
        HF = HF.split(',')
        polar = polar.split(',')
        hyperpolar = hyperpolar.split(',')
        
        print('-'*60)
        print(len(HF), len(polar), len(hyperpolar))
    
        HFs.append(HF)
        polars.append(polar)
        hyperpolars.append(hyperpolar)
        
        HF_polar_hyperpolar = HF + polar + hyperpolar
        HF_polar_hyperpolars.append(HF_polar_hyperpolar)
    
    
    compoundnames = [x.replace(r'./', '').replace(r'.log', '')   for  x in filenames]
    
    # for name in compoundnames:
    #     print(name)
    
    datanames = ["hf", "axx", "axy", "ayy", "axz", "ayz", "azz", \
        "bxxx", "bxxy", "bxyy", "byyy", "bxxz", "bxyz", "byyz", "bxzz", "byzz", "bzzz"]
        
        
    df = pd.DataFrame(data=HF_polar_hyperpolars, columns=datanames)
    df["compound"] = compoundnames
    df.set_index("compound", inplace=True)
    
    print(df.shape)
    print(df)
    
    os.chdir( project_dir ) 

    return df
#----------------------------------------------------------------------------------------




#--main func -----------------------------------------------------------------------------

base_wkdir = os.getcwd()
print("base_wkdir: \n", base_wkdir)


#-------main loop ------------------------------------------------------------
print('*'*60)
print("# Begin PG009__property_analysis_summary.")

GXXXX_pick_mols_com_files_finished_com_files_dir =  './project/'  +   GXXXX  +  '/pick_mols/com-files/finished/com-files/'


normal_logfile_names = get_normal_lognames(pbs_jobs_wkdir=GXXXX_pick_mols_com_files_finished_com_files_dir, 
                                           project_dir=base_wkdir,)


print("\nNormal_logfile_names: ")
for inf in normal_logfile_names:
    print(inf)


#-----------------------------------------------------------------------------

os.chdir(base_wkdir)
CWD = os.getcwd()
print("\nCWD: \n", CWD)
#------------------------------------------------------------------------------


print("# Begin analyzing property.\n")

if (analyzed_property == "tadf") or (analyzed_property == "TADF"):
    
    df_tadf = analysis_property_tadf(normal_logfile_names, 
                                     pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                                     project_dir=base_wkdir
                                     )
    
    print('-'*60)
    tadf_summary_file_path = './project/' + GXXXX +  '/tadf_summary_'   +   PXXXX  +  '.csv'
    print("The summary of property analysis TADF is stored at: ")
    print(tadf_summary_file_path)
    
    with open(tadf_summary_file_path, 'w') as tmp:
        df_tadf.to_csv(tmp)

elif (analyzed_property == "nlo") or (analyzed_property == "NLO"):
    
    df_nlo = analysis_property_nlo(normal_logfile_names, 
                                    pbs_jobs_wkdir='./project/%s/pick_mols/com-files/finished/com-files/'%GXXXX, 
                                    project_dir=base_wkdir
                                    )
    
    print('-'*60)
    nlo_summary_file_path = './project/' + GXXXX +  '/nlo_summary_'   +   PXXXX  +  '.csv'
    print("The summary of property analysis NLO is stored at: ")
    print(nlo_summary_file_path)
    
    with open(nlo_summary_file_path, 'w') as tmp:
        df_nlo.to_csv(tmp)

else:
    print("No defined parameter.")    
    print("analyzed_property: tadf or nlo.")
    exit(1)
    

print('-'*60)
src_file_path = './project/'    +   GXXXX  +  '/pick_mols/sdf-files/'
GXXXX_PXXXXrev_sdf_path =  './project/'   +  GXXXX  +  '/'  +  PXXXX  + 'rev.sdf'

print("\nThe revised pick_mols is stored at %s"%GXXXX_PXXXXrev_sdf_path)

call_rm_GXXXX_PXXXXrev_sdf_path  =  'rm  -f  '  +  GXXXX_PXXXXrev_sdf_path  + '   2>/dev/null  '
status, output = subprocess.getstatusoutput( call_rm_GXXXX_PXXXXrev_sdf_path )
print("rm -f   %s.    status, output = "%GXXXX_PXXXXrev_sdf_path, status, output)


normal_compoundnames = [x.replace(r'./', '').replace(r'.log', '')   for  x in  normal_logfile_names]

for normal_name in normal_compoundnames:
    #print(normal_name)
    normal_sdf_file_name = src_file_path + normal_name + ".sdf"
    cat_file_to_Pickmols = 'cat  '   +  normal_sdf_file_name   +   '   >>  ./project/'  +  GXXXX  + '/'   +  PXXXX   +  'rev.sdf   '
    status, output = subprocess.getstatusoutput( cat_file_to_Pickmols )
    #print("status, output = ", status, output)
    

print("\n### End of program:  PG009!\n")

