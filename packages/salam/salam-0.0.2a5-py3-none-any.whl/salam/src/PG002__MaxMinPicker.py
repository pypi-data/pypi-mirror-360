#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 14:30:21 2021

rdkit.SimDivFilters

@author: tucy
"""

import sys 
import os
#os.chdir('../')
script_wkdir = os.getcwd()
sys.path.append(script_wkdir)


import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")
parser.add_argument('--pickmols_size', type=int, default=100)

args = parser.parse_args()

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print("pickmols_size is ", args.pickmols_size, type(args.pickmols_size))
pickmols_size = args.pickmols_size


from rdkit import Chem
from rdkit.Chem.rdMolDescriptors import GetMorganFingerprint
from rdkit import DataStructs
from rdkit.SimDivFilters.rdSimDivPickers import MaxMinPicker

from salam.module_MD.D_Pi_A_Enumeration import draw_mols

from tqdm import tqdm
import datetime
import multiprocessing as mp

import subprocess
import shutil 
import time
from joblib import Parallel, delayed

from salam.module_MD.D_Pi_A_Enumeration import try_embedmolecule


#-----------------------------------------------------------------------------
def write_mol_to_sdf(mol, cpd_name, outfile_path='./project/G0000/separate_mols/'):
    
    outname=  outfile_path + '%s.sdf'%(cpd_name)
    #print(outname)
    one_w = Chem.SDWriter(outname)
    m_temp = Chem.AddHs(mol)
    m1_temp, nb_try_EmbedMolecule = try_embedmolecule(m_temp)
    m1_temp.SetProp("_Name", cpd_name)
    one_w.write(m1_temp)


def write_mols_paralell(mols, cpd_names, outfile_path='./project/G0000/separate_mols/'):
    #-------  paralell write mols-----------------------------------------------------------
    print("The outfile_path is : %s" % outfile_path )
    
    start = time.time()
    
    rm_GXXXX_separate_mols_sdf = 'rm -f   '  +  outfile_path + 'cpd-*.sdf  '
    (status0, output0) = subprocess.getstatusoutput( rm_GXXXX_separate_mols_sdf )
    
    Parallel(n_jobs=-1)(delayed(write_mol_to_sdf)(mol, cpd_name, outfile_path) \
                        for mol, cpd_name in zip(mols, cpd_names) )
    
    end = time.time()
    
    print('-'*60)
    print("write_mol_to_sdf run in paralell.")
    print('{:.4f} s'.format(end-start))



#-----------------main function -----------------------------------------------


#--- multiprocessing ---------------------------------------------------
num_cores = int(mp.cpu_count())
print("The number of processors of local machine is : " + str(num_cores) + " cores. ")
pool = mp.Pool(num_cores)

start_t0 = datetime.datetime.now()


#-------------------------------------------------------------------------


base_wkdir = './project/'  + GXXXX + "/"
allmols_sdffile_path = base_wkdir + GXXXX + ".sdf"

ms = [x for x in Chem.SDMolSupplier(allmols_sdffile_path)]

print("1st len(ms) = ", len(ms))

while ms.count(None): 
    ms.remove(None)

print("2nd len(ms) = ",len(ms))


#pick_ratio = 0.10
if len(ms) > 0:
    pick_ratio = pickmols_size / float( len(ms) )


#fps = [pool.apply_async(GetMorganFingerprint, args=(mol, 3) ) for mol in ms]
fps = [ GetMorganFingerprint(mol, 3) for mol in tqdm(ms)]
nfps = len(fps)

def distij(i, j, fps=fps):
    return 1-DataStructs.DiceSimilarity(fps[i], fps[j])

picker = MaxMinPicker()
pickIndices = picker.LazyPick(distij, nfps, int(nfps*pick_ratio), seed=23)
#pickIndices = pool.apply_async(picker.LazyPick, 
#                               args=(distij, nfps, int(nfps*pick_ratio)))  


pick_mols = [ms[x] for x in pickIndices]

print("len(ms): ", len(ms))
print("len(pick_mols): ", len(pick_mols))


pick_cpd_names = [mol.GetProp("_Name") for mol in pick_mols]

src_pick_cpds = [ base_wkdir + 'separate_mols/' + cpdname + '.sdf'  for cpdname in pick_cpd_names]


call_mkdir_separate_mols_pick_mols = 'mkdir     ./project/%s'%GXXXX  +  '/pick_mols/   '  +   '   ./project/%s'%GXXXX + '/separate_mols  ' +   '   ./project/%s'%GXXXX + '/images/   '  +  '    2> /dev/null '
status, output = subprocess.getstatusoutput( call_mkdir_separate_mols_pick_mols )
print("status, output = ", status, output)


call_rm_sdf_files = 'rm -f   ./project/%s'%GXXXX  +  '/pick_mols/cpd*.sdf  '  +   '   ./project/%s'%GXXXX + '/%s'%PXXXX +  '.sdf   2> /dev/null '
status, output = subprocess.getstatusoutput( call_rm_sdf_files )
print("status, output = ", status, output)


all_cpd_names = [mol.GetProp("_Name") for mol in ms]


if (GXXXX == "G0000"):
    print("split total sdf file to separate mols for mutation_generation = 0 only.")
    write_mols_paralell(ms, all_cpd_names, outfile_path='./project/%s/separate_mols/'%GXXXX )
else:
    print("\nDo not create dir ./project/%s/separate_mols/\n"%GXXXX )


dst_file_path = './project/%s/pick_mols/'%GXXXX

print("The src_pick_cpds is:\n",  dst_file_path)
print('-'*60)
for ele in tqdm(src_pick_cpds):
    print(ele)
    shutil.copy(ele, dst_file_path)


cat_sdfs_to_onefile = 'cat  ./project/%s'%GXXXX  +  '/pick_mols/cpd*.sdf  >>  '  +  './project/%s'%GXXXX  + '/%s'%PXXXX  +  '.sdf '
status, output = subprocess.getstatusoutput( cat_sdfs_to_onefile )
print("status, output = ", status, output)


#----------------------------------------------------------------
draw_mols(pick_mols[:16], 
          16, 
          './project/%s/images/foo--pick-mols-in-all-mols.png'%GXXXX, 
          molsPerRow=4, 
          size=(800, 800)
          )


end_t0 = datetime.datetime.now()
elapsed_sec0 = (end_t0 - start_t0).total_seconds()
print("\nTotal running time is : " + "{:.2f}".format(elapsed_sec0) + " sec")



print("\n### End of program PG002!\n")

#End of program
