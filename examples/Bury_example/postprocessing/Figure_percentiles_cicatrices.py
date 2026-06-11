"""
    Compares 75e water levels between two .csv wse files (produced with WSE_probability_envelopes.py)
    and returns a figure of the difference as a function of chainage. 
"""




import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np


# Case : baseline

# Tout
# cas_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\joint_max_results_baseline\Assomptionextra_joint_maximized.csv'
# cicats_1 = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_9Juin.csv") # millieu 
# cicats_2 = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_10Juin.csv") # aval
# cicats_3 = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_03Juillet.csv") # amont
# cicats = pd.concat([cicats_1,cicats_2,cicats_3]).reset_index(drop=True) 

# Aval
cas_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_aval\Results\New_figures\Assomption_aval.csv'
cicats = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_10Juin.csv") # aval

# Millieu
# cas_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_millieu\Results\New_figures\Assomption_Millieu.csv'
# cicats = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_9Juin.csv") # millieu 

# Amont
# cas_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_amont\Results\New_figures\Assomption_Amont.csv'
# cicats = pd.read_csv(r"C:\Glace\StochICE_Assomption\Assomption_scars_03Juillet.csv") # amont



df_wse = pd.read_csv(cas_file)

nbr_cicats = len(cicats['Height'])

percentiles =[10, 20, 25,30, 40, 50, 60, 70, 75, 80, 90, 100]

for percentil in percentiles :
    num = 'num_q'+str(percentil)
    qname = 'q'+str(percentil)

    cicats[num] = np.interp(cicats['Chainage'],df_wse['chainage'],df_wse[qname])
    cicats[qname] = [ cicats[num][i] > cicats['Height'][i] for i in range(nbr_cicats)]

cicats_values = [sum(cicats['q'+str(i)])/nbr_cicats*100 for i in percentiles]


# Figures 
line_width = 1;
lecolor = 'chocolate'
fontsize = 15
plt.rcParams.update({"font.size": fontsize})
fig, ax = plt.subplots(figsize=(4, 6))

plt.scatter(percentiles, cicats_values)
plt.plot(percentiles, cicats_values, ':k')

stars_x = [percentiles[2], percentiles[8]]
stars_y = [cicats_values[2], cicats_values[8]]

plt.scatter(stars_x, stars_y)

# general plot parameters
plt.xlim(0, 100)
plt.ylim(0, 100)

plt.xlabel("Percentil (%)", fontsize=fontsize)
plt.ylabel("%  Cicatrices dans le percentile (%)", fontsize=fontsize)


plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.tight_layout(pad=0.1)

# # Export:    
# plt.savefig(png_export_path, format="png", bbox_inches="tight")
plt.show()
# print(f"PNG exporté à : {png_export_path}")