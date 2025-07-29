#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:06:20 2021

@author: tucy
"""

import argparse

parser = argparse.ArgumentParser(description="manual to this script:")
parser.add_argument('--analyzed_property', type=str, default="tadf")
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


print("analyzed_property: ", args.analyzed_property, type(args.analyzed_property) )
analyzed_property = args.analyzed_property


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
#import tensorflow as tf

import deepchem as dc
import numpy as np
import pandas as pd
#import tempfile
from sklearn.ensemble import RandomForestRegressor

from rdkit import Chem
#from rdkit.Chem import Draw, AllChem
#from rdkit.Chem import rdDepictor

from sklearn.model_selection import GridSearchCV
#from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

#pd.set_option('display.max_columns', 100)
#pd.set_option('max_colwidth', 400)

from sklearn.impute import SimpleImputer

import subprocess


#------------------------------------------------------------------------------
def display_scores(scores):
    print("Scores:", scores)
    print("Mean:", scores.mean())
    print("Standard deviation:", scores.std())


def load_mols_in_sdf(sdf_path='./data/Pick_mols.sdf'):
    #-------- loading  sdf file ---------------------------------------------------
    sdsuppl = Chem.SDMolSupplier(sdf_path)
    mols = [x for x in sdsuppl if x is not None]
    smiles = [Chem.MolToSmiles(mol) for mol in mols]
    print("-"*60)  
    print( "number of molecules is ", len(mols) )
    
    return mols, smiles


def impute_dataset(X, strategy="median"):
    imputer = SimpleImputer(strategy=strategy)
    imputer.fit(X)
    X_imputed = imputer.transform(X)
    print("type(X_imputed) is ", type(X_imputed))
    
    return X_imputed 


def load_nlo_csv_creat_properties_list(filename='./data/nlo-summary.csv'):
    #---load properties summary file-----------------------------------------------
    df_props = pd.read_csv(filename)
    
    df_props["beta_x"]  = (df_props["bxxx"]  +  df_props["bxyy"] + df_props["bxzz"] )
    df_props["beta_y"]  = (df_props["bxxy"]  +  df_props["byyy"] + df_props["byzz"] )
    df_props["beta_z"]  = (df_props["bxxz"]  +  df_props["byyz"] + df_props["bzzz"] )
    df_props["beta_total"]  = np.sqrt(df_props["beta_x"]**2 + df_props["beta_y"]**2 + df_props["beta_z"]**2)
    
    properties = df_props["beta_total"].tolist()

    print("-"*60) 
    print("properties set is")
    print(properties)
    
    print("-"*60) 
    print( "df_props.beta_total.describe()" )
    print( df_props["beta_total"].describe() )
    
    return properties


def load_tadf_csv_creat_properties_list(filename='./data/tadf-summary.csv'):
    #---load properties summary file-----------------------------------------------
    df_props = pd.read_csv(filename)
    print(df_props.head())
    df_props_num = df_props.drop("compound", axis=1)
    print(df_props_num.head())
    imputer = SimpleImputer(strategy="median")
    imputer.fit(df_props_num)
    props_imputed = imputer.transform(df_props_num)
    print("type(props_imputed) is ", type(props_imputed))
    
    column_names = ["T1_en", "S1_en", "S1_freq", "T2_en", "S2_en", "S2_freq",\
                    "T3_en","S3_en","S3_freq",\
                        # "T4_en","S4_en","S4_freq",\
                        # "T5_en","S5_en","S5_freq","T6_en","S6_en","S6_freq",\
                        #     "T7_en","S7_en","S7_freq","T8_en","S8_en","S8_freq",\
                        #     "T9_en","S9_en","S9_freq","T10_en","S10_en","S10_freq"
                    ]
    
    df_props_imputed = pd.DataFrame(data=props_imputed, columns=column_names)
    
    df_props_imputed["deltaEST"]  = df_props_imputed["S1_en"]  -  df_props_imputed["T1_en"] 
    
    properties = df_props_imputed["deltaEST"].tolist()

    print("-"*60) 
    print("properties set is")
    print(properties)
    
    print("-"*60) 
    print( "df_props_imputed.deltaEST.describe()" )
    print( df_props_imputed["deltaEST"].describe() )
    
    return properties


def load_tpa_csv_creat_properties_list(filename='./data/tpa-summary.csv'):
    #---load properties summary file-----------------------------------------------
    df_props = pd.read_csv(filename)
    print(df_props.head())
    df_props_num = df_props.drop("compound", axis=1)
    print(df_props_num.head())
    imputer = SimpleImputer(strategy="median")
    imputer.fit(df_props_num)
    props_imputed = imputer.transform(df_props_num)
    print("type(props_imputed) is ", type(props_imputed))
    
    column_names = ["1_En", "1_lsigma", "1_csigma", "2_En", "2_lsigma", "2_csigma",\
                    "3_En", "3_lsigma", "3_csigma", "4_En", "4_lsigma", "4_csigma",\
                        "5_En", "5_lsigma", "5_csigma", "6_En", "6_lsigma", "6_csigma"]
    
    df_props_imputed = pd.DataFrame(data=props_imputed, columns=column_names)
    
    properties = df_props_imputed["1_lsigma"].tolist()

    print("-"*60) 
    print("properties set is")
    print(properties)
    
    print("-"*60) 
    print( "df_props_imputed.1_lsigma.describe()" )
    print( df_props_imputed["1_lsigma"].describe() )
    
    return properties


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
    
    #------- WeaveFeaturizer and MolGraphConvFeaturizer
    
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


def creat_smiles_properties_csv_file(smiles, properties, file_path='./data/smiles_properties.csv'):
    #----------- CSV DataLoader ---------------------------------------------------
    # make a dataframe object for creating a CSV file
    df = pd.DataFrame(list(zip(smiles, properties)), columns=["SMILES", "property"])
    print(df)
    tmp_path = file_path
    with open(tmp_path, 'w') as tmp:
        df.to_csv(tmp)



def gridsearchcv_evaluate_model(dataset, model_path=None, verbs=False):
    print("len(dataset) is ", len(dataset) )
    
    X_train, y_train = dataset.X, dataset.y
    
    param_grid = [
        {'n_estimators': [3, 10, 30, 100], 
         'criterion': ["mse", "mae"],
         'max_depth': [2, 5, 10, 50],
         'max_features': ["auto", "sqrt", "log2"]},
        {'bootstrap': [False], 
         'n_estimators': [3, 10, 30, 100], 
         'criterion': ["mse", "mae"],
         'max_depth': [2, 5, 10, 50],
         'max_features': ["auto", "sqrt", "log2"]},
    ]
    
    forest_reg = RandomForestRegressor(random_state=0)
    
    grid_search = GridSearchCV(forest_reg, 
                               param_grid, 
                               cv=5,
                               scoring='neg_mean_squared_error',
                               return_train_score=True,
                               n_jobs=-1,
                               )
    
    grid_search.fit(X_train, y_train)
    
    if verbs == True:
        print('-'*60)
        cvres = grid_search.cv_results_
        for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
            print(np.sqrt(-mean_score), params)
    
    print('-'*60)
    print("grid_search.best_params_ is: \n", grid_search.best_params_)
    print("grid_search.best_estimator_ is: \n", grid_search.best_estimator_)
    
    best_rgr = grid_search.best_estimator_
    
    best_rgr.fit(X_train, y_train)
    
    
    scores = cross_val_score(best_rgr, 
                             X_train, 
                             y_train,
                             scoring="neg_mean_squared_error", 
                             cv=5)
    tree_rmse_scores = np.sqrt(-scores)
    
    print('-'*60)
    display_scores(tree_rmse_scores)
    
    if model_path is not None:
        joblib.dump(best_rgr, model_path)
    #joblib.dump(best_rgr, "./models/best_rgr.pkl")
    

def pca_decomposition_visualize(dataset, figname1=None, xlims=None, ylims=None):
    #-------PCA for visualization -------------------------------------------------
    X = dataset.X.copy()
    y = dataset.y.copy()
    pca = PCA(n_components=2, svd_solver='auto')
    X_pca = pca.fit_transform(X)
    
    mm_scaler = MinMaxScaler()
    X_pca_scaled = mm_scaler.fit_transform(X_pca)
    
    print('-'*60)
    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)
    print(X.shape)
    print(X_pca.shape)
    
    
    df_pca = pd.DataFrame(data=X_pca_scaled, columns=["1st-component", "2nd-component"])
    df_pca["property"] = y
    
    ax1 = df_pca.plot(kind="scatter", 
                x="1st-component", 
                y="2nd-component", 
                alpha=0.4,
                #label="prop", 
                figsize=(10,6),
                c="property", 
                cmap=plt.get_cmap("jet"), 
                colorbar=True,
    )
    #plt.legend()
    
    if xlims is not None:
        left, right = xlims
        plt.xlim(left, right)
        ax1.set_xticks([left, right])
    
    if ylims is not None:
        bottom, top = ylims
        plt.ylim(bottom, top)    
        ax1.set_yticks([bottom, top])
    
    plt.xlabel('1st-component')
    plt.ylabel('2nd-component')
    
    fig1 = ax1.get_figure() 
    
    fig1.savefig(figname1)
    
    #plt.show()
    #plt.pause(10)
    plt.close('all')
    



#----MAIN Function begins -----------------------------------------------------
#------------------------------------------------------------------------------

#mols, smiles = load_mols_in_sdf(sdf_path='./data/Pick_mols.sdf')

GXXXX_PXXXXrev_sdf_path = './project/'  +  GXXXX  + '/'    +  PXXXX   +  'rev.sdf'
mols, smiles = load_mols_in_sdf(sdf_path=GXXXX_PXXXXrev_sdf_path) 

#properties = load_nlo_csv_creat_properties_list(filename='./data/nlo-summary.csv')
#properties = load_tadf_csv_creat_properties_list(filename='./data/tadf-summary.csv')

if (analyzed_property == "tadf") or (analyzed_property == "TADF"):

    GXXXX_tadf_summary_PXXXXrev_csv_path = './project/'   +  GXXXX  + '/tadf_summary_'  +  PXXXX  +  '.csv'
    properties = load_tadf_csv_creat_properties_list(filename=GXXXX_tadf_summary_PXXXXrev_csv_path)

elif (analyzed_property == "nlo") or (analyzed_property == "NLO"):
    
    GXXXX_nlo_summary_PXXXXrev_csv_path = './project/'   +  GXXXX  + '/nlo_summary_'  +  PXXXX  +  '.csv'
    properties = load_nlo_csv_creat_properties_list(filename=GXXXX_nlo_summary_PXXXXrev_csv_path)

else:
    print("undefined property.")
    print("analyzed_property: tadf [TADF] or nlo [NLO] ")
    exit(1)



#dataset, dataset1, dataset2 =  creat_ECFP_RDKITDES_CM_features_dataset(mols, smiles, properties)
dataset, dataset1 =  creat_ECFP_RDKITDES_CM_features_dataset(mols, 
                                                             smiles, 
                                                             properties, 
                                                             is_compute_CM=False
                                                             )

X_imputed = impute_dataset(dataset.X, strategy="median")
X1_imputed = impute_dataset(dataset1.X, strategy="median")
# X2_imputed = impute_dataset(dataset2.X, strategy="median")

dataset_imputed = dc.data.NumpyDataset(X=X_imputed, y=np.array(properties)) 
dataset1_imputed = dc.data.NumpyDataset(X=X1_imputed, y=np.array(properties)) 
# dataset2_imputed = dc.data.NumpyDataset(X=X2_imputed, y=np.array(properties)) 

creat_smiles_properties_csv_file(smiles, 
                                 properties,
                                 file_path='./project/%s/smiles_properties_%s.csv'%(GXXXX, PXXXX)
                                 )

call_mkdir_GXXXX_models_dir = 'mkdir  ./project/'  +  GXXXX  +  '/models/  2>/dev/null '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXX_models_dir )
print("mkdir  ./project/%s/models/.  status, output = "%(GXXXX), status, output)

call_mkdir_GXXXX_models_ECFP_dir = 'mkdir  ./project/'  +  GXXXX  +  '/models/ECFP/  2>/dev/null '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXX_models_ECFP_dir )
print("mkdir  ./project/%s/models/ECFP/.  status, output = "%(GXXXX), status, output)

call_mkdir_GXXXX_models_RDKIT_DES_dir = 'mkdir  ./project/'  +  GXXXX  +  '/models/RDKIT_DES/  2>/dev/null '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXX_models_RDKIT_DES_dir )
print("mkdir  ./project/%s/models/RDKIT_DES/.  status, output = "%(GXXXX), status, output)

# status, output = subprocess.getstatusoutput('mkdir  ./project/G0000/models/CM/  2>/dev/null ')
# print("mkdir  ./project/G0000/models/CM/.  status, output = ", status, output)


#------------------------------------------------------------------------------
print("The ML models are stored at: " + "./project/"  +  GXXXX + "/models/" + "\n" )
print("ECFP model", "-"*60) 
rf_reg_ECFP = gridsearchcv_evaluate_model(dataset, 
                                          model_path='./project/%s/models/ECFP/rf_reg_model_ECFP.pkl'%GXXXX
                                          )


print("RDKIT_DES model", "-"*60) 
rf_reg_RDKIT_DES = gridsearchcv_evaluate_model(dataset1_imputed, 
                                                model_path='./project/%s/models/RDKIT_DES/rf_reg_model_RDKIT_DES.pkl'%GXXXX
                                                )


# print("CM model", "-"*60) 
# rf_reg_CM = gridsearchcv_evaluate_model(dataset2, 
#                                         model_path='./project/G0000/models/CM/rf_reg_model_CM.pkl'
#                                         )

#------------------------------------------------------------------------------

call_mkdir_GXXXX_images_dir = 'mkdir  ./project/'  +  GXXXX   + '/images/  2>/dev/null '
status, output = subprocess.getstatusoutput( call_mkdir_GXXXX_images_dir )
print("mkdir  ./project/%s/images/.  status, output = "%GXXXX, status, output)

print("The PCA decomposition of X vector vs property is stored at: ")
print( "./project/%s/images/"%GXXXX )

fignamea = './project/%s/images/foo-props-pca-ECFP-1.png'%GXXXX
print("save figure\n %s \n" %(fignamea))
pca_decomposition_visualize(dataset, figname1=fignamea)


fignameb = './project/%s/images/foo-props-pca-RDKITDES-1.png'%GXXXX
print("save figure\n %s \n" %(fignameb))
pca_decomposition_visualize(dataset1_imputed, figname1=fignameb)


# fignamec = './project/G0000/images/foo-props-pca-CM-1.png'
# print("save figure\n %s \n" %(fignamec))
# pca_decomposition_visualize(dataset2, 
#                             figname1=fignamec, 
#                             #xlims=(0.0, 0.10), 
#                             #ylims=(0.0, 0.05),
#                             )


print("\n### End of program: PG010!\n")
