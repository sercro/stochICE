
# -*- coding: utf-8 -*-
"""
Guide de l'utilisateur (Français)
--------------------------------
Ce script génère une enveloppe des niveaux d'eau (WSE) à partir de fichiers CSV
générés par HEC-RAS, en calculant les percentiles et en superposant le profil de
lit et des rectangles représentant des ponts ou seuils. Les rectangles sont
placés derrière les enveloppes pour une meilleure visibilité.

Paramètres à modifier :
- `directory` : Chemin vers les fichiers CSV de profils WSE.
- `bed_profile_path` : Chemin vers le fichier CSV du profil de lit.
- `pdf_export_path` : Chemin pour exporter le graphique PDF.
- `y_min`, `y_max` : Limites de l'axe y (en mètres).
- `shift` : Décalage du chaînage pour aligner avec le profil de lit.
- `rectangles_data` : Liste des données pour les rectangles (chaînage, haut, bas).

Sorties :
- Un graphique PDF des enveloppes WSE exporté à `pdf_export_path`.

Utilisation :
1. Ajustez les paramètres ci-dessus selon vos données.
2. Exécutez le script. Vérifiez le message de confirmation ou les erreurs.

User Guide (English)
-------------------
This script generates a water surface elevation (WSE) envelope from HEC-RAS-
generated CSV files, computing percentiles and overlaying the bed profile and
rectangles representing bridges or weirs. Rectangles are plotted behind the
envelopes for better visibility.

Parameters to modify:
- `directory`: Path to the WSE profile CSV files.
- `bed_profile_path`: Path to the bed profile CSV file.
- `pdf_export_path`: Path to export the PDF plot.
- `y_min`, `y_max`: Y-axis limits (in meters).
- `shift`: Chainage shift to align with the bed profile.
- `rectangles_data`: List of rectangle data (chainage, top, bottom).

Outputs:
- A PDF plot of WSE envelopes saved at `pdf_export_path`.

Usage:
1. Adjust the parameters above based on your data.
2. Run the script. Check the confirmation message or errors.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


# Some useful functions: 
def produce_percentiles(directory, river):    
        # Collecte des données WSE
        # ------------------------
        
        filter_str = river
        
        files = [
            f for f in os.listdir(directory)
            if filter_str in f and f.endswith(".csv")
            # if filter_str in f and f.endswith(".csv")
        ]
        
        if not files:
            print(f"Aucun fichier correspondant trouvé dans {directory}.")
            exit()
        
        dfs = []
        for file in files:
            try:
                df = pd.read_csv(os.path.join(directory, file))
                dfs.append(df)
            except Exception as e:
                print(f"Erreur lors de la lecture de {file} : {e}")
        
        if not dfs:
            print("Aucun fichier CSV valide à tracer.")
            exit()
        
        chainage = dfs[0]["Chainage (m)"]

        wse_series = [df["wse (m)"] for df in dfs]
        wse_df = pd.concat(wse_series, axis=1)      

        output_dict = {'chainage':dfs[0]["Chainage (m)"],
                       'q10':wse_df.quantile(0.10, axis=1),
                       'q20':wse_df.quantile(0.20, axis=1),
                       'q25':wse_df.quantile(0.25, axis=1),
                       'q30':wse_df.quantile(0.30, axis=1),
                       'q40':wse_df.quantile(0.40, axis=1),
                       'q50':wse_df.quantile(0.50, axis=1),
                       'q60':wse_df.quantile(0.60, axis=1),
                       'q70':wse_df.quantile(0.70, axis=1),
                       'q75':wse_df.quantile(0.75, axis=1),
                       'q80':wse_df.quantile(0.80, axis=1),
                       'q90':wse_df.quantile(0.90, axis=1),
                       'q100':wse_df.quantile(1.00, axis=1),
                       'median_wse':wse_df.quantile(0.50, axis=1),
                       'min_wse':wse_df.min(axis=1),
                       'max_wse':wse_df.max(axis=1)}
        
        output_df = pd.DataFrame(output_dict)
        output_df = output_df.sort_values(by='chainage')
        
        return output_df




# Paramètres spécifiés par l'utilisateur
# --------------------------------------

# detail = 2 # Index refers to detail (figure zoom in). 999 is Default

detail_limits = pd.DataFrame({'text':['det1','det2','det3'], 'x_min':[100, 2400, 4800], 'x_max':[400, 3400, 6000], 'y_min':[156, 165, 176], 'y_max':[170, 180, 190]})
message = ''



# cases with old HEC-RAS model
case_dict= [["Bury_beta_test",r"C:\Users\cros1803\Desktop\new_StochICE_version_in_prep\case_folders\Bury\Bury_example\Bury_example\StochICE_data_Bury_beta_test\\"],
            ]


bed_profile_path = (r"C:\Users\cros1803\Desktop\new_StochICE_version_in_prep\case_folders\Bury\Bury_example\Bury_profile.csv") 


index = 0; # Case entry in case_dict

directory_root = case_dict[index][1]

directory = directory_root + "\\Results\\Individual_WSE_profiles"
pdf_export_path_org = directory_root + "\\Results\\WSE_envelopes\\" 
case = case_dict[index][0]

if not os.path.exists(pdf_export_path_org):
    os.makedirs(pdf_export_path_org)

detail = 999

z0 = [0, 0, 196, 208]
z1 = [10000, 18000, 45, 65] # Aval
z2 = [28000, 38000, 60, 85] # Millieu
z3 = [45000, 52000, 65, 90] # Amont

zoom_is = z0

x_min, x_max, y_min, y_max = zoom_is[:]

shift = 0  # Décalage du chaînage (m)

texte = ''

# Determine details and update parameters accordingly:
    
if detail < 999:
    texte, x_min, x_max, y_min, y_max = detail_limits.iloc[detail,:]

    texte = '_'+texte


# Produce rectangles for inline structures
rectangles_data = [  # Données des rectangles : chaînage, haut, bas (m)
    # {"chainage": 59512, "top": 96.44, "bottom": 88.26},
    # {"chainage": 37435, "top": 82.08, "bottom": 65.68},
    # {"chainage": 15468, "top": 59.73, "bottom": 52.68},
    # {"chainage": 12500, "top": 61.07, "bottom": 49.99},
    # {"chainage": 11395, "top": 60.24, "bottom": 50.13},
    # {"chainage": 11253, "top": 59.29, "bottom": 49.04},
    # {"chainage": 9785, "top": 57.65, "bottom": 49.22},
    # {"chainage": 9223, "top": 52.18, "bottom": 40.63},    
    # {"chainage": 7895, "top": 52.06, "bottom": 39.86},
    # {"chainage": 6840, "top": 42.36, "bottom": 29.55},
]

seuils_data = [
    # {"chainage": 10013, "top": 54.00, "bottom": 51.41},
    # {"chainage": 9500, "top": 50.00, "bottom": 45.65},
]


# Lecture du profil de lit
# ------------------------
bed_df = pd.read_csv(bed_profile_path)
bed_df = bed_df.sort_values(by='River Sta')
chainage_black_line = bed_df['River Sta']
elevation_black_line = bed_df['Min Ch El']
    
df_river1 = produce_percentiles(directory, 'River 1')
# df_river1 = df_river1[df_river1['chainage'] > 500]

if True: 
    branch = 'Main'
    # Création du graphique
    # ---------------------
    line_width = 1;
    lecolor = 'chocolate'
    fontsize = 15
    plt.rcParams.update({"font.size": fontsize})
    fig, ax = plt.subplots(figsize=(12, 5))
    # fig, ax = plt.subplots(figsize=(6, 7))
    
    # Ajout des rectangles (en arrière-plan avec zorder=0)
    for rect in rectangles_data:
        x_start = rect["chainage"]
        y_start = rect["bottom"]
        height = rect["top"] - rect["bottom"]
        rect_patch = Rectangle(
            (x_start, y_start),
            20,
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
            20,
            height,
            facecolor="gray",
            edgecolor="none",
            alpha=1,
            zorder=0,  # Derrière tout
        )
        ax.add_patch(rect_patch)
    
            
    # Ajout des enveloppes WSE (zorder=1) et profil de lit (zorder=2)
    # plt.fill_between(
    #     chainage_shifted,
    #     min_wse,
    #     max_wse,
    #     color="blue",
    #     alpha=0.1,
    #     # label="0 à 100 percentile",
    #     label='0 - 100 percentile',
    #     zorder=1,
    # )
    
    plt.fill_between(
        df_river1['chainage'] + shift,
        df_river1['q90'],
        df_river1['q10'],
        color="blue",
        alpha=0.2,
        # label="10e à 90e percentile",
        label='10 - 90 percentile',
        zorder=1,
    )

    
    
    plt.fill_between(
        df_river1['chainage'] + shift,
        df_river1['q25'],
        df_river1['q75'],
        color="blue",
        alpha=0.4,
        # label="25e à 75e percentile",
        label='25 - 75 percentile',
        zorder=1,
    )
   
    plt.plot(
        df_river1['chainage'] + shift,
        df_river1['median_wse'],
        color="blue",
        linewidth=line_width,
        # label="WSE médiane",
        label='WSE median',
        zorder=1,
    )

    # plt.plot(
    #     chainage_black_line,
    #     elevation_black_line,
    #     color="black",
    #     linewidth=1.5,
    #     label="Talweg",
    #     zorder=2,
    # )
    
    
    
    #Plot talweg
    plot_df = bed_df
    
    plt.plot(
        plot_df['River Sta']+shift,
        plot_df['Min Ch El'],
        color="black",
        linewidth=1.5,
        label="Talweg",
        zorder=2,
    ) 
    

    
    if True: 
    
        # Ajoute tree scar mesures
        exp_chainage = [3128.886, 3111.886, 3090.986, 3095.686, 3077.586, 2920.54, 2916.24, 2895.64, 2891.64, 2506.29, 2493.59, 2496.29, 2483.39, 2480.79,1809.95] # Experimental chainage
        exp_chainage = [chain_m*0.3048 for chain_m in exp_chainage]
        exp_niveau = [205.27 ,204.88 ,204.33 ,203.99 ,204.76 ,205.04 ,205.06 ,204.1 ,204.18 ,204.54 ,203.29 ,204.17 ,203.88 ,203.4 ,202.44] #  Experimental niveau    
    
        cicats_1 = pd.DataFrame({'Chainage':exp_chainage, 'Height':exp_niveau})
        
        plt.scatter(
            cicats_1['Chainage'], 
            cicats_1['Height'],    
            marker='o', edgecolor='black', s=35, color='red', zorder=1, label='Cicatrices'
            )        

    
    # add note
    if True:
      message = ''
      plt.text(0.75*(x_max-x_min)+x_min, y_max-2, message, fontsize=fontsize)  
    
    # Write case
    # plt.text(0.75*(x_max-x_min)+x_min, y_max-4, case, fontsize=fontsize)
    
    plt.xlabel("(local) Distance (m)", fontsize=fontsize)
    plt.ylabel("Surface elevation (m)", fontsize=fontsize)
    
    if x_min!= 0 or x_max != 0:
        plt.xlim(x_min,x_max)
    
    plt.ylim(y_min, y_max)
    plt.legend(fontsize=fontsize-1, loc='lower right')
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.tight_layout(pad=0.1)
    
    # Exportation du PDF
    pdf_export_path = pdf_export_path_org+case+'_'+branch+'_'+texte+'.png'
    plt.savefig(pdf_export_path, format="png", bbox_inches="tight")
    plt.show()
    print(f"PNG exporté à : {pdf_export_path}")


    csv_export_path = pdf_export_path_org+case+texte+'.csv'
    df_river1.to_csv(csv_export_path, index=False)
    print(f"Percentile results exporté à : {csv_export_path}")
            


