import pandas as pd

import os
import glob
import shutil
import random
import time
import win32com.client
import numpy as np
import statistics
import rasterio
# import re
import csv
import h5py

from matplotlib.patches import Rectangle

from scipy.ndimage import label

from matplotlib import pyplot as plt


from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import argparse



# Postprocessing functions most like used directly by users: 

def produce_percentiles(directory, river):    
    """
    Reads the individual wse profiles in directory, and produces the 0 : 10 : 100 percentiles

    Args:
        directory (str): path to the folder with the individual WSE profiles produced by HECRAS
        river (str): name of the river (same as HECRAS) along which the percentiles are calculated 

    """
    # Collecte des données WSE
    # ------------------------
    
    filter_str = river
    
    files = [
        f for f in os.listdir(directory)
        if filter_str in f and f.endswith(".csv")
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


# stochICE simulation functions

def plot_basic_wse_envelope(wse_profiles_path, basic_wse_path):
	"""
	Generates water surface elevation (WSE) envelope plots.

	This method groups CSV files by river number, plots the WSE profiles for
	each river, and saves the plots to the WSE_envelopes folder.

	Args:
		None

	Returns:
		None
	"""
	river_files = {}

	# Collect files grouped by river number
	for root, dirs, files in os.walk(wse_profiles_path):
		for file in files:
			if file.endswith('.csv') and 'River' in file:
				river_number = file.split('_')[0]  # Extract river number
				if river_number not in river_files:
					river_files[river_number] = []
				river_files[river_number].append(os.path.join(root, file))

	# envelope_path = os.path.join(results_path, "WSE_envelopes")
	# os.makedirs(envelope_path, exist_ok=True)

	# Plot WSE profiles for each river
	for river_number, file_paths in river_files.items():
		plt.figure(figsize=(10, 6))
		for file_path in file_paths:
			data = pd.read_csv(file_path)
			plt.plot(data.iloc[:, 0], data.iloc[:, 1], label=os.path.basename(file_path))

		# Set plot properties
		plt.xlabel('Chainage (m)')
		plt.ylabel('Water Surface Elevation (m)')
		plt.title(f'Water Surface Elevation Profile for {river_number}')
		plt.legend()

		# Save the plot
		plot_filename = os.path.join(basic_wse_path, f"{river_number}_wse_envelope.png")
		plt.savefig(plot_filename)
	   
		plt.close()




def create_combined_maximum_depth_map(max_depth_path):
	"""
	Creates a combined maximum depth map from individual depth map files.

	This method finds and combines all maximum depth map TIFF files into
	a single raster file representing the maximum depths across all simulations.

	Args:
		None

	Returns:
		None
	"""
	depth_map_files = glob.glob(os.path.join(max_depth_path, "maximum_depth_map_*.tif"))

	if not depth_map_files:
		print("Warning: No 'maximum_depth_map' files found. Path too long?")
		return

	with rasterio.open(depth_map_files[0]) as src:
		meta = src.meta
		depth_stack = np.stack([rasterio.open(f).read(1) for f in depth_map_files])

	max_depth = np.max(depth_stack, axis=0)
	meta.update(dtype=rasterio.float32, count=1, compress='DEFLATE')

	combined_path = os.path.join(max_depth_path, "combined_maximum_depth_map.tif")
	with rasterio.open(combined_path, 'w', **meta) as dst:
		dst.write(max_depth.astype(rasterio.float32), 1)




def create_combined_maximum_wse_map(max_wse_path):
	"""
	Creates a combined maximum wse map from individual wse map files.

	This method finds and combines all maximum wse map TIFF files into
	a single raster file representing the maximum wse across all simulations.

	Args:
		None

	Returns:
		None
	"""
	wse_map_files = glob.glob(os.path.join(max_wse_path, "maximum_wse_map_*.tif"))

	if not wse_map_files:
		print("No 'maximum_wse_map' files found.")
		return

	with rasterio.open(wse_map_files[0]) as src:
		meta = src.meta
		wse_stack = np.stack([rasterio.open(f).read(1) for f in wse_map_files])

	max_wse = np.max(wse_stack, axis=0)
	meta.update(dtype=rasterio.float32, count=1, compress='DEFLATE')

	combined_path = os.path.join(max_wse_path, "combined_maximum_wse_map.tif")
	with rasterio.open(combined_path, 'w', **meta) as dst:
		dst.write(max_wse.astype(rasterio.float32), 1)
	


def create_combined_frequency_map(frequency_tif_path,simulations_per_process):
	"""
	Creates a combined flood frequency map from individual frequency map files.

	This method calculates the global flood frequency across all simulations and
	generates a combined map with values representing the percentage of flooding (0-100).

	Args:
		None

	Returns:
		None
	"""
	# Get list of frequency map files
	frequency_map_files = glob.glob(os.path.join(frequency_tif_path, "frequency_floodmap_*.tif"))
	if not frequency_map_files:
		print("No 'frequency_floodmap' files found.")
		return

	# Number of simulations per map (from your parse method)
	# simulations_per_process = StochHECRAS_parallel.parse_simulation_count()
	num_maps = len(frequency_map_files)
	total_simulations = simulations_per_process * num_maps

	# Read and process the maps
	with rasterio.open(frequency_map_files[0]) as src:
		meta = src.meta
		# Initialize array to accumulate the number of flooded instances
		flooded_count = np.zeros(src.shape, dtype=np.float32)

	# For each map, convert percentage to flooded count and accumulate
	for f in frequency_map_files:
		with rasterio.open(f) as src:
			frequency_data = src.read(1)  # Values are 0-100 (percentage)
			# Convert percentage to number of flooded simulations for this map
			flooded_in_map = (frequency_data / 100.0) * simulations_per_process
			flooded_count += flooded_in_map

	# Calculate global frequency as a percentage
	combined_frequency = (flooded_count / total_simulations) * 100.0
	combined_frequency = np.clip(combined_frequency, 0, 100)  # Ensure range 0-100

	# Update metadata and write output
	meta.update(dtype=rasterio.float32, count=1, compress='DEFLATE')
	combined_path = os.path.join(frequency_tif_path, "combined_frequency_floodmap.tif")
	with rasterio.open(combined_path, 'w', **meta) as dst:
		dst.write(combined_frequency, 1)

	print(f"Combined frequency map created at {combined_path}")







def print_hola():
	print('\n\nHola pato\n\n')


