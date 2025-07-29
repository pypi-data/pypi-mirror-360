#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 15:26:07 2023

@author: tucy
"""


from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
# from rdkit.Chem.Draw import rdMolDraw2D

from D_Pi_A_Enumeration import find_label_atom_idx
# from D_Pi_A_Enumeration import find_label_atom_idxs
from D_Pi_A_Enumeration import replace_dummy_by_Po_label_v1
from D_Pi_A_Enumeration import D_A_Enumeration_new
from D_Pi_A_Enumeration import delete_repeated_smiles_of_mols
from D_Pi_A_Enumeration import draw_mols
from D_Pi_A_Enumeration import delete_label_atom
# from D_Pi_A_Enumeration import delete_label_atoms
from D_Pi_A_Enumeration import try_embedmolecule

import numpy as np
from itertools import combinations
import pandas as pd
from rdkit import DataStructs
from rdkit.Chem import Descriptors

from tqdm import tqdm
from joblib import Parallel, delayed



#------------------------------------------------------------------------
def set_atomNotes(mol):
    mol_tmp = mol
    # Iterate over the atoms
    for atom in mol_tmp.GetAtoms():
        # For each atom, set the property "atomNote" to a index+1 of the atom
        atom.SetProp("atomNote", str(atom.GetIdx() + 1))
    
    return mol_tmp        


#---------------------------------------------------------------------------
def get_num_of_rings(mh):
    m = Chem.RemoveHs(mh)
    ri = m.GetRingInfo()
    return ri.NumRings()


#---------------------------------------------------------------------------
def get_num_of_aromaticrings(mh):
    m = Chem.RemoveHs(mh)
    ring_info = m.GetRingInfo()
    atoms_in_rings = ring_info.AtomRings()
    num_aromatic_ring = 0
    for ring in atoms_in_rings:
        aromatic_atom_in_ring = 0
        for atom_id in ring:
            atom = m.GetAtomWithIdx(atom_id)
            if atom.GetIsAromatic():
                aromatic_atom_in_ring += 1
        if aromatic_atom_in_ring == len(ring):
            num_aromatic_ring += 1
            
    return num_aromatic_ring


#---------------------------------------------------------------------------
def get_largest_ring_size(mh):
    m = Chem.RemoveHs(mh)
    ri = m.GetRingInfo()
    largest_ring_size = max((len(r) for r in ri.AtomRings()), default=0)
    return largest_ring_size


#---------------------------------------------------------------------------
def get_smallest_ring_size(mh):
    m = Chem.RemoveHs(mh)
    ri = m.GetRingInfo()
    smallest_ring_size = min((len(r) for r in ri.AtomRings()), default=6)
    return smallest_ring_size


#---------------------------------------------------------------------------
def get_numatoms(mol):
    return mol.GetNumAtoms()


#---------------------------------------------------------------------------
def delete_unbroken_mols(mols, pmol, numatom_shift=3):
    mols_list = mols
    print("Entering func: delete_unbroken_mols()")
    print("len(mols_list) = ", len(mols_list))
    equal_numatoms_idxs = []
    pm_numatoms = pmol.GetNumAtoms()
    print("pm_numatoms = ", pm_numatoms)
    for idx in range(len(mols_list)):
        tmp_numatoms = mols_list[idx].GetNumAtoms()
        
        # print("tmp_numatoms = ", tmp_numatoms)
        
        if tmp_numatoms >= (pm_numatoms + numatom_shift):
            equal_numatoms_idxs.append(idx)
                        
          
    if len(equal_numatoms_idxs) > 0:
        equal_numatoms_idxs_sorted = sorted(equal_numatoms_idxs, 
                                            reverse=True
                                            ) 
        
        print("### Delete the following mols:")                   
        for idx1 in equal_numatoms_idxs_sorted:
            print(Chem.MolToSmiles( mols_list[idx1] ))

        for idx1 in equal_numatoms_idxs_sorted:
            mols_list.pop(idx1)            
    

    print("After deleting, len(mols_list) = ", len(mols_list))

    return mols_list        


#---------------------------------------------------------------------------
def sort_mols_by_anverage_fingerprint_similarity(mols, 
                                                 pmol1, 
                                                 pmol2,
                                                 is_shown=False
                                                 ):

    mols = np.array(mols)
    
    df_fps = pd.DataFrame(data=mols, columns=['mols'])
    df_fps['smiles'] = df_fps['mols'].apply(lambda x: Chem.MolToSmiles(x) )
    
    df_fps['fps'] = df_fps['mols'].apply(lambda x: AllChem.GetMorganFingerprintAsBitVect(x, 2, nBits=1024) )
    
    fp1 = AllChem.GetMorganFingerprintAsBitVect(pmol1, 2, nBits=1024)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(pmol2, 2, nBits=1024)
    
    df_fps['fps_mol1'] = df_fps['fps'].apply(lambda fp: DataStructs.DiceSimilarity(fp, fp1) )
    df_fps['fps_mol2'] = df_fps['fps'].apply(lambda fp: DataStructs.DiceSimilarity(fp, fp2) )
    df_fps['fps_anv'] = 0.5*(df_fps['fps_mol1'] + df_fps['fps_mol2'])
    
    print("df_fps.describe(): ", df_fps.describe())
    print("df_fps.head(): ", df_fps.head())
    
    df_fps.sort_values(by="fps_anv", ascending=False, inplace=True)
    
    print("After sorting, df_fps.describe(): ", df_fps.describe())
    print("df_fps.head(): ", df_fps.head())
    
    mols_sorted = df_fps['mols'].tolist()
    
    print('-'*30)
    print("fps_anv, smiles:")
    for smi, fp_anv in zip(df_fps['smiles'].tolist(), df_fps['fps_anv'].tolist()):
        print("%10.3f, %s"%(fp_anv, smi) )
        
    
    if is_shown == True:
        for mol,i in zip(mols_sorted, range(30)):
            Draw.ShowMol(mol, 
                         size=(600, 600), 
                         title="the combined %d th molecule"%i
                         )

    return df_fps  


#---------------------------------------------------------------------------
def crossover_two_mols_break_singlebond(m1, 
                                        m2, 
                                        type1_smarts=['[a&R]-[R]'], 
                                        typestr="aR-R",
                                        RS_LIMITS=[4, 9],
                                        MolWt_expansion_ratios=[-0.10, 0],
                                        NAR_SHIFTS=[-1, 0],
                                        is_shown=False,
                                        nsamplesplot=30,
                                        is_draw=False
                                        ):
    #----------- get m1_lista --------------------------------------------
    # type1_smart = '[R]-[R]'
    # type1_smart = '[a&R]-[R]'
    # type1_smart = '[a&R]-[a&R]'
    # type1_smart = '[a&R]-[!R]'
    # type1_smarts = [ '[a&R]-[R]', '[a&R]-[!R]' ]

    combine_lista_slrs = []
    combine_lista_slrs_slmr = []    
    combine_lista_slrs_slmr_slnar = []
    
    
    m1_lista = [ ]
    
    bis1 = []
    for type1_smart in type1_smarts:
        bis1 += m1.GetSubstructMatches( Chem.MolFromSmarts(type1_smart) )
        
    
    if len(bis1) == 0:
        print("CAUTIONS: len(bis1) = 0")
        print("Just return the original two molecules.")
        return [ m1, m2 ]
    else:
        print("len(bis1) > 0 is Ture.")
         
        
    bs1 = []
    labels1 = []
    
    begin_label1 = 1000
    end_label1 = 2000
    
    print("len(bis1) = ", len(bis1))
    
    for bi in bis1:
        b = m1.GetBondBetweenAtoms(bi[0], bi[1])
        if b.GetBeginAtomIdx() == bi[0]:
            labels1.append((begin_label1, end_label1))
        else:
            labels1.append((end_label1, begin_label1))
        bs1.append(b.GetIdx())
        
        begin_label1 += 2000
        end_label1 += 2000
        
    print("bis1:")
    print(bis1)
    print("labels1:")
    print(labels1)
    print("bs1:")
    print(bs1)
    
    print("mol1 smiles: ", Chem.MolToSmiles(m1) )
    for i in range(len(bs1)):
        nm1 = Chem.FragmentOnBonds(m1, bs1[i:i+1], dummyLabels=labels1[i:i+1])
        # print("Fragemetal mol on bond index %d with dummylabels %s: \n"%(bs1[i], labels1[i]), Chem.MolToSmiles(nm1, True) )
        rs1 = Chem.GetMolFrags(nm1, asMols=True) 
        rs1_ = list(rs1)
        m1_lista += rs1_
    
    
    #----------- get m2_lista --------------------------------------------
    m2_lista = [ ] 
    
    bis2 = []
    for type1_smart in type1_smarts:
        bis2 += m2.GetSubstructMatches( Chem.MolFromSmarts(type1_smart) )


    if len(bis2) == 0:
        print("CAUTIONS: len(bis2) = 0")
        print("Just return the original two molecules.")
        return [ m1, m2 ]
    else:
        print("len(bis2) > 0 is Ture.")

        
    bs2 = []
    labels2 = []
    
    begin_label2 = 1000
    end_label2 = 2000
    
    print("len(bis2) = ", len(bis2))
    
    for bi in bis2:
        b = m2.GetBondBetweenAtoms(bi[0], bi[1])
        if b.GetBeginAtomIdx() == bi[0]:
            labels2.append((begin_label2, end_label2))
        else:
            labels2.append((end_label2, begin_label2))
        bs2.append(b.GetIdx())
        
        begin_label2 += 2000
        end_label2 += 2000
        
    print("bis2:")
    print(bis2)
    print("labels2:")
    print(labels2)
    print("bs2:")
    print(bs2)
    
    print("mol2 smiles: ", Chem.MolToSmiles(m2) )
    for i in range(len(bs2)):
        nm2 = Chem.FragmentOnBonds(m2, bs2[i:i+1], dummyLabels=labels2[i:i+1])
        # print("Fragemetal mol on bond index %d with dummylabels %s: \n"%(bs2[i], labels2[i]), Chem.MolToSmiles(nm2, True) )
        rs2 = Chem.GetMolFrags(nm2, asMols=True) 
        rs2_ = list(rs2)
        m2_lista += rs2_
    
    
    
    print("delete unbroken mols.")
    m1_lista = delete_unbroken_mols(m1_lista, m1, numatom_shift=1)
    m2_lista = delete_unbroken_mols(m2_lista, m2, numatom_shift=1)
    
    
    print("delete repeated smiles of mols.")
    m1_lista = delete_repeated_smiles_of_mols(m1_lista)
    m2_lista = delete_repeated_smiles_of_mols(m2_lista)
    
    
    print('-'*30)
    print("m1_lista:")
    for mol1 in m1_lista:
        print(Chem.MolToSmiles(mol1))

    print('-'*30)
    print("m2_lista:")
    for mol2 in m2_lista:    
        print(Chem.MolToSmiles(mol2))
        
    
    #------- obtain combine_lista ----------------------
    
    combine_lista = []
    
    print("-"*30)
    for mol1 in m1_lista:
        for mol2 in m2_lista:
            print(Chem.MolToSmiles(mol1), " : " , Chem.MolToSmiles(mol2))
    
            # dummy1_index = find_label_atom_idx(mol1, atom_symbol='*')
            # dummy2_index = find_label_atom_idx(mol2, atom_symbol='*')
    
            mol2_rev = replace_dummy_by_Po_label_v1(mol2, 
                                                    original_label_symbol='*', 
                                                    final_label_symbol='Po', 
                                                    reverse=False
                                                    )
            
            # Po_index = find_label_atom_idx(mol2_rev, atom_symbol='[Po]')
    
            # print("dummy1_index = %d, dummy2_index = %d, Po_index = %d"%(dummy1_index, dummy2_index, Po_index))
            
    
            D_A_mols = D_A_Enumeration_new(ligandA_smis=[ Chem.MolToSmiles(mol1) ], 
                                           ligandB_smis=[ Chem.MolToSmiles(mol2_rev) ]
                                           )
    
    
            combine_lista += D_A_mols
    
    
    
    print('-'*30)
    print("len(combine_lista) = ", len(combine_lista) )
    
    combine_lista = delete_repeated_smiles_of_mols( combine_lista )
    print("after deleting, len(combine_lista) = ", len(combine_lista) )
    
    print("Sort list by NumAtoms.")
    combine_lista = sorted(combine_lista, 
                          key=get_numatoms, 
                          reverse=False
                          )    
    
    
    
    # combine_lista = [ m1, m2 ] + combine_lista
    # # combine_lista = delete_repeated_smiles_of_mols( combine_lista )
    # print("After adding parent 2 mols, len(combine_lista) = ", len(combine_lista) )
    

    # draw_mols(m1_lista,
    #           len(m1_lista),
    #           file_name='./foo-gridimage-mols-m1_lista-%s.png'%typestr,
    #           molsPerRow=5,
    #           size=(600, 600)
    #           )
    
    # draw_mols(m2_lista,
    #           len(m2_lista),
    #           file_name='./foo-gridimage-mols-m2_lista--%s.png'%typestr,
    #           molsPerRow=5,
    #           size=(600, 600)
    #           )
    

    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest ring sizes.")

    for mol in combine_lista:
        # print(Chem.MolToSmiles(mol))
        
        lrs = get_largest_ring_size(mol)
        srs = get_smallest_ring_size(mol)
        
        if ((srs > RS_LIMITS[0]) and (lrs < RS_LIMITS[1])):
            combine_lista_slrs.append(mol)
        # else:
        #     print("### Macrocycles or Microcycles found!")
    
    print('_'*30)
    print("len(combine_lista_slrs) = ", len(combine_lista_slrs))


    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest molecular weights.")

    SMR_LIMIT = min(Descriptors.HeavyAtomMolWt(m1), Descriptors.HeavyAtomMolWt(m2)) * (1.0 + MolWt_expansion_ratios[0])
    LMR_LIMIT = max(Descriptors.HeavyAtomMolWt(m1), Descriptors.HeavyAtomMolWt(m2)) * (1.0 + MolWt_expansion_ratios[1])
    
    for mol in combine_lista_slrs:
        
        molwt = Descriptors.HeavyAtomMolWt(mol)
        
        if ((molwt > SMR_LIMIT) and (molwt < LMR_LIMIT)):
            combine_lista_slrs_slmr.append(mol)
        # else:
        #     print("### Molecular weight is out of range!")
    
    print('_'*30)
    print("len(combine_lista_slrs_slmr) = ", len(combine_lista_slrs_slmr))


    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest number of aromatic rings.")

    SNAR_LIMIT = min(get_num_of_aromaticrings(m1), get_num_of_aromaticrings(m2)) + NAR_SHIFTS[0]
    LNAR_LIMIT = max(get_num_of_aromaticrings(m1), get_num_of_aromaticrings(m2)) + NAR_SHIFTS[1]


    for mol in combine_lista_slrs_slmr:
        # print(Chem.MolToSmiles(mol))
        nar = get_num_of_aromaticrings(mol)
        
        if ((nar >= SNAR_LIMIT) and (nar <= LNAR_LIMIT)):
            combine_lista_slrs_slmr_slnar.append(mol)
        # else:
        #     print("### num_of_aromaticrings is out of range!")
    
    print('_'*30)
    print("len(combine_lista_slrs_slmr_slnar) = ", len(combine_lista_slrs_slmr_slnar))    


    if is_shown == True:

        m1 = set_atomNotes(m1)
        m2 = set_atomNotes(m2)        
        
        Draw.ShowMol(m1, size=(600, 600), title="mol1")
        Draw.ShowMol(m2, size=(600, 600), title="mol2")
        
        # for mol,i in zip(m1_lista, range(len(m1_lista))):
        #     Draw.ShowMol(mol, 
        #                   size=(600, 600), 
        #                   title="mol1: the fragmental %d th molecule"%i
        #                   )
        
        # for mol,i in zip(m2_lista, range(len(m2_lista))):
        #     Draw.ShowMol(mol, 
        #                   size=(600, 600), 
        #                   title="mol2: the fragmental %d th molecule"%i
        #                   )
        
        for mol,i in zip(combine_lista_slrs_slmr_slnar, range(nsamplesplot)):
            Draw.ShowMol(mol, 
                          size=(600, 600), 
                          title="the combined %d th molecule"%i
                          )

    if is_draw == True:
        draw_mols(combine_lista_slrs_slmr_slnar,
                  nsamplesplot,
                  # file_name='./foo-gridimage-mols-combine_lista-R-R.png',
                  file_name='./foo-gridimage-mols-combine_lista--%s.png'%typestr,
                  # file_name='./foo-gridimage-mols-combine_lista-aR-aR.png',
                  molsPerRow=5,
                  size=(600, 600)
                  )


    print('*'*60)
    print("### Final combine_lista_slrs_slmr_slnar:")      
    for mol in combine_lista_slrs_slmr_slnar:
        print(Chem.MolToSmiles(mol))


    return combine_lista_slrs_slmr_slnar



#---------------------------------------------------------------------------
def crossover_two_mols_break_twobondsring(m1, 
                                          m2, 
                                          type2_smarts=['a1:a:a:a:a:a1'],
                                          typestr="aR6",
                                          RS_LIMITS=[4, 9],
                                          MolWt_expansion_ratios=[-0.10, 0],
                                          NAR_SHIFTS=[-1, 0],
                                          is_shown=False,
                                          nsamplesplot=30,
                                          is_draw=False
                                          ):
    
    
    #---apply limits on smallest and largest ring sizes---------------------------
    #------- the following setup corresponding to restrict the sizes of rings 
    #--------in ranges from 5 - 7. 
    # SRS_LIMIT = 4
    # LRS_LIMIT = 8
    # combine_listb_new_lrs = []
    combine_listb_new_slrs = []
    combine_listb_new_slrs_slmr = []
    combine_listb_new_slrs_slmr_slnar = []
    
    # nsamplesplot = 20
    
    
    #-------compute m1_listb_new---------------------------------------------------
    m1_listb = []
    all_ris1 = []
    
    for i in range(len(type2_smarts)):
        if len( m1.GetSubstructMatches(Chem.MolFromSmarts( type2_smarts[i] )) ) > 0:
            print("Non-empty matches exist.")
            for ele in m1.GetSubstructMatches(Chem.MolFromSmarts( type2_smarts[i] )):
                print(ele)
                all_ris1.append( ele )
    
    
    print("len(all_ris1) = ", len(all_ris1))
    print("all_ris1 = ", all_ris1 )
    
    # print("reset ris1=ris1[0]")
    # ris1 = ris1[0]
    
    # print("len(ris1) = ", len(ris1))
    # print("ris1 = ", ris1 )
    
    print("mol1 smiles: ", Chem.MolToSmiles(m1) )
    
    all_rbis1 = []
    
    for ris1 in all_ris1:
        
        rbis1 = []
    
        for i in range(len(ris1) - 1):
                b = m1.GetBondBetweenAtoms(ris1[i], ris1[i+1])
                print( b.GetIdx() )
                rbis1.append( b.GetIdx() )        
                
        b_tmp = m1.GetBondBetweenAtoms(ris1[-1], ris1[0])
        rbis1.append( b_tmp.GetIdx() )                
        
        print("len(rbis1) = ", len(rbis1))
        print("rbis1 = ", rbis1)
        
        # comb2bonds = combinations(rbis1, 2)

        all_rbis1 += rbis1
            
    
        for bs_comb2 in combinations(rbis1, 2):
            # print(bs_comb2)
            nm1 = Chem.FragmentOnBonds(m1, 
                                        bs_comb2[:], 
                                        dummyLabels=[(10000, 10000),(20000,20000)]
                                        )
            # print("Fragemetal mol on two bonds indexs: \n", bs_comb2 ) 
            # print( Chem.MolToSmiles(nm1) )
        
            
            rs1 = Chem.GetMolFrags(nm1, 
                                   asMols=True,
                                   sanitizeFrags=False
                                   )
                
            rs1_ = list(rs1)
            m1_listb += rs1_
    
    
    print("-"*30)
    print("all_rbis1 = ", all_rbis1)
    
    print("-"*30)
    print("len(m1_listb) = ", len(m1_listb) )
    
    # print("m1_listb:")
    # m1_listb_new = []
    
    # for ele in m1_listb:
    #     # print( Chem.MolToSmiles(ele) )
    #     new_smi = Chem.MolToSmiles(ele).replace(r'[10000*]', '[Po]').replace(r'[20000*]', '[Te]')
    #     # print(new_smi)
    #     m1_listb_new.append( Chem.MolFromSmiles(new_smi, sanitize=False) )
    
    
    # print("len(m1_listb) = ", len(m1_listb) )
    
    print("delete unbroken mols.")
    m1_listb = delete_unbroken_mols(m1_listb, m1, numatom_shift=3)
    
    
    m1_listb = delete_repeated_smiles_of_mols(m1_listb, is_sanitize=False)
    print("After deleting redundance, len(m1_listb) = ", len(m1_listb) )
    
    print("Sort list by NumAtoms.")
    m1_listb = sorted(m1_listb, 
                      key=get_numatoms, 
                      reverse=False
                      )
    
    
    # print("len(m1_listb_new) = ", len(m1_listb_new) )
    # m1_listb_new = delete_repeated_smiles_of_mols(m1_listb_new, is_sanitize=False)
    
    # print("After deleting redundance, len(m1_listb_new) = ", len(m1_listb_new) )
    
    # m1_listb_new = sorted(m1_listb_new, 
    #                       key=get_numatoms, 
    #                       reverse=False
    #                       )
    
    
    print('-'*30)
    print("Final m1_listb:")
    for mol,i in zip(m1_listb, range(len(m1_listb))):
        if mol is not None:
            print("mol %4d, smi = "%i,  Chem.MolToSmiles(mol) )
        else:
            print("mol %4d is None."%i)
            
    
    # print('-'*30)
    # print("m1_listb_new:")
    # for mol,i in zip(m1_listb_new, range(len(m1_listb_new))):
    #     if mol is not None:
    #         print("mol %4d, smi = "%i,  Chem.MolToSmiles(mol) )
    #     else:
    #         print("mol %4d is None."%i)
    
    
    #-------compute m2_listb_new---------------------------------------------------
    m2_listb = []
    all_ris2 = []
    
    
    for i in range(len(type2_smarts)):
        if len( m2.GetSubstructMatches(Chem.MolFromSmarts( type2_smarts[i] )) ) > 0:
            print("Non-empty matches exist.")
            for ele in m2.GetSubstructMatches(Chem.MolFromSmarts( type2_smarts[i] )):
                print(ele)
                all_ris2.append( ele )
                
    
    print("len(all_ris2) = ", len(all_ris2))
    print("all_ris2 = ", all_ris2 )
    
    # print("reset ris2=ris2[0]")
    # ris2 = ris2[0]
    
    # print("len(ris2) = ", len(ris2))
    # print("ris2 = ", ris2 )
    
    print("mol2 smiles: ", Chem.MolToSmiles(m2) )
    
    
    all_rbis2 = []
    
    for ris2 in all_ris2:
        
        rbis2 = []
    
        for i in range(len(ris2) - 1):
                b = m2.GetBondBetweenAtoms(ris2[i], ris2[i+1])
                print( b.GetIdx() )
                rbis2.append( b.GetIdx() )        
                
        b_tmp = m2.GetBondBetweenAtoms(ris2[-1], ris2[0])
        rbis2.append( b_tmp.GetIdx() )                
        
        print("len(rbis2) = ", len(rbis2))
        print("rbis2 = ", rbis2)
        
        # comb2bonds = combinations(rbis2, 2)
        
        all_rbis2 += rbis2
        
        
        for bs_comb2 in combinations(rbis2, 2):
            # print(bs_comb2)
            nm2 = Chem.FragmentOnBonds(m2, 
                                       bs_comb2[:], 
                                       dummyLabels=[(10000, 10000),(20000,20000)]
                                       )
            # print("Fragemetal mol on two bonds indexs: \n", bs_comb2 ) 
            # print( Chem.MolToSmiles(nm2) )
        
            rs2 = Chem.GetMolFrags(nm2, 
                                   asMols=True,
                                   sanitizeFrags=False)
                
            rs2_ = list(rs2)
            m2_listb += rs2_


    print("-"*30)
    print("all_rbis2 = ", all_rbis2)    
    
    print("-"*30)
    print("len(m2_listb) = ", len(m2_listb) )


    print("delete unbroken mols.")
    m2_listb = delete_unbroken_mols(m2_listb, m2, numatom_shift=3)

    
    # print("m2_listb:")
    m2_listb_new = []
    
    for ele in m2_listb:
        # print( Chem.MolToSmiles(ele) )
        new_smi = Chem.MolToSmiles(ele).replace(r'[10000*]', '[Po]').replace(r'[20000*]', '[Te]')
        # print(new_smi)
        m2_listb_new.append( Chem.MolFromSmiles(new_smi, sanitize=False) )
    
    
    
    # print("len(m2_listb) = ", len(m2_listb) )
    
    m2_listb = delete_repeated_smiles_of_mols(m2_listb, is_sanitize=False)
    print("After deleting redundance, len(m2_listb) = ", len(m2_listb) )
    
    print("Sort list by NumAtoms.")
    m2_listb = sorted(m2_listb, 
                      key=get_numatoms, 
                      reverse=False
                      )
    
    
    print("len(m2_listb_new) = ", len(m2_listb_new) )
    m2_listb_new = delete_repeated_smiles_of_mols(m2_listb_new, is_sanitize=False)
    
    print("After deleting redundance, len(m2_listb_new) = ", len(m2_listb_new) )
    
    print("Sort list by NumAtoms.")
    m2_listb_new = sorted(m2_listb_new, 
                          key=get_numatoms, 
                          reverse=False
                          )
    
    print('-'*30)
    print("Final m2_listb:")
    for mol,i in zip(m2_listb, range(len(m2_listb))):
        if mol is not None:
            print("mol %4d, smi = "%i,  Chem.MolToSmiles(mol) )
        else:
            print("mol %4d is None."%i)
    
    
    print('-'*30)
    print("Final m2_listb_new:")
    for mol,i in zip(m2_listb_new, range(len(m2_listb_new))):
        if mol is not None:
            print("mol %4d, smi = "%i,  Chem.MolToSmiles(mol) )
        else:
            print("mol %4d is None."%i)
    
    
    #------begin to reconstruct molecules-----------------------------------
    print('*'*30)
    print("Begin to reconstruct molecules.")
    
    combine_listb = []
    
    for i in range(len(m1_listb)):
        for j in range(len(m2_listb_new)):    
            testmol1 = m1_listb[i]
            testmol2 = m2_listb_new[j]
            
            print( Chem.MolToSmiles(testmol1) )
            print( Chem.MolToSmiles(testmol2) )
            
            Po_idx = find_label_atom_idx(testmol2, atom_symbol='Po')
            # print("Po_index = %d"%(Po_idx))
            
            
            ligandA_Po_ligandB = Chem.ReplaceSubstructs(testmol1, 
                                                        Chem.MolFromSmarts('[#0]'), 
                                                        testmol2, 
                                                        replacementConnectionPoint=Po_idx
                                                        )
            
            
            print( len(ligandA_Po_ligandB) )
            
            for mol in ligandA_Po_ligandB:
                print(Chem.MolToSmiles(mol))
            
            
            for k in range(len(ligandA_Po_ligandB)):
                new_mol = ligandA_Po_ligandB[k]
                
                mw = Chem.RWMol(new_mol)
                # print("#1 combined mol, ", Chem.MolToSmiles(mw)) 
                
                # Po_index = find_label_atom_idx(mw, atom_symbol='Po')
                Te_index = find_label_atom_idx(mw, atom_symbol='Te')
                # print("#1 combined mol, ", "Po_index:", Po_index)
                # print("#1 combined mol, ", "Te_index:", Te_index )
                
                mw1 = delete_label_atom(mw, 
                                        delete_atom_symbol='Po', 
                                        bondtype=Chem.BondType.AROMATIC
                                        )
                
                mw1 = Chem.RWMol(mw1)
                # print("#2 combined mol, after deleting Po, ", Chem.MolToSmiles(mw1)) 
                
                dummy_index = find_label_atom_idx(mw1, atom_symbol='*')
                Te_index = find_label_atom_idx(mw1, atom_symbol='Te')
                # print("#2 combined mol, ", "dummy_index:", dummy_index)
                # print("#2 combined mol, ", "Te_index:", Te_index )
                
                
                dummy_atom = mw1.GetAtomWithIdx(dummy_index)
                
                dummy_neighbors = dummy_atom.GetNeighbors()
                
                # print("#2 combined mol, ", "len(dummy_neighbors) = ", len(dummy_neighbors))
                # print("#2 combined mol, ", "dummy_neighbors = ", dummy_neighbors)
                
                
                mw1.AddBond(dummy_neighbors[0].GetIdx(), Te_index, Chem.BondType.AROMATIC )
                
                # print("#3 combined mol, after adding bond between dummy_neighbors[0] and Te, ", Chem.MolToSmiles(mw1))
                
                try:
                    mw2 = delete_label_atom(mw1, 
                                            delete_atom_symbol='Te', 
                                            bondtype=Chem.BondType.AROMATIC
                                            )
                
                    # print("#4 combined mol, after deleting Te, ", Chem.MolToSmiles(mw2)) 
                    
                except Exception as e1:
                    print(e1)
                    mw2 = mw1
                    # print("#4 combined mol, do not delete Te, ", Chem.MolToSmiles(mw2)) 
                    
                
                mw2 = Chem.RWMol(mw2)
                
                mw3 = delete_label_atom(mw2, 
                                        delete_atom_symbol='*',
                                        bondtype=Chem.BondType.AROMATIC
                                        )
                
                # print("#5 combined mol, after deleting *, ", Chem.MolToSmiles(mw3)) 
                
                # print("### %4d, %4d, %4d : "%(i, j, k), Chem.MolToSmiles(mw3)) 
                
                # print("\ntry SanitizeMol.")
                # try:
                #     Chem.SanitizeMol(mw3)
                # except Exception as e:
                #     print(e)
                
                if len(mw3.GetSubstructMatches( Chem.MolFromSmarts('[Te]') )) >= 1:
                    print("Te atom exist, hence do not append to the list.")   
                else:
                    combine_listb.append(mw3)
    
    
    print("len(combine_listb) = ", len(combine_listb) )
    combine_listb = delete_repeated_smiles_of_mols(combine_listb, is_sanitize=False)
    
    print("After deleting redundance, len(combine_listb) = ", len(combine_listb) )
    
    print("Sort list by NumAtoms.")
    combine_listb = sorted(combine_listb, 
                          key=get_numatoms, 
                          reverse=False
                          )
    
    print("len(combine_listb) = ", len(combine_listb))
    
    print('-'*30)
    print("The complete set of reconstructed molecules in combine_listb.")
    for mol in combine_listb:
        print(Chem.MolToSmiles(mol))
    
    
    print("Sanitize the molecules to return only kekulizable ones to a new list.")
    combine_listb_new = []
    sanitize_failed_idxs = []
    for mol,i in zip(combine_listb, range(len(combine_listb))):
        try:
            Chem.SanitizeMol(mol)
            combine_listb_new.append(mol)
    
        except Exception as e2:
            # print("### mol %4d. "%i)
            print(e2)
            sanitize_failed_idxs.append(i)
    
    
    # for i in sanitize_failed_idxs:
    #     print(i,)
    
    print("len(combine_listb_new) = ", len(combine_listb_new))

    
    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest ring sizes.")

    for mol in combine_listb_new:
        # print(Chem.MolToSmiles(mol))
        
        lrs = get_largest_ring_size(mol)
        srs = get_smallest_ring_size(mol)

        if ((srs > RS_LIMITS[0]) and (lrs < RS_LIMITS[1])):
            combine_listb_new_slrs.append(mol)
        # else:
        #     print("### Macrocycles or Microcycles found!")

    
    print('_'*30)
    print("len(combine_listb_new_slrs) = ", len(combine_listb_new_slrs))


    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest molecular weights.")

    SMR_LIMIT = min(Descriptors.HeavyAtomMolWt(m1), Descriptors.HeavyAtomMolWt(m2)) * (1.0 + MolWt_expansion_ratios[0])
    LMR_LIMIT = max(Descriptors.HeavyAtomMolWt(m1), Descriptors.HeavyAtomMolWt(m2)) * (1.0 + MolWt_expansion_ratios[1])
    
    for mol in combine_listb_new_slrs:
        
        molwt = Descriptors.HeavyAtomMolWt(mol)

        if ((molwt > SMR_LIMIT) and (molwt < LMR_LIMIT)):
            combine_listb_new_slrs_slmr.append(mol)
        # else:
        #     print("### Molecular weight is out of range!")

    
    print('_'*30)
    print("len(combine_listb_new_slrs_slmr) = ", len(combine_listb_new_slrs_slmr))


    #--------------------------------------------------------------------
    print("### Set restriction on the smallest and largest number of aromatic rings.")

    SNAR_LIMIT = min(get_num_of_aromaticrings(m1), get_num_of_aromaticrings(m2)) + NAR_SHIFTS[0]
    LNAR_LIMIT = max(get_num_of_aromaticrings(m1), get_num_of_aromaticrings(m2)) + NAR_SHIFTS[1]

    for mol in combine_listb_new_slrs_slmr:
        # print(Chem.MolToSmiles(mol))
        nar = get_num_of_aromaticrings(mol)

        if ((nar >= SNAR_LIMIT) and (nar <= LNAR_LIMIT)):
            combine_listb_new_slrs_slmr_slnar.append(mol)
        # else:
        #     print("### num_of_aromaticrings is out of range!")

    
    print('_'*30)
    print("len(combine_listb_new_slrs_slmr_slnar) = ", len(combine_listb_new_slrs_slmr_slnar)) 

    
    print("End of reconstructing molecules.")


    if is_shown == True:

        m1 = set_atomNotes(m1)
        m2 = set_atomNotes(m2)
        
        Draw.ShowMol(m1, size=(600, 600), title="mol1")
        Draw.ShowMol(m2, size=(600, 600), title="mol2")
        
        for mol,i in zip(combine_listb_new_slrs_slmr_slnar, range(nsamplesplot)):
            Draw.ShowMol(mol, 
                         size=(600, 600), 
                         title="the combined %d th molecule"%i
                         )
    
    if is_draw == True:
        draw_mols(combine_listb_new_slrs_slmr_slnar,
                  nsamplesplot,              
                  file_name='./foo-gridimage-mols-combine_listb--%s.png'%typestr,
                  molsPerRow=5,
                  size=(600, 600)
                  )


    print('*'*60)
    print("### Final combine_listb_new_slrs_slmr_slnar:")    
    for mol in combine_listb_new_slrs_slmr_slnar:
        print(Chem.MolToSmiles(mol))
    

    return combine_listb_new_slrs_slmr_slnar




#-----------------------------------------------------------------------------
def crossover_mols_parallel(parent_mols_smis='./parent-mols.smi',
                            MolWt_expansion_ratios=[-0.20, 0.20],
                            RS_LIMITS=[4, 7],
                            NAR_SHIFTS=[-1, 1],
                            type1_smarts=['[a&R]-[R]', '[a&R]-[!R]'],
                            type2_smarts=['a1:a:a:a:a:a1', 'a1:a:a:a:a1']
                            ):
    
    basemol_suppl = Chem.SmilesMolSupplier(parent_mols_smis,
                                           titleLine=False
                                           )
    
    base_mols = [x for x in basemol_suppl if x is not None]
    
    
    print("len(base_mols) = ", len(base_mols))
    
       
    Slibs = []
    Dlibs = []
    SDlibs = []


    combine_listas = Parallel(n_jobs=-1)(delayed(crossover_two_mols_break_singlebond)(m1=base_mols[i],
                                                                                      m2=base_mols[j],
                                                                                      type1_smarts=type1_smarts,
                                                                                      typestr="aR-R-or-notR",
                                                                                      RS_LIMITS=RS_LIMITS, 
                                                                                      MolWt_expansion_ratios=MolWt_expansion_ratios,
                                                                                      NAR_SHIFTS=NAR_SHIFTS,
                                                                                      is_shown=False,
                                                                                      nsamplesplot=20,
                                                                                      is_draw=False) for i in tqdm(range(len(base_mols))) for j in range(len(base_mols)))
           
           
    combine_listbs = Parallel(n_jobs=-1)(delayed(crossover_two_mols_break_twobondsring)(m1=base_mols[i], 
                                                                                        m2=base_mols[j], 
                                                                                        type2_smarts=type2_smarts,
                                                                                        typestr="aR6",
                                                                                        RS_LIMITS=RS_LIMITS, 
                                                                                        MolWt_expansion_ratios=MolWt_expansion_ratios,
                                                                                        NAR_SHIFTS=NAR_SHIFTS,
                                                                                        is_shown=False,
                                                                                        nsamplesplot=20,
                                                                                        is_draw=False) for i in tqdm(range(len(base_mols))) for j in range(len(base_mols)))
                                                                                        

    for combine_lista in combine_listas:
        Slibs += combine_lista
                
    for combine_listb in combine_listbs:
        Dlibs += combine_listb
            
    for combine_lista, combine_listb in zip(combine_listas, combine_listbs):
        SDlibs += combine_lista + combine_listb
    
    
    Slibs_rev = delete_repeated_smiles_of_mols(Slibs, is_sanitize=True)
    Dlibs_rev = delete_repeated_smiles_of_mols(Dlibs, is_sanitize=True)
    SDlibs_rev = delete_repeated_smiles_of_mols(SDlibs, is_sanitize=True)
    
    
    return Slibs_rev, Dlibs_rev, SDlibs_rev


#----------------------------------------------------------------------------
def load_csv_for_select(top_csv_path='./finaltop10-cpdname-smile-betacalc.csv'):

    df_top = pd.read_csv(top_csv_path, 
                         usecols=['smiles', 'betas']
                         )
    
    print(df_top.head())
    print(df_top.describe())

    return df_top


#----------------------------------------------------------------------------
def select_roulette(chromosomes, fitnesses, nsamples=2):
    """
    select_roulette, 
    :param chromosomes: list
    :param fitnesses: list
    :param nsamples: integer
    :return: list
    """
    total_fitnesses = np.array(fitnesses).sum()  
    fit_ratios = [i / total_fitnesses for i in fitnesses]  
    
    Chromosomes = []
    
    for i in range(nsamples):
        chromosome = np.random.choice(a=chromosomes, size=1, replace=True, p=fit_ratios)
        Chromosomes.append(chromosome[0])
    

    print('-'*30)
    for smi in Chromosomes:
        print(smi)    
    
    return Chromosomes



#---------------------------------------------------------------------------
#--- O, 8; S, 16; Se, 34 ----------------------------------------------------
#--- smarts=['[#8]@[#8]', '[#8]@[#16]', '[#16]@[#16]']
def screen_unfavored_rings(mols, 
                           smarts_list=['[#8&r6]', '[#16&r6]', '[#34&r6]']):
    
    mols_list = mols.copy()
    matched_idxs = []
    
    print("len(mols_list) = ", len(mols_list))
    
    print("Check if matched?")
    print("index : hit_at")
    
    for smarts in smarts_list:
        patt = Chem.MolFromSmarts(smarts)
        print("Chem.MolToSmiles(patt) = ", Chem.MolToSmiles(patt))
        for mol,idx  in zip(mols,range(len(mols))):
            hit_at = mol.GetSubstructMatches(patt) 
            if len(hit_at) >= 1:
                matched_idxs.append(idx)
                print(idx, " : ", hit_at)
                # for at_idx in hit_at:
                #     print(at_idx, " , ",  mol.GetAtomWithIdx(at_idx).GetSymbol() )


    matched_idxs = list(set(matched_idxs))


    mols_list_delete = [mols_list[idx] for idx in matched_idxs]


    if len(matched_idxs) > 0:
        matched_idxs_sorted = sorted(matched_idxs, 
                                     reverse=True
                                     ) 
        
        print("### Delete the following mols:")                   
        for idx1 in matched_idxs_sorted:
            print(Chem.MolToSmiles( mols_list[idx1] ))

        for idx1 in matched_idxs_sorted:
            mols_list.pop(idx1)   


    print("After deleting, len(mols_list) = ", len(mols_list))
    print("len(mols_list_delete) = ", len(mols_list_delete))
                     
    return mols_list, mols_list_delete 
