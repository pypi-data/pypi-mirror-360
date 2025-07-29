#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 11:18:02 2021

@author: tucy
"""

import sys 
import os
#os.chdir('../')
script_wkdir = os.getcwd()
sys.path.append(script_wkdir)

from salam.module_MD.D_Pi_A_Enumeration import draw_mols
from rdkit import Chem
#from rdkit.Chem import AllChem

from tqdm import tqdm
from salam.module_MD.D_Pi_A_Enumeration import try_embedmolecule
from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols

#from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic
#from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic_termino_H
from salam.module_MD.OrganoMetalics_Enumeration import  debranch_CR_aromatic
from salam.module_MD.OrganoMetalics_Enumeration import  mutations_N_to_CH_aromatic


import subprocess

import numpy as np
#from scipy.special import comb

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
# parser.add_argument('--N_PATT', type=str, default='[n&R&H0,N&R&H0,N&R&H1]' )
# parser.add_argument('--CR_PATT', type=str, default='[a&R]-[A&!#1,a&!#1]' )

parser.add_argument('--N_PATT', type=str, default='[n&R&H0]' )
parser.add_argument('--CR_PATT', type=str, default='[c&R]-[A&!#1]' )

parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")
parser.add_argument('--GXXXXPLUSONE', type=str, default="G0001")

args = parser.parse_args()

print("args.N_PATT: ", args.N_PATT, type(args.N_PATT))
N_PATT = args.N_PATT

print("args.CR_PATT: ", args.CR_PATT, type(args.CR_PATT))
CR_PATT = args.CR_PATT

#TERMINO_HYDROGEN_SUBS  = [ ele.strip()  for ele in TERMINO_HYDROGEN_SUBS.strip().split(",") ]


print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.GXXXXPLUSONE, type(args.GXXXXPLUSONE))
GXXXXPLUSONE = args.GXXXXPLUSONE




def random_sampling_mols(All_mols, sample_number=1000):
    #------random sampling 1000 mols------------------------------------------
    print("The length of All_mols is : ", len(All_mols))
    if (sample_number >= 1) & ( len(All_mols) >= sample_number):
        sample_indexs = np.random.choice(len(All_mols), sample_number, replace=False)
        All_mols_sample = [All_mols[idx] for idx in sample_indexs]
        All_mols = All_mols_sample 
        print("After sampling, the length of All_mols is : ", len(All_mols))
    else:
        print("The length of All_mols is  smaller than sample_number: ", len(All_mols) , "   <   ",  sample_number )
    
    return All_mols


#------ main function -----------------------------------------------------
#--------------------------------------------------------------------------

#----- reading opt_mols sdf file -----------------
opt_sdf_path = './project/'  +  GXXXX  +   '/'  +  OXXXX   + '.sdf'
sdsuppl = Chem.SDMolSupplier(opt_sdf_path)
opt_mols = [x for x in sdsuppl if x is not None]
print("length of opt_mols is : ", len(opt_mols))


#-----------------------------------------------------------------------------
#---- create combinational compound library --------------------------
#---- via calling mutations_N_to_CH_aromatic() or debranch_CR_aromatic()

print("\n", '*'*80)

All_mols = []
for opt_mol  in opt_mols[:10]:
    # mutation_mols = mutations_CH_aromatic(opt_mol, 
    #                                       patt=Chem.MolFromSmarts('c[H]'), 
    #                                       substitute_atom=CARBON_SUB,
    #                                       substitute_atomnum=7, 
    #                                       substi_number=1, 
    #                                       sample_number=3, 
    #                                       #is_showmol=True, 
    #                                       max_subpos=10
    #                                       )

    mutation_mols = mutations_N_to_CH_aromatic(opt_mol, 
                                                patt=Chem.MolFromSmarts( N_PATT ), 
                                                #patt=Chem.MolFromSmarts('[n&R&H0,N&R&H0]'),  
                                                #patt=Chem.MolFromSmarts('[n&R&H0]'),  
                                                #patt=Chem.MolFromSmarts('[n&R]'),  
                                                #patt=Chem.MolFromSmarts('[n&R&H0,N&R]'), 
                                                substitute_group=Chem.MolFromSmarts('C-[H]'),
                                                substi_site_symbol='C',
                                                substi_number=1, 
                                                sample_number=2, 
                                                is_showmol=True,
                                                #is_showmol=False,
                                                max_subpos=10
                                                )

    
    #All_mols +=  [ opt_mol ] +  mutation_mols 
    
    # for termino_hydrogen_sub in TERMINO_HYDROGEN_SUBS:
    #     mutation_mols1 = mutations_CH_aromatic_termino_H(opt_mol, 
    #                                                     patt=Chem.MolFromSmarts('c[H]'), 
    #                                                     substitute_group=Chem.MolFromSmiles( termino_hydrogen_sub ), 
    #                                                     substi_number=1, 
    #                                                     sample_number=3, 
    #                                                     #is_showmol=True,
    #                                                     max_subpos=10
    #                                                     )


    mutation_mols1 = debranch_CR_aromatic(opt_mol, 
                                          patt=Chem.MolFromSmarts( CR_PATT ),      
                                          #patt=Chem.MolFromSmarts('[a&R]-[A&!#1,a&!#1]'),  
                                          dummylabels=(11111, 22222),
                                          #dummylabels=(0, 0),
                                          substi_atom="H", 
                                          substi_atomnum=1, 
                                          # substi_atom="F", 
                                          # substi_atomnum=9,
                                          debranch_number=2, 
                                          sample_number=8, 
                                          is_showmol=True,
                                          #is_showmol=False,
                                          max_debranchpos=10
                                        )


        
    All_mols +=  [ opt_mol ] +  mutation_mols + mutation_mols1
    

print("The length of All_mols is : ", len(All_mols))


draw_mols(All_mols, 
          16, 
          './project/%s/images/foo011a--mutation-mols-demo.png'%GXXXX, 
          molsPerRow=4, 
          size=(800, 800)
          )


All_mols  =  delete_repeated_smiles_of_mols(All_mols)
print("After delete_repeated_smiles_of_mols, the length of All_mols is : ", len(All_mols))

#------random sampling 1000 mols-----------------------------------------------------
All_mols = random_sampling_mols(All_mols, sample_number=1000)

cpd_names = [ "cpd-%05d" % (i+1) for i in range(len(All_mols)) ]
for mol, cpd_name in zip(All_mols, cpd_names):
    mol.SetProp("_Name", cpd_name )


#---- write molecules to SD File ------------------------------- 
call_mkdir_GXXXXplus1 = 'mkdir  ./project/' +  GXXXXPLUSONE  +  '/  2>/dev/null  '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXXplus1 )
print("mkdir  ./project/GXXXX+1/;    status, output = ", status, output)

outfile_path = './project/'   +   GXXXXPLUSONE   +  '/'   + GXXXXPLUSONE + 'a.sdf'
All_mols_w = Chem.SDWriter(outfile_path)
for m in tqdm(All_mols): 
    m_temp = Chem.AddHs(m)
    m1_temp, nb_try_EmbedMolecule = try_embedmolecule(m_temp)
    All_mols_w.write(m1_temp)




print("\n### End of program: PG012a!\n")