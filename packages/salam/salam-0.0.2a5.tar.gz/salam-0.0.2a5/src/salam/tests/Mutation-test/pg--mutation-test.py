#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 15:26:07 2023

@author: tucy
"""


from rdkit import Chem

from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols
from salam.module_MD.D_Pi_A_Enumeration import write_mols_paralell
from salam.module_MD.OrganoMetalics_Enumeration import mutual_mutations_mols
from salam.module_MD.Crossover import get_numatoms


from time import time
import argparse


parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--output_lib_type', type=str, default="csv")

args = parser.parse_args()

print("output_lib_type: ", args.output_lib_type, type(args.output_lib_type))
output_lib_type = args.output_lib_type

#------------output_lib_type = "sdf" or "csv"-------------
#------------ "csv" is used for test purpose 
#------------ "sdf" is used for practical generation of compound library, which can be used for subsequent computation.  
#------------ output_lib_type = "csv"



#_________________________________________________________________________________
#*********************************************************************************
#-----__main__ function begins here ----------------------------------------------
if __name__ == '__main__':

    print("Begins")
    print("-"*80)

    start_time = time()

    basemol_suppl = Chem.SmilesMolSupplier('./parent-mols.smi',
                                           titleLine=False
                                           )
    
    base_mols = [x for x in basemol_suppl if x is not None]
    
    print("len(base_mols) = ", len(base_mols))


    Mut_libs = mutual_mutations_mols(BASE_MOLS=base_mols, 
                                     CARBON_SUB='N', 
                                     TERMINO_HYDROGEN_SUB='*C#N',
                                     MAX_SUBPOS=16, 
                                     SUBSTI_NUMBER_CARBON=0, 
                                     SAMPLE_NUMBER_CARBON=0, 
                                     SUBSTI_NUMBER_HYDROGEN=0, 
                                     SAMPLE_NUMBER_HYDROGEN=0)


    sdf_name = './Mut_libs.sdf'
    csv_name = './Mut_libs.csv'
    dir_name = './Mut_libs'

    
    print('^'*60)
    print("### Summary of libs:")    
    print("len(Mut_libs) = ", len(Mut_libs) )
    Mut_libs = delete_repeated_smiles_of_mols(Mut_libs, is_sanitize=True)
       
    print("After deleting redundance, len(Mut_libs) = ", len(Mut_libs) )
       
    print("Sort list by NumAtoms.")
    Mut_libs = sorted(Mut_libs, 
                     key=get_numatoms, 
                     reverse=False
                     )
       
    print("len(Mut_libs) = ", len(Mut_libs))
       
    print('-'*30)
    print("!!! The complete set of reconstructed molecules in Mut_libs.")
    for mol,i in zip(Mut_libs,range(len(Mut_libs))):
        print(i+1, " : ",  Chem.MolToSmiles(mol))


    #---- set Names for mols ------------------------------- 
    All_mols1 = Mut_libs
    All_smis1 = [ Chem.MolToSmiles(mol) for mol in All_mols1 ]
    cpd_names1 = [ "cpd-%05d" % (i+1) for i in range(len(All_mols1)) ]
    for mol, cpd_name in zip(All_mols1, cpd_names1):
        mol.SetProp("_Name", cpd_name )
    
    if (output_lib_type == "sdf") or (output_lib_type == "SDF"): 
        
        write_mols_paralell(All_mols1, 
                            cpd_names1, 
                            outfile_path='%s/'%dir_name
                            )
        
    
    elif (output_lib_type == "csv") or (output_lib_type == "CSV"): 
        with open(csv_name, 'w') as fp:
            fp.write("cpdname,smile\n")
            for cpd_name, smi in zip(cpd_names1, All_smis1):
                fp.write("%s,%s\n"%(cpd_name,smi))
    
    else:
        print("Parameter output_lib_type must be either csv or sdf.")
            


    end_time = time()
    run_time = (end_time - start_time)/60.
    print("### The CPU time is %15.3f min.\n"%run_time)

    print("\nFinished!")      
