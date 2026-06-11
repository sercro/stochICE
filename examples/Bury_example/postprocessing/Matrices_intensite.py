# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 12:14:24 2025

@author: dugj2403
"""

import rasterio
import numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon
from rasterio.features import shapes
import geopandas as gpd
import os

def extract_depth_polygons(geotiff_path, output_dir):
    """
    Extract polygons from a GeoTIFF based on water depth ranges and save as shapefiles.
    
    Parameters:
    geotiff_path (str): Path to the input GeoTIFF file
    output_dir (str): Directory to save the output shapefiles
    """
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the GeoTIFF file
    with rasterio.open(geotiff_path) as src:
        # Read the data as a numpy array
        depth_data = src.read(1)  # Assuming depth data is in the first band
        transform = src.transform  # Get the georeferencing transform
        crs = src.crs  # Get the coordinate reference system
        
        # Create binary masks for each depth range
        mask_high = depth_data > 0.6
        mask_mid = (depth_data >= 0.3) & (depth_data <= 0.6)
        mask_low = (depth_data > 0) & (depth_data < 0.3)
        
        # Function to convert mask to a single polygon
        def mask_to_polygon(mask, transform):
            # Generate shapes (polygons) from the mask
            shape_gen = shapes(mask.astype(np.uint8), mask=mask, transform=transform)
            
            # Collect all polygons into a list
            polygons = [shape(geom) for geom, _ in shape_gen]
            
            # If no polygons are found, return None
            if not polygons:
                return None
                
            # Merge all polygons into a single MultiPolygon or Polygon
            merged = MultiPolygon(polygons).buffer(0)  # buffer(0) cleans up geometry
            
            # Simplify to a single Polygon if possible
            if isinstance(merged, MultiPolygon) and len(merged.geoms) == 1:
                return merged.geoms[0]
            return merged
        
        # Generate polygons for each depth range
        poly_high = mask_to_polygon(mask_high, transform)
        poly_mid = mask_to_polygon(mask_mid, transform)
        poly_low = mask_to_polygon(mask_low, transform)
        
        # Prepare GeoDataFrames for each depth range
        depth_ranges = [
            ('depth_gt_0.6m', poly_high),
            ('depth_0.3-0.6m', poly_mid),
            ('depth_0-0.3m', poly_low)
        ]
        
        for name, poly in depth_ranges:
            if poly is not None:
                # Create a GeoDataFrame
                gdf = gpd.GeoDataFrame({'geometry': [poly]}, crs=crs)
                
                # Define output shapefile path
                output_path = os.path.join(output_dir, f'{name}.shp')
                
                # Save to shapefile
                gdf.to_file(output_path)
                print(f"Saved {name} to {output_path}")
            else:
                print(f"No data found for {name}")

# Example usage
if __name__ == "__main__":
    geotiff_file = r"C:\Users\dugj2403\Desktop\Chateauguay_final_5mars2025\HECRAS_project_folder\StochICE_data_Final_Q_fixed_475\Results\Individual_depth_tifs_downsampled\percentile_90_2998maps_new.tif"
    output_directory = r"C:\Users\dugj2403\Desktop\Chateauguay_final_5mars2025\HECRAS_project_folder\StochICE_data_Final_Q_fixed_475\Results\Matrices_intensite"
    extract_depth_polygons(geotiff_file, output_directory)