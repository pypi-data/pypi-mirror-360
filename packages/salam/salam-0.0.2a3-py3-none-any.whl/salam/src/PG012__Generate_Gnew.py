#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:53:00 2021

Using scikit-learn with RDKit

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

# from tqdm import tqdm
# from salam.module_MD.D_Pi_A_Enumeration import try_embedmolecule
from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols
from salam.module_MD.D_Pi_A_Enumeration import write_mols_paralell

from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic
from salam.module_MD.OrganoMetalics_Enumeration import mutations_CH_aromatic_termino_H
import subprocess

import numpy as np
#from scipy.special import comb

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")

parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")
parser.add_argument('--GXXXXPLUSONE', type=str, default="G0001")

parser.add_argument('--carbon_sub', type=str, default='N' )
#parser.add_argument('--termino_hydrogen_subs', type=list, default=[ '*F',  '*C#N',  '*OC',  '*N(C)C' ], action='append')
parser.add_argument('--termino_hydrogen_subs', action='append')

parser.add_argument('--max_subpos', type=int, default=10)
parser.add_argument('--substi_number_carbon', type=int, default=1)
parser.add_argument('--sample_number_carbon', type=int, default=6)
parser.add_argument('--substi_number_hydrogen', type=int, default=1)
parser.add_argument('--sample_number_hydrogen', type=int, default=6)

parser.add_argument('--is_substi_carbon', type=int, default=1 )
parser.add_argument('--is_substi_hydrogen', type=int, default=1 )

parser.add_argument('--parent_optmols_size', type=int, default=-1 )


args = parser.parse_args()


print("args.carbon_sub: ", args.carbon_sub, type(args.carbon_sub))
CARBON_SUB = args.carbon_sub

print("args.termino_hydrogen_subs: ", args.termino_hydrogen_subs, type(args.termino_hydrogen_subs))
TERMINO_HYDROGEN_SUBS = args.termino_hydrogen_subs

#TERMINO_HYDROGEN_SUBS  = [ ele.strip()  for ele in TERMINO_HYDROGEN_SUBS.strip().split(",") ]
#'max_subpos', 'substi_number_carbon', 'sample_number_carbon', 'substi_number_hydrogen', 'sample_number_hydrogen'

print("args.max_subpos: ", args.max_subpos, type(args.max_subpos ))
print("args.substi_number_carbon: ", args.substi_number_carbon, type(args.substi_number_carbon ))
print("args.sample_number_carbon: ", args.sample_number_carbon, type(args.sample_number_carbon ))
print("args.substi_number_hydrogen: ", args.substi_number_hydrogen, type(args.substi_number_hydrogen ))
print("args.sample_number_hydrogen: ", args.sample_number_hydrogen, type(args.sample_number_hydrogen ))

MAX_SUBPOS = args.max_subpos 
SUBSTI_NUMBER_CARBON = args.substi_number_carbon 
SAMPLE_NUMBER_CARBON = args.sample_number_carbon 
SUBSTI_NUMBER_HYDROGEN = args.substi_number_hydrogen
SAMPLE_NUMBER_HYDROGEN = args.sample_number_hydrogen 

print("args.is_substi_carbon: ", args.is_substi_carbon, type(args.is_substi_carbon))
print("args.is_substi_hydrogen: ", args.is_substi_hydrogen, type(args.is_substi_hydrogen))

IS_SUBSTI_CARBON = bool( args.is_substi_carbon )
IS_SUBSTI_HYDROGEN = bool( args.is_substi_hydrogen )


if TERMINO_HYDROGEN_SUBS is None:
    TERMINO_HYDROGEN_SUBS = [ '*F',  '*C#N',  '*OC',  '*N(C)C' ] 
    

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.GXXXXPLUSONE, type(args.GXXXXPLUSONE))
GXXXXPLUSONE = args.GXXXXPLUSONE


print("args.parent_optmols_size: ", args.parent_optmols_size, type(args.parent_optmols_size))
PARENT_OPTMOLS_SIZE = args.parent_optmols_size 


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

if ( PARENT_OPTMOLS_SIZE > 0 ):
    print("PARENT_OPTMOLS_SIZE = ", PARENT_OPTMOLS_SIZE )
    print("Restrict the size of parent opt_mols by this para.")
    opt_mols = opt_mols[:PARENT_OPTMOLS_SIZE]
else:
    print("All mols in opt_mols will be used.")


print("length of opt_mols is : ", len(opt_mols))


#-----------------------------------------------------------------------------
#---- create combinational compound library --------------------------
#---- via calling mutations_CH_aromatic() or mutations_CH_aromatic_termino_H()

print("\n", '*'*80)

All_mols = []
for opt_mol  in opt_mols:
    
    All_mols +=  [ opt_mol ]
    
    if (IS_SUBSTI_CARBON == True):
        mutation_mols = mutations_CH_aromatic(opt_mol, 
                                              patt=Chem.MolFromSmarts('c[H]'), 
                                              substitute_atom=CARBON_SUB,
                                              substitute_atomnum=7, 
                                              substi_number=SUBSTI_NUMBER_CARBON, 
                                              sample_number=SAMPLE_NUMBER_CARBON, 
                                              #is_showmol=True, 
                                              max_subpos=MAX_SUBPOS
                                              )
        All_mols +=  mutation_mols     
    else:
        print("!!! IS_SUBSTI_CARBON is False. No substitutions occur at site of carbons.")
    

    if (IS_SUBSTI_HYDROGEN == True):     
        for termino_hydrogen_sub in TERMINO_HYDROGEN_SUBS:
            mutation_mols1 = mutations_CH_aromatic_termino_H(opt_mol, 
                                                            patt=Chem.MolFromSmarts('c[H]'), 
                                                            substitute_group=Chem.MolFromSmiles( termino_hydrogen_sub ), 
                                                            substi_number=SUBSTI_NUMBER_HYDROGEN, 
                                                            sample_number=SAMPLE_NUMBER_HYDROGEN, 
                                                            #is_showmol=True,
                                                            max_subpos=MAX_SUBPOS
                                                            )
            All_mols +=  mutation_mols1
    else:
        print("!!! IS_SUBSTI_HYDROGEN is False. No substitutions occur at site of carbons.")
    

print("The length of All_mols is : ", len(All_mols))


draw_mols(All_mols, 
          16, 
          './project/%s/images/foo011--mutation-mols-demo.png'%GXXXX, 
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
print("\nWrite to sdf file.\n")

call_mkdir_GXXXXplus1 = 'mkdir  ./project/' +  GXXXXPLUSONE  +  '/  2>/dev/null  '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXXplus1 )
print("mkdir  ./project/GXXXXPLUSONE/;    status, output = ", status, output)

outdir_path = './project/'   +   GXXXXPLUSONE   +  '/separate_mols/'

call_mkdir_GXXXXplus1_separate_mols = 'mkdir   ' +  outdir_path  +  '    2>/dev/null  '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXXplus1_separate_mols )
print("mkdir  ./project/GXXXXPLUSONE/separate_mols/;    status, output = ", status, output)        

status, output = subprocess.getstatusoutput( 'rm   -f    ' + outdir_path + 'cpd-*.sdf   2>/dev/null ' )
print("remove ./project/GXXXXPLUSONE/separate_mols/cpd-*.sdf.  status, output = ", status, output)

print("call write_mols_paralell(), the separate mols are written to dir:  %s"%outdir_path )
write_mols_paralell(All_mols, cpd_names, outfile_path=outdir_path)

print("remove  ./project/GXXXXPLUSONE/GXXXXPLUSONE.sdf")
status, output = subprocess.getstatusoutput( 'rm  -f   ./project/%s'%GXXXXPLUSONE  +  '/%s.sdf'%GXXXXPLUSONE  +  '   2>/dev/null ' )
print("status, output = ", status, output)

cat_sdfs_to_onefile = 'cat   '  +  outdir_path  + 'cpd*.sdf  >>  '  +  './project/%s'%GXXXXPLUSONE  + '/%s.sdf  '%GXXXXPLUSONE
status, output = subprocess.getstatusoutput( cat_sdfs_to_onefile )
print("cat cpd*.sdf to GXXXXPLUSONE.sdf.   status, output = ", status, output)


print("\n### End of program: PG012!\n")
