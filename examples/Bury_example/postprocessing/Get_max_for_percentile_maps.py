# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 17:44:26 2025

@author: cros1803
"""

import os
import time
import numpy as np
import rasterio
from rasterio.windows import Window
import csv


# Output file path

# Case for UMax= 5m/s
output_directory = r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\joint_max_results_baseline"
output_file = os.path.join(output_directory,"Assomption_max_75e_2000maps.tif")

# 75% 
file_list = [r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_amont\Results\Percentile_maps\Assomption_baseline_amont_percentile_75_2000maps_parallel.tif",
             r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_millieu\Results\Percentile_maps\Assomption_baseline_milieu_percentile_75_2000maps_parallel.tif",
             r"C:\Glace\StochICE_Assomption\HECRAS\StochICE_Assomption\StochICE_data_Assomption_baseline_aval\Results\Percentile_maps\Assomption_baseline_aval_percentile_75_2000maps_parallel.tif",]


# Open all rasters
rasters = [rasterio.open(f) for f in file_list]

# Read metadata from the first raster
meta = rasters[0].meta.copy()

# Read all raster data into a 3D numpy array (layers, rows, cols)
data_stack = np.array([r.read(1) for r in rasters])

# Compute the maximum value per pixel across all rasters
max_data = np.max(data_stack, axis=0)

# Optional: mask nodata values
nodata = meta.get('nodata', None)
if nodata is not None:
    mask = np.all(data_stack == nodata, axis=0)
    max_data[mask] = nodata

# Update metadata if necessary
meta.update(dtype=rasterio.float32)


# Write result to new raster file
with rasterio.open(output_file, 'w', **meta) as dst:
    dst.write(max_data.astype(rasterio.float32), 1)

# Close all opened rasters
for r in rasters:
    r.close()

print(f"Maximized joint file written to: {output_file}")
