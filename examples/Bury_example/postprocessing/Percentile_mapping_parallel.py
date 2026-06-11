import os
import time
import numpy as np
import math as mt
import rasterio
from rasterio.windows import Window
import csv
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import argparse



# List of case directories, each entry is : [[case_name,case_directory]]
cases_list = [['Bury_beta_test',r'C:\Users\cros1803\Desktop\new_StochICE_version_in_prep\case_folders\Bury\Bury_example\Bury_example\StochICE_data_Bury_beta_test'],
              #["other_case" ,r"other_case_directory"],
              ]


# percentiles = [50,75,90]
percentiles = [75,] #90] # add as many percentiles as you want, they will be computed for each case in cases_list 


tile_size = 512*0 + 1280
coordinates = [(193570.5014586, 207533.5023082)]  # (x, y)

# ========== FUNCTION TO PROCESS A TILE ==========
def process_tile(tile_info):

    # percentile = 75


    row_off, col_off, win_h, win_w, file_list, percentile = tile_info
    window = Window(col_off=col_off, row_off=row_off, width=win_w, height=win_h)

    tile_stack = []
    for file_path in file_list:
        with rasterio.open(file_path) as ds:
            tile_data = ds.read(1, window=window)
            tile_stack.append(tile_data)
    tile_stack = np.array(tile_stack)  # shape: (num_files, win_h, win_w)
    p75 = np.percentile(tile_stack, percentile, axis=0).astype(np.float32)
    return (row_off, col_off, window, p75)

# ========== MAIN FUNCTION ==========
def main(case_list):

    total_cases = len(case_list)    
    case_nbr = 1
    for case_line in case_list:
        case_name = case_line[0]
        case_folder = case_line[1]
    
    
        input_folder = os.path.join(case_folder, 'Results','Individual_depth_tifs')       
        output_folder = os.path.join(case_folder, 'Results','Percentile_maps') 

        # Create destination directory if it does not exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
    
        for percentile in percentiles:
        
            # --- Parse command-line argument for number of processes ---
            parser = argparse.ArgumentParser(description="Parallel raster percentile processor")
            parser.add_argument('--nprocs', type=int, default=multiprocessing.cpu_count(),
                                help="Number of parallel processes to use (default: use all available cores)")
            args = parser.parse_args()
            nprocs = args.nprocs
            print(f"Using {nprocs} parallel processes.")
        
            # --- Gather raster files ---
            file_list = [os.path.join(input_folder, f) for f in os.listdir(input_folder)
                         if f.lower().endswith(('.tif', '.tiff'))]
            file_list.sort()
            num_files = len(file_list)
            if num_files == 0:
                raise FileNotFoundError("No GeoTIFF files found in the input folder.")
        
            with rasterio.open(file_list[0]) as ref:
                ref_profile = ref.profile
                height, width = ref.height, ref.width
                crs = ref.crs
                transform = ref.transform
        
            # --- Prepare output raster ---
            out_profile = ref_profile.copy()
            out_profile.update(count=1, dtype=np.float32)
            output_path = os.path.join(output_folder, f"{case_name}_percentile_{percentile}_{num_files}maps_parallel.tif")
        
            # --- Generate tile info list ---
            tile_infos = []
            for row_off in range(0, height, tile_size):
                for col_off in range(0, width, tile_size):
                    win_h = min(tile_size, height - row_off)
                    win_w = min(tile_size, width - col_off)
                    tile_infos.append((row_off, col_off, win_h, win_w, file_list, percentile))
        
            start_time = time.time()
            print(f"Processing {len(tile_infos)} tiles in parallel...")
        
            # --- Parallel processing of tiles ---
            with rasterio.open(output_path, 'w', **out_profile) as out_ds:
                with ProcessPoolExecutor(max_workers=nprocs) as executor:
                    for i, result in enumerate(executor.map(process_tile, tile_infos)):
                        row_off, col_off, window, p75 = result
                        out_ds.write(p75, 1, window=window)
                        print(f"[{percentile}] Tile {i+1}/{len(tile_infos)} done (row_off={row_off}, col_off={col_off})")
        
                        if ((i>1) and (i % 10) == 0): # Prints ETA every 10 iterations
                            elapsed_time = time.time() - start_time
                            mean_time_per_tile = elapsed_time / (i)
                            estimated_remaining_time = (len(tile_infos) - i)  * mean_time_per_tile
                            eta_m, eta_s = divmod(estimated_remaining_time, 60)
                            eta_h, eta_m = divmod(eta_m, 60)
                            print(f"                  File [{case_nbr:.0f}/{total_cases:.0f}] - {output_path} remaining time (for this run): {eta_h:00.0f}:{eta_m:00.0f}:{eta_s:.1f}\n")
                            print(f"                  Estimated remaining time (for this run): {eta_h:00.0f}:{eta_m:00.0f}:{eta_s:.1f}\n")
        
        
            elapsed = time.time() - start_time
            print(f"Parallel processing complete in {elapsed:.1f} seconds.")
        
            # # ======= Coordinate Value Extraction ========
            # print("Extracting values at specified coordinates...")
            # datasets = [rasterio.open(fp) for fp in file_list]
            # all_coords_data = []
        
            # for ds in datasets:
            #     row_vals = []
            #     for (x, y) in coordinates:
            #         try:
            #             row, col = ds.index(x, y)
            #         except Exception:
            #             row, col = None, None
            #         if row is None or col is None or row < 0 or row >= ds.height or col < 0 or col >= ds.width:
            #             val = np.nan
            #         else:
            #             window = Window(col, row, 1, 1)
            #             arr = ds.read(1, window=window)
            #             val = float(arr[0, 0]) if arr.size > 0 else np.nan
            #         row_vals.append(val)
            #     all_coords_data.append(row_vals)
        
            # all_data_array = np.array(all_coords_data, dtype=float)
            # coord_values = {75: []}
            # for j in range(len(coordinates)):
            #     col_data = all_data_array[:, j]
            #     coord_values[75].append(float(np.nanpercentile(col_data, 75)))
        
            # coord_headers = [f"{x}_{y}" for (x, y) in coordinates]
            # csv_path = os.path.join(input_folder, f"percentile_75_values_at_coordinates.csv")
            # with open(csv_path, 'w', newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(["Map"] + coord_headers)
            #     for idx, row_vals in enumerate(all_coords_data):
            #         map_label = os.path.basename(file_list[idx])
            #         writer.writerow([map_label] + [row_vals[j] for j in range(len(coordinates))])
            #     writer.writerow(["P75"] + [coord_values[75][j] for j in range(len(coordinates))])
            # print(f"Wrote {csv_path}")
        
            # for ds in datasets:
            #     ds.close()
            print(f"{percentile} percentile processing complete.\n\n")
        case_nbr = case_nbr + 1




# ========== SAFETY GUARD FOR WINDOWS ==========
if __name__ == "__main__":
    
    main(cases_list)
