#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 18 08:45:09 2022

Chem.RDKFingerprint
DataStructs.FingerprintSimilarity

The default set of parameters used by the fingerprinter is:
    - minimum path size: 1 bond - maximum path size: 7 bonds 
    - fingerprint size: 2048 bits 
    - number of bits set per hash: 2 
    - minimum fingerprint size: 64 bits 
    - target on-bit density 0.0

Available similarity metrics include 
Tanimoto, Dice, Cosine, Sokal, Russel, Kulczynski, McConnaughey, and Tversky.

@author: tucy
"""


import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--GXXXX', type=str, default="G0000")

args = parser.parse_args()

print("args.GXXXX = ", args.GXXXX, " , type(args.GXXXX) = ",  type(args.GXXXX))
GXXXX = args.GXXXX


import sys 
import os
#os.chdir('../')
script_wkdir = os.getcwd()
sys.path.append(script_wkdir)


from salam.module_MD.Metrics import get_intersection_plus_smiles
from salam.module_MD.Metrics import get_centroid
# from salam.module_MD.Metrics import compute_similarity_matrix
from salam.module_MD.Metrics import map_molslibs_by_similarity
from salam.module_MD.Metrics import draw_mols_and_show

from salam.module_MD.Metrics import load_mols_in_sdf


#-----------------------------------------------------------------------------
#---- main here --------------------------------------------------------------
if __name__ == "__main__":
    print("Begin of program.")
    
    # -------- two steps -----------------------------------------------------
    # smis1 = [ 'CCCNCCO', 'CCNCCO', 'CC', 'COOC', 'CCCOOC', \
    #             'CCCO', 'CCCCO', 'CCOC', 'CCO', 'COC',\
    #                 'CCOOC', 'CCCCOC', 'CCC', 'CCCC', 'CNCCO'
    #               ]
        
    # smis2 = [ 'CCCNCCO', 'CCNCCO', 'CCCCOOC', 'CCCNCOC', 'CNCCOC',\
    #             'CC', 'CCCOOC', 'CCCNCCOC', 'CCCO', 'CCNCCOC',\
    #                 'CCCCO', 'CCO', 'CCNCOC', 'CCOOC', 'CCC',\
    #                     'CCCC', 'CNCOC', 'CNCCO' 
    #                   ]
        
    print("-"*60) 
    mutation_generation = int( GXXXX[1:] )
    GXXXX_PLUS1 = "G%04d"%(mutation_generation - 1)
    GXXXX_sdf_path1 = './project/'  +  GXXXX    +  '/'  + GXXXX  +  '.sdf'
    GXXXX_sdf_path2 = './project/'  +  GXXXX_PLUS1    +  '/'  + GXXXX_PLUS1  +  '.sdf'
    
    print("Loading sdf for FPSimilarity map, the path1 is:\n", GXXXX_sdf_path1)

    _ , smis1 = load_mols_in_sdf(sdf_path=GXXXX_sdf_path1)

    centriod_smi1, inner_max_ave_sim1 = get_centroid(smis=smis1)
    
    draw_mols_and_show([ centriod_smi1 ],
                        figname='./project/%s/images/foo--mols1-centriod.png'%GXXXX,
                        molsPerRow=1,
                        subImgSize=(800, 800)
                        )

    print('-'*60)
    if (mutation_generation > 0):
        print("Loading sdf for FPSimilarity map, the path2 is:\n", GXXXX_sdf_path2)        
        _ , smis2 = load_mols_in_sdf(sdf_path=GXXXX_sdf_path2)

        centriod_smi2, inner_max_ave_sim2 = get_centroid(smis=smis2)
        
        # draw_mols_and_show([ centriod_smi2 ],
        #                     figname='./project/%s/images/foo--mols1-centriod.png'%GXXXX_PLUS1,
        #                     molsPerRow=1,
        #                     subImgSize=(800, 800)
        #                     ) 


        intersection_smis, smis1_rev, smis2_rev, exchange_flag = get_intersection_plus_smiles(smis1=smis1, 
                                                                                              smis2=smis2
                                                                                              )
    
        new_smis1, new_smis2, mat_sim, inter_max_app_sim = map_molslibs_by_similarity(smis1=smis1_rev, 
                                                                                        smis2=smis2_rev,
                                                                                        fpSize=2048,
                                                                                        is_return_max_app_sim=True
                                                                                        ) 
    
    
        # draw_mols_and_show(new_smis1,
        #                     figname='./project/%s/images/foo--FPSmap-mols1.png'%GXXXX,
        #                     molsPerRow=3,
        #                     subImgSize=(800, 800),
        #                     num_of_mols=9
        #                     )
    
        # draw_mols_and_show(new_smis2,
        #                     figname='./project/%s/images/foo--FPSmap-mols2.png'%GXXXX,
        #                     molsPerRow=3,
        #                     subImgSize=(800, 800),
        #                     num_of_mols=9
        #                     )
    
        print("len(smis1) = ", len(smis1))
        print("len(smis2) = ", len(smis2))    
        print("exchange_flag = ", exchange_flag)
        print("len(smis1_rev) = ", len(smis1_rev))
        print("len(smis2_rev) = ", len(smis2_rev))
        print("len(intersection_smis) = ", len(intersection_smis))
    
        print("\ncentriod_smi1:\n", centriod_smi1)
        print("centriod_smi2:\n", centriod_smi2)
        
        print("inner_max_ave_sim1 = %10.3f"%inner_max_ave_sim1)
        print("inner_max_ave_sim2 = %10.3f"%inner_max_ave_sim2)
        
        print("inter_max_app_sim = %10.3f"%inter_max_app_sim)

        #----------- store data for mutation_diagram ---------------------------
        print("\nData for mutation_diagram is stored in /project/mutation_diagram.csv\n")
        with open('./project/mutation_diagram.csv', 'a+') as fr:
            fr.write('%5d'%mutation_generation + \
                     ', %s'%centriod_smi1 + \
                         ", %5d"%len(smis1) + \
                             ', %10.3f'%inner_max_ave_sim1 + \
                                 ', %10.3f'%inter_max_app_sim + "\n")

        
    else:
        print("mutation_generation = 0. Do not compute inter_max_app_sim.")
        print("set inter_max_app_sim =  1.000")
        inter_max_app_sim =  1.000
        
        print("len(smis1) = ", len(smis1))
        print("\ncentriod_smi1:\n", centriod_smi1)
        print("inner_max_ave_sim1 = %10.3f"%inner_max_ave_sim1)       

        
        #----------- store data for muation_diagram ---------------------------
        print("\nData for mutation_diagram is stored in /project/mutation_diagram.csv\n")
        with open('./project/mutation_diagram.csv', 'w') as fr:
            fr.write("mutation_generation,centriod_smi1,len_smis1,inner_max_ave_sim1,inter_max_app_sim\n")
            fr.write('%5d'%mutation_generation + \
                     ', %s'%centriod_smi1 + \
                         ", %5d"%len(smis1) + \
                             ', %10.3f'%inner_max_ave_sim1 + \
                                 ', %10.3f'%inter_max_app_sim + "\n")
    
    

    print("\nEnd of PG015!\n")

