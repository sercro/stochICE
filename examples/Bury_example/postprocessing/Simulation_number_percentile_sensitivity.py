# -*- coding: utf-8 -*-
"""
Guide de l'utilisateur (Français)
----------------------------------
Ce script permet de visualiser la stabilisation des percentiles du niveau d'eau (WSE) 
en fonction du nombre de simulations incluses. Il lit un fichier CSV contenant une 
colonne 'WSE', mélange les valeurs aléatoirement sans remplacement, puis calcule les 
percentiles (25e, 50e, 75e, 90e et 100e) au fur et à mesure que les données sont ajoutées 
une à une. Le graphique résultant montre comment chaque percentile évolue et s’il atteint 
un plateau. Cela permet d’évaluer la stabilité statistique des estimations des niveaux d’eau.

Le fichier CSV d’entrée doit être au format produit par le script 
`Multivariate_WSE_regression_analysis.py`.

Guide for Users (English)
--------------------------
This script visualizes the stabilization of water surface elevation (WSE) percentiles 
as more simulations are added. It reads a CSV file containing a 'WSE' column, randomly 
shuffles the values without replacement, and then computes the 25th, 50th, 75th, 90th, 
and 100th percentiles as the sample size increases. The resulting figure illustrates how 
each percentile evolves and whether it reaches a plateau, allowing the user to assess 
the statistical stability of WSE estimates.

The input CSV file must be in the format produced by the 
`Multivariate_WSE_regression_analysis.py` script.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Paramètres utilisateur ===


# Baseline amont
chemin_csv = r"C:\Glace\StochICE_Assomption\StochICE_Assomption\StochICE_data_Assomption_02_amont_lowQ\Results\Individual_WSE_profiles\regression_analysis\chainage_48609\data_chainage_48609.csv"
dossier_sortie = r"C:\Glace\StochICE_Assomption\StochICE_Assomption\StochICE_data_Assomption_02_amont_lowQ\Results\Individual_WSE_profiles\regression_analysis\chainage_48609"

# Estacade amont
# chemin_csv = r"C:\Glace\StochICE_Assomption\StochICE_Estacade_Amont\StochICE_data_Assomption_Estacade_Amont\Results\Individual_WSE_profiles\regression_analysis\chainage_48609\data_chainage_48609.csv"
# dossier_sortie = r"C:\Glace\StochICE_Assomption\StochICE_Estacade_Amont\StochICE_data_Assomption_Estacade_Amont\Results\Individual_WSE_profiles\regression_analysis\chainage_48609"

# Créer le dossier de sortie s’il n’existe pas
os.makedirs(dossier_sortie, exist_ok=True)

# Charger les données
df = pd.read_csv(chemin_csv)

# Extraire les valeurs WSE
valeurs_wse = df["WSE"].values
n = len(valeurs_wse)

# Définir les percentiles à suivre
percentiles_a_suivre = [25, 50, 75, 90, 100]
resultats = {p: [] for p in percentiles_a_suivre}

# Mélanger aléatoirement les valeurs de WSE
np.random.seed(42)
wse_melange = np.random.permutation(valeurs_wse)

# Calcul des percentiles pour des tailles d’échantillons croissantes
for i in range(1, n + 1):
    echantillon = wse_melange[:i]
    for p in percentiles_a_suivre:
        resultats[p].append(np.percentile(echantillon, p))

# Types de ligne pour différencier les courbes
types_ligne = {
    25: 'solid',
    50: 'dashed',
    75: 'dashdot',
    90: 'dotted',
    100: (0, (1, 1)),  # pointillés très fins
}

# Tracer la figure
plt.figure(figsize=(6, 4))
for p in percentiles_a_suivre:
    plt.plot(
        range(1, n + 1),
        resultats[p],
        label=f"{p}e percentile",
        linestyle=types_ligne[p],
        color="black"
    )

plt.xlabel("Nombre de simulations incluses")
plt.ylabel("Valeur du percentile du niveau d'eau (m)")

plt.tight_layout()

# Sauvegarder la figure
chemin_fig = os.path.join(dossier_sortie, "convergence_percentiles_WSE.pdf")
plt.savefig(chemin_fig, format="pdf")

print(f"Figure enregistrée : {chemin_fig}")
