# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 16:12:50 2025

@author: cros1803
"""


import pandas as pd
import os



# Compare amont
# case_aval = r"C:\Glace\StochICE_Assomption\StochICE_Assomption\StochICE_data_Assomption_02_aval_lowQ"
# case_milieu = r"C:\Glace\StochICE_Assomption\StochICE_Assomption\StochICE_data_Assomption_02_millieu_lowQ"
# case_amont = r"C:\Glace\StochICE_Assomption\StochICE_Assomption\StochICE_data_Assomption_02_amont_lowQ"




# case_org = case_aval
# case_drg = case_amont



# df_org = pd.read_csv(os.path.join(case_org,"Logs\\Batch_sim_parameters.csv"))
# df_drg = pd.read_csv(os.path.join(case_drg,"Logs\\Batch_sim_parameters.csv"))

df_org = pd.read_csv(r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_amont\Logs\Batch_sim_parameters.csv')
df_drg = pd.read_csv(r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_millieu\Logs\Batch_sim_parameters.csv')



print('Checking if corresponding columns in both seed parameter files are equal: ')
for column in df_org.keys():
    diff = (df_org[column]==df_drg[column]).any()
    text = 'For ' + column + ': '+ str(diff)
    print(text)