#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:42:45 2021

Murcko Decomposition

@author: tucy
"""


import sys 
import os
#os.chdir('../')
script_wkdir = os.getcwd()
sys.path.append(script_wkdir)


import pandas as pd
# import numpy as np
from rdkit import Chem
# from rdkit.Chem import AllChem
# from rdkit.Chem import Draw
from rdkit.Chem.Scaffolds import MurckoScaffold
from salam.module_MD.D_Pi_A_Enumeration import draw_mols
from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols


import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")
parser.add_argument('--num_high_freqs', type=int, default=9)

args = parser.parse_args()

print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print("args.num_high_freqs= ", args.num_high_freqs, ", type(args.num_high_freqs)= ", type(args.num_high_freqs))
NUM_HIGH_FREQS = args.num_high_freqs


#---------------------------------------------------------------------
mols_suppl = Chem.SDMolSupplier('./project/%s/%s.sdf'%(GXXXX, GXXXX))

mols_sup = [x for x in mols_suppl if x is not None]
print("len(mols_sup) = ", len(mols_sup))

mols_origin = delete_repeated_smiles_of_mols(mols_sup)
print("After delete_repeated_smiles_of_mols")
print("len(mols_origin) = ", len(mols_origin))

mols = []
cores = []
fws = []


##---- Delete AtomValenceException, if error occurs -----------------
# mols_origin_cp = mols_origin.copy()
# pop_idxs = []
# print("# Delete AtomValenceException, if error occurs.")
# for idx, mol, in zip(range(len(mols_origin_cp)), mols_origin_cp):
#     try:
#         core = MurckoScaffold.GetScaffoldForMol(mol)
#         fw = MurckoScaffold.MakeScaffoldGeneric(core)
#     except Exception as e:
#         # 访问异常的错误编号和详细信息
#         print(e.args)
#         print(str(e))
#         print(repr(e))
#         print("To be poped index is ", idx)
#         pop_idxs.append(idx)

# print("len(pop_idxs) = ", len(pop_idxs))

# if len(pop_idxs) > 0:
#     for idx in sorted(pop_idxs, reverse=True):
#         print("delete molecule: %5d" %idx )
#         mols_origin.pop(idx)
# 
# print("len(mols_origin) = ", len(mols_origin))


for mol in mols_origin:
    core = MurckoScaffold.GetScaffoldForMol(mol)
    fw = MurckoScaffold.MakeScaffoldGeneric(core)
    if Chem.MolToSmiles(core) != "":
        mols.append(mol)
        cores.append(core)
        fws.append(fw)

        
df = pd.DataFrame(data=zip(mols, cores, fws), columns=["mols", "cores", "fws"])
df["smis"] = df["mols"].apply(lambda x: Chem.MolToSmiles(x) )
df["core_smis"] = df["cores"].apply(lambda x: Chem.MolToSmiles(x) )
df["fw_smis"] = df["fws"].apply(lambda x: Chem.MolToSmiles(x) )

print(df.head())
print(df.shape)

print(df.info() )
print(df.describe() )

print("size of smis = ", len(set(list(df["smis"]))))
print("size of core_smis = ", len(set(list(df["core_smis"]))))
print("size of fw_smis = ", len(set(list(df["fw_smis"]))))

df_core_smis = df["core_smis"].value_counts()
print('-'*60)
print("df.core_smis.value_counts():  1-%d high freqs."%NUM_HIGH_FREQS)
print(df_core_smis.head(NUM_HIGH_FREQS))

core_smis_str = str(df_core_smis.head(NUM_HIGH_FREQS)).split("\n")
core_smis_str1 = [ele.strip().split()[0] for ele in core_smis_str]
core_smis_str1.pop(-1)
core_highfreq_mols = [Chem.MolFromSmiles(smi) for smi in core_smis_str1]

core_freqs = [ele.strip().split()[1] for ele in core_smis_str]
core_freqs.pop(-1)

print("core_freqs \n", core_freqs)


df_fw_smis = df["fw_smis"].value_counts()
print('-'*60)
print("df.fw_smis.value_counts():  1-%d high freqs."%NUM_HIGH_FREQS)
print(df_fw_smis.head(NUM_HIGH_FREQS))

fw_smis_str = str(df_fw_smis.head(NUM_HIGH_FREQS)).split("\n")
fw_smis_str1 = [ele.strip().split()[0] for ele in fw_smis_str]
fw_smis_str1.pop(-1)
fw_highfreq_mols = [Chem.MolFromSmiles(smi) for smi in fw_smis_str1]

fw_freqs = [ele.strip().split()[1] for ele in fw_smis_str]
fw_freqs.pop(-1)

print("fw_freqs \n", fw_freqs)


# draw_mols(mols, 
#           9, 
#           './project/G0000/images/foo001-Murcko-decomposition.png', 
#           molsPerRow=3, 
#           size=(800, 800)
#           )


draw_mols(core_highfreq_mols, 
          len(core_highfreq_mols), 
          './project/%s/images/foo-%s-Murcko-decomp-highfreq-core-mols.png'%(GXXXX, GXXXX), 
          molsPerRow=3, 
          size=(800, 800),
          legends=core_freqs,
          )

draw_mols(fw_highfreq_mols, 
          len(fw_highfreq_mols), 
          './project/%s/images/foo-%s-Murcko-decomp-highfreq-fw-mols.png'%(GXXXX, GXXXX), 
          molsPerRow=3, 
          size=(800, 800),
          legends=fw_freqs,
          )


print("\n### End of program: PG013!\n")
