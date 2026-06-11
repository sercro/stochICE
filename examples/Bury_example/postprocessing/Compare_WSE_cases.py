"""
    Compares 75e water levels between two .csv wse files (produced with WSE_probability_envelopes.py)
    and produces a figure showing the differences along the talweg. 
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# Case 1 : baseline
cas1_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\joint_max_results_baseline\Assomptionextra_joint_maximized.csv'
cas1_ds = pd.read_csv(cas1_file)

# Case 2 : chenal
cas2_file = r'C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption_Chenal_V2\StochICE_data_Assomption_Chenal_whole_manning_n\Results\New_figures\Assomption_chenal.csv'
cas2_ds = pd.read_csv(cas2_file)

# Where to export the resulting figure
png_export_path = r'C:\Glace\StochICE_Assomption\QGis\Assomption_chenal_WSE.png'

# Bed path
bed_profile_path = (r"C:\Glace\StochICE_Assomption\Assomption_channel_profile.csv") 

# Produce rectangles for inline structures
rectangles_data = [  # Données des rectangles : chaînage, haut, bas (m)
    {"chainage": 59512, "top": 96.44, "bottom": 88.26},
    {"chainage": 37435, "top": 82.08, "bottom": 65.68},
    {"chainage": 15468, "top": 59.73, "bottom": 52.68},
    {"chainage": 12500, "top": 61.07, "bottom": 49.99},
    {"chainage": 11395, "top": 60.24, "bottom": 50.13},
    {"chainage": 11253, "top": 59.29, "bottom": 49.04},
    {"chainage": 9785, "top": 57.65, "bottom": 49.22},
    {"chainage": 9223, "top": 52.18, "bottom": 40.63},    
    {"chainage": 7895, "top": 52.06, "bottom": 39.86},
    {"chainage": 6840, "top": 42.36, "bottom": 29.55},
]

seuils_data = [
    {"chainage": 10013, "top": 54.00, "bottom": 51.41},
    {"chainage": 9500, "top": 50.00, "bottom": 45.65},
]



# Zoom settings:
z0 = [15500, 27000, -1, 1]
z1 = [9000, 26000, 40, 70] # Aval
z2 = [28000, 45000, 60, 85] # Millieu
z3 = [45000, 60000, 68, 100] # Amont
z4 = [5000, 10000, 30, 60 ] # Extra

zoom_is = z0

x_min, x_max, y_min, y_max = zoom_is[:]


# Add 75e wse from case 2 into case 1 dataframe for the same chainage 
cas1_ds = cas1_ds.merge(
    cas2_ds[['chainage','q75']],
    on='chainage',
    how='left',
    suffixes=("",'_cas2'))


# Calculate difference
cas1_ds['delta'] = cas1_ds['q75_cas2'] - cas1_ds['q75']

# Read bed data:
bed_df = pd.read_csv(bed_profile_path)
bed_df = bed_df.sort_values(by='River Sta')
chainage_black_line = bed_df['River Sta']
elevation_black_line = bed_df['Min Ch El']
    


line_width = 1;
lecolor = 'chocolate'
fontsize = 15
plt.rcParams.update({"font.size": fontsize})
fig, ax = plt.subplots(figsize=(12, 5))



if False:    
    # Ajout des rectangles (en arrière-plan avec zorder=0)
    for rect in rectangles_data:
        x_start = rect["chainage"]
        y_start = rect["bottom"]
        height = rect["top"] - rect["bottom"]
        rect_patch = Rectangle(
            (x_start, y_start),
            80,
            height,
            facecolor="gray",
            edgecolor="none",
            alpha=1,
            zorder=0,  # Derrière tout
        )
        ax.add_patch(rect_patch)
    
    
    # Ajout des rectangles (en arrière-plan avec zorder=0)
    for rect in seuils_data:
        x_start = rect["chainage"]
        y_start = rect["bottom"]
        height = rect["top"] - rect["bottom"]
        rect_patch = Rectangle(
            (x_start, y_start),
            80,
            height,
            facecolor="blue",
            edgecolor="none",
            alpha=1,
            zorder=0,  # Derrière tout
        )
        ax.add_patch(rect_patch)


# Plot difference
plt.plot(
    cas1_ds['chainage'],
    cas1_ds['delta'],
    color="blue",
    linewidth=line_width,
    # label="WSE médiane",
    # label='WSE median',
    zorder=1,
)

plt.plot([0,70000], [0,0], ':k')

# Mark chenal position
plt.plot([20583, 20583],[-0.3, 0.3], '-k')
plt.text(20583, 0.43, 'Entrée du chenal')

plt.plot([18241, 18241],[-0.28, 0.28], '-k')
plt.text(18241, 0.4, 'Sortie du chenal')

# general plot parameters
plt.xlabel("Chaînage (m)", fontsize=fontsize)
plt.ylabel("Delta niveau d'eau : \n Cas chenal moins cas base (m)", fontsize=fontsize)


if x_min!= 0 or x_max != 0:
    plt.xlim(x_min,x_max)

plt.ylim(y_min, y_max)
plt.legend(fontsize=fontsize-1, loc='lower right')
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.tight_layout(pad=0.1)

# Export:    
plt.savefig(png_export_path, format="png", bbox_inches="tight")
plt.show()
print(f"PNG exporté à : {png_export_path}")