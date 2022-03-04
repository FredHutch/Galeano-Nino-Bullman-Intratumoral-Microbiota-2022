#!/usr/bin/env python3
# this script is to turn on additional spots that contain pathogen UMI
import pandas as pd
import os 
import sys
from shutil import copyfile
from os.path import exists
def read_medatada_cells(raw_matrix_validate_csv):
    raw_matrix_validate = pd.read_csv(raw_matrix_validate_csv,header = 0,sep = ',',index_col='barcode')
    #barcode = raw_matrix_validate.lic[:,['barcode']]
    barcode = list(raw_matrix_validate.index)
    return barcode

def read_position_matrix(barcodes, position_matrix_file,position_matrix_backup_file):
    # first, back-up the position matrix! before copy the file, check if the back-up file already exists, if exists donb't copy!remember to do the test before real run
    # check existance
    if exists(position_matrix_backup_file):
        copyfile(position_matrix_backup_file, position_matrix_file)
    # copy file
    copyfile(position_matrix_file, position_matrix_backup_file)
    position_matrix = pd.read_csv(position_matrix_file,header=None,index_col=0)#,index_col='barcode')
    #print(position_matrix.head() )
    for each_barcode in barcodes:
        if each_barcode in position_matrix.index:
            position_matrix.loc[each_barcode,1] = 1 
            #print(position_matrix.loc[[each_barcode]])
    position_matrix.to_csv(position_matrix_file,index=True,header=False)
    return

if __name__ == "__main__":
    samples_folder = argv[1] # SpaceRanger output directory, where each folder is a sample
    processed_foler = argv[2] # Directory containing all pathogen UMI matrix csvs for each Visium sample 
    folder_list = os.listdir(samples_folder)
    for folder in folder_list:
        if folder.startswith('V'):
            sample_name = folder
            print(sample_name)
            metadata_file = processed_foler+'/'+sample_name+'.visium.raw_matrix.genus.csv'
            position_matrix_file = samples_folder+'/'+sample_name+'/outs/spatial/tissue_positions_list.csv'
            position_matrix_backup_file = samples_folder+'/'+sample_name+'/outs/spatial/tissue_positions_list_backup.csv'
            barcodes = read_medatada_cells(metadata_file)
            read_position_matrix(barcodes, position_matrix_file,position_matrix_backup_file)

