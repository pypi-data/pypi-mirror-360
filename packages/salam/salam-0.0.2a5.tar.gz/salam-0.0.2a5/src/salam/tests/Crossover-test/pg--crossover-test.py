#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 15:26:07 2023

@author: tucy
"""


from rdkit import Chem

from salam.module_MD.D_Pi_A_Enumeration import delete_repeated_smiles_of_mols
# from D_Pi_A_Enumeration import try_embedmolecule
from salam.module_MD.D_Pi_A_Enumeration import write_mols_paralell
# from Crossover import crossover_two_mols_break_singlebond
# from Crossover import crossover_two_mols_break_twobondsring
from salam.module_MD.Crossover import crossover_mols_parallel
from salam.module_MD.Crossover import screen_unfavored_rings
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


    Slibs, Dlibs, SDlibs = crossover_mols_parallel(parent_mols_smis='./parent-mols.smi',
                                                   MolWt_expansion_ratios=[-0.20, 0.20],
                                                   RS_LIMITS=[4, 7], 
                                                   NAR_SHIFTS=[-1, 1],
                                                   type1_smarts=['[a&R]-[R]', '[a&R]-[!R]'],    
                                                   type2_smarts=['a1:a:a:a:a:a1', 'a1:a:a:a:a1'],
                                                   )


    #--- screen_unfavored_rings -------------------------------------------
    SDlibs_rev, SDlibs_delete = screen_unfavored_rings(SDlibs, 
                                                       smarts_list=['[#16&r6]', '[#34&r6]'],
                                                       )
    

    all_libs = [ Slibs, Dlibs, SDlibs, SDlibs_rev, SDlibs_delete ]
    sdf_names = ['./Slibs.sdf', './Dlibs.sdf', './SDlibs.sdf', './SDlibs_rev.sdf', './SDlibs_delete.sdf']
    csv_names = ['./Slibs.csv', './Dlibs.csv', './SDlibs.csv', './SDlibs_rev.csv', './SDlibs_delete.csv']
    dir_names = ['./Slibs', './Dlibs', './SDlibs', './SDlibs_rev', './SDlibs_delete']

    
    print('^'*60)
    print("### Summary of libs:")    
    for tmplibs, sdf_name, csv_name, dir_name  in zip(all_libs, sdf_names, csv_names, dir_names):
        print("len(tmplibs) = ", len(tmplibs) )
        tmplibs = delete_repeated_smiles_of_mols(tmplibs, is_sanitize=True)
           
        print("After deleting redundance, len(tmplibs) = ", len(tmplibs) )
           
        print("Sort list by NumAtoms.")
        tmplibs = sorted(tmplibs, 
                         key=get_numatoms, 
                         reverse=False
                         )
           
        print("len(tmplibs) = ", len(tmplibs))
           
        print('-'*30)
        print("!!! The complete set of reconstructed molecules in tmplibs.")
        for mol,i in zip(tmplibs,range(len(tmplibs))):
            print(i+1, " : ",  Chem.MolToSmiles(mol))
    
    
        #---- set Names for mols ------------------------------- 
        All_mols1 = tmplibs
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
