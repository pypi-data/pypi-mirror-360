#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 21:50:49 2021

@author: tucy
"""

import sys 
import os
#os.chdir('../')
script_wkdir = os.getcwd()
sys.path.append(script_wkdir)


import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--prop_tendency', type=str, default="small")
parser.add_argument('--GXXXX', type=str, default="G0000")
parser.add_argument('--PXXXX', type=str, default="P0000")
parser.add_argument('--OXXXX', type=str, default="O0000")

args = parser.parse_args()
print(args.GXXXX, type(args.GXXXX))
print(args.PXXXX, type(args.PXXXX))
print(args.OXXXX, type(args.OXXXX))
GXXXX = args.GXXXX
PXXXX = args.PXXXX
OXXXX = args.OXXXX

print(args.prop_tendency, type(args.prop_tendency))
prop_tendency = args.prop_tendency


#import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#import tensorflow as tf

import deepchem as dc
import numpy as np
import pandas as pd
#import tempfile
#from sklearn.ensemble import RandomForestRegressor
from rdkit import Chem
#from rdkit.Chem import Draw, AllChem
#from rdkit.Chem import rdDepictor
from salam.module_MD.D_Pi_A_Enumeration import draw_mols
import joblib
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import subprocess


#----------------------------------------------------------------------------------
def load_sdf_to_df(sdf_path='./data/All_mols.sdf'):
    #-------- loading  sdf file ---------------------------------------------------
    sdsuppl = Chem.SDMolSupplier(sdf_path)
    #sdsuppl = Chem.SDMolSupplier('./data/Prod_mols.sdf')
    
    mols = [x for x in sdsuppl if x is not None]
    smiles = [Chem.MolToSmiles(mol) for mol in mols]
    compoundnames = [mol.GetProp("_Name") for mol in mols]
    properties = [np.nan for i in range(len(mols))]
    print("-"*60)  
    print( "len(mols) is ", len(mols) ) 
    print("len(properties) is ", len(properties))
    
    df_mols = pd.DataFrame(data=zip(mols, smiles, compoundnames), columns=["mols", "smiles", "compoundnames"])
    
    df_mols.set_index("compoundnames", inplace=True)
    
    print(df_mols.head())
    
    return mols, smiles, compoundnames, properties, df_mols


def impute_dataset(X, strategy="median"):
    imputer = SimpleImputer(strategy=strategy)
    imputer.fit(X)
    X_imputed = imputer.transform(X)
    print("type(X_imputed) is ", type(X_imputed))
    
    return X_imputed 


def creat_ECFP_RDKITDES_CM_features_dataset(mols, smiles, properties, is_compute_CM=True):   
    #--------- ECFP ---------------------------------------------------
    featurizer = dc.feat.CircularFingerprint(size=2048)
    ecfp = featurizer.featurize(smiles)
    dataset = dc.data.NumpyDataset(X=ecfp, y=np.array(properties))
    print("ecfp.shape is ", ecfp.shape )
    print("len(dataset) is ", len(dataset) ) 
    
    #-------------------------------------------------------------------
    #------- RDKitDescriptors ------------------------------------------
    rdkit_featurizer = dc.feat.RDKitDescriptors()
    rdkit_des_features = rdkit_featurizer(smiles)
    dataset1 = dc.data.NumpyDataset(X=rdkit_des_features, y=np.array(properties))
    print("len(dataset1) is ", len(dataset1) ) 
    
    print("-"*60) 
    print("RDKit Descriptors and values for a compound.") 
    for feature, descriptor in zip(rdkit_des_features[0][:], rdkit_featurizer.descriptors):
        print(descriptor, feature)
    
    print('The number of sample present is: ', len(rdkit_des_features))
    print('The number of descriptors present is: ', len(rdkit_des_features[0]))
    
    print("rdkit_des_features.shape is ", rdkit_des_features.shape)
    
    #------------------------------------------------------------------------------
    #------- CoulombMatrix --------------------------------------------------------
    if (is_compute_CM == True):
        coulomb_mat = dc.feat.CoulombMatrix(max_atoms=100)
        coulomb_mat_features = coulomb_mat(mols)
        
        print("type(coulomb_mat_features) ", type(coulomb_mat_features))
        print("coulomb_mat_features.shape is ", coulomb_mat_features.shape)
        
        coulomb_mat_features = coulomb_mat_features.reshape(coulomb_mat_features.shape[0],
                                                            coulomb_mat_features.shape[1]*coulomb_mat_features.shape[2])
        
        print("coulomb_mat_features.shape is ", coulomb_mat_features.shape)
        
        dataset2 = dc.data.NumpyDataset(X=coulomb_mat_features, y=np.array(properties))
        print("len(dataset2) is ", len(dataset2) ) 
        
        return  dataset, dataset1, dataset2
    else:
        return  dataset, dataset1


#------ load and predict ------------------------------------------
def load_and_predict(df, dataset, model_path=None, ascending=False):

    if model_path is not None:
        model_loaded = joblib.load(model_path)
    else:
        print("loading model %s failed!" % model_path)
        exit(-1)

    # model evaluate on  all molecules. 
    prop_preds = model_loaded.predict(dataset.X)
    print( "len(prop_preds) is ", len(prop_preds) )
    
    df["prop_preds"] = prop_preds
    
    df.sort_values(by="prop_preds", ascending=ascending, inplace=True)

    print('# The optimal 16 molecules are: ')
    print( df.head(16) )
    
    return df


def draw_optimal_mols(df, imgname='./images/foo009-optimal-mols.png', unit=' a.u. '):
    opt_mols = df["mols"].tolist()[:16]
    props_values = df["prop_preds"].tolist()[:16] 
    props_as_legends = [" " + str(round(number, 3)) + unit for number in props_values]
    
    draw_mols(opt_mols, 
              16, 
              imgname, 
              molsPerRow=4, 
              size=(800, 800),
              legends=props_as_legends,
              )


def plot_prop_pred(df, figname='./images/foo009-property-statistics.png', xlabel_name='Energy gap'):
    ax1 = df['prop_preds'].plot(title='Distribution of property',
                                  kind='hist',
                                )
    
    plt.xlabel(xlabel_name)
    #plt.ylabel('Frequency')
    
    fig1 = ax1.get_figure() 
    fig1.savefig(figname)
    #plt.show()
    #plt.pause(10)
    plt.close()



#---main function begins --------------------------------------------------------
#--------------------------------------------------------------------------------

print("-"*60) 
GXXXX_sdf_path = './project/'  +  GXXXX    +  '/'  + GXXXX  +  '.sdf'
print("Loading sdf for ML prediction, the path is:\n", GXXXX_sdf_path)

mols, smiles, compoundnames, properties, df_mols = load_sdf_to_df(sdf_path=GXXXX_sdf_path )

dataset, dataset1 = creat_ECFP_RDKITDES_CM_features_dataset(mols, 
                                                            smiles, 
                                                            properties, 
                                                            is_compute_CM=False
                                                            )

print("The ECFP model is loaded for prediction of whole mols.")

X_imputed = impute_dataset(dataset.X, strategy="median")
dataset_imputed = dc.data.NumpyDataset(X=X_imputed, y=np.array(properties)) 

if (prop_tendency == "small"):
    df_ECFP = load_and_predict(df_mols, 
                               dataset_imputed, 
                               model_path='./project/%s/models/ECFP/rf_reg_model_ECFP.pkl'%GXXXX, 
                               ascending=True
                               )
elif (prop_tendency == "large"):
    df_ECFP = load_and_predict(df_mols, 
                               dataset_imputed, 
                               model_path='./project/%s/models/ECFP/rf_reg_model_ECFP.pkl'%GXXXX, 
                               ascending=False
                               )
else:
    print("prop_tendency: small or large.")    
    exit(1)


print("The optimal mols is shown in fig: \n", './project/%s/images/foo-ECFP-optimal-mols-in-all-mols.png'%GXXXX )
draw_optimal_mols(df_ECFP, 
                  imgname='./project/%s/images/foo-ECFP-optimal-mols-in-all-mols.png'%GXXXX, 
                  unit=' eV '
                  )

print("The property statistics is shown in fig: \n", './project/%s/images/foo-property-statistics-in-all-mols.png'%GXXXX )
plot_prop_pred(df_ECFP, 
               figname='./project/%s/images/foo-property-statistics-in-all-mols.png'%GXXXX, 
               xlabel_name='Energy gap'
               )


#---- write df_ECFP to csv-----------------------------------------------------
print('-'*60)
print(df_ECFP.head() )
GXXXX_df_ECFP_csv_path = './project/'  +  GXXXX    +  '/'  + GXXXX   +  '_df_ECFP.csv'
call_rm_GXXXX_df_ECFP_csv_file =  'rm -f  '  +  GXXXX_df_ECFP_csv_path  +  '   2>/dev/null  '
status, output = subprocess.getstatusoutput( call_rm_GXXXX_df_ECFP_csv_file )
print("rm -f  %s.    status, output = "%GXXXX_df_ECFP_csv_path,  status, output)
print("df_ECFP is stored at %s\n"%GXXXX_df_ECFP_csv_path )

with open(GXXXX_df_ECFP_csv_path, 'w') as tmp:
    df_ECFP.to_csv(tmp)
#-----------------------------------------------------------------------------


optimal_cpdnames = df_ECFP.index.tolist()[0:100]
print("-"*60)
print("The optimal_cpdname are:")
for cpdname in optimal_cpdnames:
    print(cpdname)



print('-'*60)
src_file_path = './project/%s/separate_mols/'%GXXXX
print("\nThe optimal_cpds is stored at ./project/%s/%s.sdf"%(GXXXX, OXXXX) )

call_rm_GXXXX_OXXXX_sdf_file =  'rm -f  ./project/'  +  GXXXX  +  '/'   +  OXXXX  +  '.sdf 2>/dev/null  '
status, output = subprocess.getstatusoutput( call_rm_GXXXX_OXXXX_sdf_file )
print("rm -f  ./project/%s/%s.sdf.    status, output = "%(GXXXX, OXXXX), status, output)

for normal_name in optimal_cpdnames:
    #print(normal_name)
    normal_sdf_file_name = src_file_path + normal_name + ".sdf"
    cat_file_to_Pickmols = "cat  "  +  normal_sdf_file_name   +  "   >>  "  +  "./project/"  +  GXXXX  + "/"  +  OXXXX  +  ".sdf"
    status, output = subprocess.getstatusoutput( cat_file_to_Pickmols )
    #print("status, output = ", status, output)



print("\n### End of program: PG011!\n")
