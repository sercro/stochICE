# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 11:38:01 2025

@author: cros1803


Given certain conditions (e.g. jam loc downstream)
Get the corresponidng files (same jam loc downstream) from the flowfile directory 
Copy over the geometry and result files with the same name pattern onto the destination directory

"""


import pandas as pd
import os
from pathlib import Path
import shutil
import glob


def concatenate_name(df_row):
    filename = str(df_row[0])
    for i in range(len(df_row)-1):
        value = df_row[i+1]
        filename=filename+'_'+str(value)
    return filename


# Directory names
root_dir = r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\\"

# Desired condition (pied d'embacle for now)
# pied_embacle = [48096, 48289,] # amont
# source_case_dir = '\StochICE_data_Assomption_baseline_amont\\'

# aval 
pied_embacle = [19003, 19082, 19248,] # aval
source_case_dir = '\StochICE_data_Assomption_baseline_aval\\'

destination_dir = root_dir +"copy_cases\\"+source_case_dir

# Specific directories
flowfile_dir = r"\Inputs\Individual_FlowFiles"
geofile_dir = r"\Inputs\Individual_GeoFiles"
ind_depth_dir = r"\Results\Individual_depth_tifs"
ind_prof_dir = r"\Results\Individual_WSE_profiles"
ind_wse_dir = r"\Results\Individual_wse_tifs"


# Update source directory name
source_case_dir = root_dir + source_case_dir

# Create destination directory if it does not exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

#########
# Make a list of the filename patterns that respect the condition based on the flowfiles (*.f01)
file_list = []
filename = source_case_dir+flowfile_dir

# Get a list of all the flowfiles
for p in Path(filename).iterdir():
    if p.is_file():
        file_list.append(p.name)
        
# Make a dataframe with the flowfiles
aux_list = []
for p in file_list:
    aux_list.append(p.split('_'))

# Slice the dataframe according to the desired condition
column_names = ['Q','Frontthick','ice_cover_n','phi','jam_loc_downstream','jam_loc_upstream','proc']
aux_list = pd.DataFrame(aux_list,columns=column_names)

# Transform the data into numeric
aux_list[ ['Q','Frontthick','ice_cover_n','phi','jam_loc_downstream','jam_loc_upstream'] ] = aux_list[ ['Q','Frontthick','ice_cover_n','phi','jam_loc_downstream','jam_loc_upstream']].apply(pd.to_numeric)
aux_list = aux_list[aux_list['jam_loc_downstream'].isin(pied_embacle)]

# save caselist
if not os.path.exists(destination_dir+'Logs'):
    os.makedirs(destination_dir+'Logs')
aux_list.to_csv(destination_dir+'Logs'+'\\Reduced_sim_parameters.csv')

aux_list = aux_list[['jam_loc_downstream','jam_loc_upstream','proc']]
# Create list of chosen files
file_list = [concatenate_name(filename) for filename in aux_list.values.tolist()[:]]

# Transform into pattern list
file_list = [filename.split('.f01')[0] for filename in file_list]

# copy files

folder_list = [flowfile_dir,geofile_dir,ind_depth_dir,ind_prof_dir,ind_wse_dir]

for folder in folder_list:    
    if not os.path.exists(destination_dir+folder):
        os.makedirs(destination_dir+folder)
    
    source_case_path = Path(source_case_dir+folder)
    destination_path = Path(destination_dir+folder)
    
    if not os.path.exists(destination_dir+folder):
        os.makedirs(destination_dir)
    
    for file_pattern in file_list:
        pattern = "*"+file_pattern+"*"
        for p in source_case_path.glob(pattern):
            shutil.copy2(p, destination_path)




print("\nFiltered results copied to:\n")
print(destination_dir)


