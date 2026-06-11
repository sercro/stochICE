# -*- coding: utf-8 -*-
"""
Created on Fri May  9 06:42:58 2025

@author: cros1803
"""


#%% Impot stuff
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np



#%% Read file and produce data frame
# case_directory = r"C:\Glace\StochICE_Assomption\vieux_cas\StochICE_Assomption\StochICE_data_Assomption_02_amont_lowQ\Logs"


# case_directory = r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption_Chenal_V2\StochICE_data_Assomption_Chenal_new_whole\Logs"
case_directory = r"C:\Users\cros1803\Desktop\new_StochICE_version_in_prep\case_folders\Bury\Bury_example\Bury_example\StochICE_data_Bury_beta_test\\Logs"

input_file = r"\Batch_sim_parameters.csv"

df = pd.read_csv(case_directory + input_file)

#%% Discard non-phisically high ice volumes
ice_vol_max_threshold = 1E20

for i in range(len(df['ice_vol_jam'])):
    if df['ice_vol_jam'][i] > ice_vol_max_threshold:
        df['ice_vol_jam'][i] = 0


for i in range(len(df['ice_vol_toe'])):
    if df['ice_vol_toe'][i] > ice_vol_max_threshold:
        df['ice_vol_toe'][i] = np.nan

for i in range(len(df['ice_vol_head'])):
    if df['ice_vol_head'][i] > ice_vol_max_threshold:
        df['ice_vol_head'][i] = np.nan

#%% Calculate ice-jam volume cfd
fontsize = 25

plt.figure(figsize=(12,12))
e = ECDF(df['ice_vol_jam'])
plt.step(e.x, e.y, color='blue',)
plt.xlabel('ice jam volume (m3)',fontsize=fontsize)
plt.ylabel('CDF',fontsize=fontsize)
plt.tick_params(axis='both', labelsize=fontsize)
plt.grid()
plt.show()




#%% Plot ice volume distribution

plt.figure(figsize=(12,12))
hist = df['ice_vol_jam'].hist(figsize=(12,12))
plt.grid()
plt.xlabel('ice jam volume (m3)',fontsize=fontsize)
plt.ylabel('occurrences',fontsize=fontsize)
plt.tick_params(axis='both', labelsize=fontsize)
plt.show()
# plt.savefig(case_directory + output_file)




#%% Q vs Vol 
plt.figure(figsize=(12,12))
plt.scatter(df['Frontthick'],df['ice_vol_jam'])
plt.ylabel('ice jam volume (m3)',fontsize=15)
plt.xlabel('Q',fontsize=fontsize)
plt.tick_params(axis='both', labelsize=15)
plt.show()
