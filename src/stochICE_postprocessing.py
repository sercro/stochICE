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