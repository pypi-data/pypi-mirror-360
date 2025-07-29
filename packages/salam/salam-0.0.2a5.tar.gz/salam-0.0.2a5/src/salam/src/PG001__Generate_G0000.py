#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:53:00 2021

Using scikit-learn with RDKit

@author: tucy
"""

from salam.module_MD.D_Pi_A_Enumeration import D_A_Enumeration_new
from salam.module_MD.D_Pi_A_Enumeration import draw_mols

from rdkit import Chem
from rdkit.Chem import AllChem

from tqdm import tqdm
from salam.module_MD.D_Pi_A_Enumeration import try_embedmolecule



#--------------------------------------------------------------------------
def print_numAtoms_of_fragments(frags_suppl, frags_suppl_name='frags'):
    print("-"*60)    
    print("length of %s is : " % (frags_suppl_name), len(frags_suppl))
    i = 0
    for mol in frags_suppl:
        i += 1
        if mol is None: continue
        print("NumAtoms of frag %d is: " %(i) , mol.GetNumAtoms())


#--------------------------------------------------------------------------
#----- reading smiles of Donors, Acceptors from smi files -----------------

donor_suppl = Chem.SmilesMolSupplier('./data/Donor_smiles.smi')
#print_numAtoms_of_fragments(donor_suppl, "donor_suppl")
donor_mols = [x for x in donor_suppl if x is not None]
print("length of donor_mols is : ", len(donor_mols))

acceptor_suppl = Chem.SmilesMolSupplier('./data/Acceptor_smiles.smi')
#print_numAtoms_of_fragments(acceptor_suppl, "acceptor_suppl")
acceptor_mols = [x for x in acceptor_suppl if x is not None]
print("length of acceptor_mols is : ", len(acceptor_mols))


#----------------------------------------------------------------------------
#---- write molecules to SD File ------------------------------- 
donor_w = Chem.SDWriter('data/Donor_mols.sdf')
for m in donor_mols: 
    m_temp = Chem.AddHs(m)
    AllChem.EmbedMolecule(m_temp, randomSeed=38)
    donor_w.write(m_temp)

#---- write molecules to SD File ------------------------------- 
acceptor_w = Chem.SDWriter('data/Acceptor_mols.sdf')
for m in acceptor_mols: 
    m_temp = Chem.AddHs(m)
    AllChem.EmbedMolecule(m_temp, randomSeed=38)
    acceptor_w.write(m_temp)



# =============================================================================
# draw_mols(donor_mols, len(donor_mols), './images/foo001--donor-mols-preexperiment.png', molsPerRow=4, size=(800, 800))
# draw_mols(acceptor_mols, len(acceptor_mols), './images/foo001--acceptor-mols-preexperiment.png', molsPerRow=4, size=(800, 800))


#-----------------------------------------------------------------------------
#---- create combinational compound library --------------------------
#---- via calling D_A_Enumeration_new() or D_Pi_A_Enumeration_new()
ligandA_smis = [Chem.MolToSmiles(mol)  for mol in donor_mols]
ligandB_smis = [Chem.MolToSmiles(mol)  for mol in acceptor_mols] 


DA_mols = D_A_Enumeration_new(ligandA_smis, 
                              ligandB_smis, 
                              verbse=False)


All_mols = DA_mols


draw_mols(DA_mols, 9, './images/foo001--DA-mols-preexperiment.png', molsPerRow=3, size=(800, 800))


print("length of DA_mols is : ", len(DA_mols))
print("length of All_mols = DA_mols + DPiA_mols is : ", len(All_mols))



# #---- write molecules to SD File ------------------------------- 
# DA_mols_w = Chem.SDWriter('data/Donor_Acceptor_mols.sdf')
# for m in tqdm(DA_mols): 
#     m_temp = Chem.AddHs(m)
#     m1_temp, nb_try_EmbedMolecule = try_embedmolecule(m_temp)
#     DA_mols_w.write(m1_temp)
    

All_mols = All_mols[:1000] 

cpd_names = [ "cpd-%05d" % (i+1) for i in range(len(All_mols)) ]
for mol, cpd_name in zip(All_mols, cpd_names):
    mol.SetProp("_Name", cpd_name )


#---- write molecules to SD File ------------------------------- 
outfile_path = './project/G0000/G0000.sdf'
All_mols_w = Chem.SDWriter(outfile_path)
for m in tqdm(All_mols): 
    m_temp = Chem.AddHs(m)
    m1_temp, nb_try_EmbedMolecule = try_embedmolecule(m_temp)
    All_mols_w.write(m1_temp)



print("\nEnd of program PG001!\n")

