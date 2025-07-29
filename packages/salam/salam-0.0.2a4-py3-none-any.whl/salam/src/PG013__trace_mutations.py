#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:53:00 2021

Using scikit-learn with RDKit

@author: tucy
"""


from salam.module_MD.D_Pi_A_Enumeration import draw_mols
from rdkit import Chem
#from rdkit.Chem import AllChem

from tqdm import tqdm
from salam.module_MD.D_Pi_A_Enumeration import try_embedmolecule
from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols

from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic
from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic_termino_H
import subprocess

import numpy as np
#from scipy.special import comb
#import os

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--carbon_sub', type=str, default='N' )
parser.add_argument('--termino_hydrogen_subs', type=list, default=[ '*F',  '*C#N',  '*OC',  '*N(C)C' ] )

parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")
parser.add_argument('--GXXXXPLUSONE', type=str, default="G0001")

args = parser.parse_args()

print("args.carbon_sub: ", args.carbon_sub, type(args.carbon_sub))
CARBON_SUB = args.carbon_sub

print("args.termino_hydrogen_subs: ", args.termino_hydrogen_subs, type(args.termino_hydrogen_subs))
TERMINO_HYDROGEN_SUBS = args.termino_hydrogen_subs

#TERMINO_HYDROGEN_SUBS  = [ ele.strip()  for ele in TERMINO_HYDROGEN_SUBS.strip().split(",") ]


print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.GXXXXPLUSONE, type(args.GXXXXPLUSONE))
GXXXXPLUSONE = args.GXXXXPLUSONE


# script_call_path = os.getcwd()
# print("script_call_path:\n", script_call_path)
# print("script name:\n")
# print(__file__)
# print("change to ../")
# os.chdir( "../" )



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
#---- via calling mutations_CH_aromatic() or mutations_CH_aromatic_termino_H()

print("\n", '*'*80)

All_mols = []


carbon_or_hydrogen_subs = [ CARBON_SUB ] +  TERMINO_HYDROGEN_SUBS

subs_mols = [ [] for i in range(len(carbon_or_hydrogen_subs))]



for opt_mol  in opt_mols[:]:
    mutation_mols = mutations_CH_aromatic(opt_mol, 
                                          patt=Chem.MolFromSmarts('c[H]'), 
                                          substitute_atom=CARBON_SUB,
                                          substitute_atomnum=7, 
                                          substi_number=1, 
                                          sample_number=3, 
                                          #is_showmol=True, 
                                          max_subpos=10
                                          )
    
    All_mols +=  [ opt_mol ] +  mutation_mols
    subs_mols[0] +=  mutation_mols
    
    for termino_hydrogen_sub, i in zip( TERMINO_HYDROGEN_SUBS,  range(1, len(carbon_or_hydrogen_subs)) ):
        mutation_mols1 = mutations_CH_aromatic_termino_H(opt_mol, 
                                                        patt=Chem.MolFromSmarts('c[H]'), 
                                                        substitute_group=Chem.MolFromSmiles( termino_hydrogen_sub ), 
                                                        substi_number=1, 
                                                        sample_number=3, 
                                                        #is_showmol=True,
                                                        max_subpos=10
                                                        )
        
        subs_mols[i]  +=  mutation_mols1
        
        All_mols +=  mutation_mols1
    

print("The length of All_mols is : ", len(All_mols))


draw_mols(All_mols, 
          16, 
          './project/%s/images/foo011--mutation-mols-demo.png'%GXXXX, 
          molsPerRow=4, 
          size=(800, 800)
          )


All_mols  =  delete_repeated_smiles_of_mols(All_mols)
print("After delete_repeated_smiles_of_mols, the length of All_mols is : ", len(All_mols))

new_subs_mols = []
for i in range(len(carbon_or_hydrogen_subs)):
    subs_mols[i]  =  delete_repeated_smiles_of_mols(subs_mols[i])
    
    #subs_mols[i] = [ mol for mol in opt_mols ]
    new_sub_mols = list( set(subs_mols[i]).difference(set(opt_mols)) )
    new_subs_mols.append( new_sub_mols )



#------random sampling 1000 mols-----------------------------------------------------
All_mols = random_sampling_mols(All_mols, sample_number=1000)

cpd_names = [ "cpd-%05d" % (i+1) for i in range(len(All_mols)) ]
for mol, cpd_name in zip(All_mols, cpd_names):
    mol.SetProp("_Name", cpd_name )


#---- write molecules to SD File ------------------------------- 
call_mkdir_GXXXXplus1 = 'mkdir  ./project/' +  GXXXXPLUSONE  +  '/  2>/dev/null  '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXXplus1 )
print("mkdir  ./project/GXXXX+1/;    status, output = ", status, output)

outfile_path = './project/'   +   GXXXXPLUSONE   +  '/'   + GXXXXPLUSONE + '.sdf'
All_mols_w = Chem.SDWriter(outfile_path)
for m in tqdm(All_mols): 
    m_temp = Chem.AddHs(m)
    m1_temp, nb_try_EmbedMolecule = try_embedmolecule(m_temp)
    All_mols_w.write(m1_temp)




print("\nEnd of program: PG011!\n")
