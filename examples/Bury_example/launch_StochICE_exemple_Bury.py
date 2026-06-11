

import os 
import pandas as pd 
import stochICE as ice


# Get current directory: 
cwd = os.getcwd()


src_folder = os.path.join(cwd,"Bury_example")
script_path = os.path.join(cwd,"Bury_example\\nothing.py")

jam_locations_file = os.path.join(cwd,"Bury_jam_locations.csv") # A csv (no header) containing jam locations. Column 0: jam head (aval). Column 1: jam end (amont)

# Next two lines read the jam_locations_file and create a list of lists to be parsed onto the 'jam_locations' key in params
jam_loc_df = pd.read_csv(jam_locations_file, names=('xo','xf'))
jam_locations_list = [list(pos) for pos in zip(jam_loc_df['xo'], jam_loc_df['xf'])]


# number of processors 
n_procs=4

# StochICE parameters
params = {
    'path': os.path.join(cwd,'Bury_example'), # Path to the HECRAS project files
    'batch_ID': 'Bury_tutorial_01', # Name of the stochastic simulation run. Results folder will be StochICE_data_'Batch_ID'
    'ras': 'Bury_SNormal_exampl.prj', # HECRAS project file name
    'geo': 'Bury_SNormal_exampl.g01', # HECRAS geo file name (must be .g01)
    'flowFile': 'Bury_SNormal_exampl.f01', # HECRAS flow file name (must be .f01)
    'wse': 'WSE (PF 1).Terrain.MNT_Bury_aval.MNT_Bury_Aval.tif', # WSE output raster filename
    'depth': 'Depth (PF 1).Terrain.MNT_Bury_aval.MNT_Bury_Aval.tif', # depth output raster filename

    'NSims': 4, # Number of simulations per processor 

    'write_maps': True, # If True, the frequency, maximum depth and maximum wse maps will be created (individuals and maximums)
    'ice_jam_in_OB': True, # If True, ice-jams cover the overbanks and main channel. False: ice-jams cover only the main channel. 
    'ice_fixed_manning': False, # False: Ice-jam Manning's n computed using Nezhikovsky's (recommended), True (not recommended): Ice-jam Manning's n is constant
    'ice_max_mean_velocity': 1.524, # Maximum mean velocity in the ice layer [m/s]
    'ice_jam_reach': 1, # Reach ID where ice jams occur 
    'reach_distributions' : [[1146.55, 1.0],], # List of the xsections with specified discharge in HEC-RAS (flow data), along with the corresponding proportion of the stochastically variable flowrate Q (defined in stochVars below).
                                               # e.g. : [[1146.55, 1.0], [851, 0.3],] means that the discharge is 1.0*Q at xsection 1146.55, and 0.3*Q at xsection 851. 

    # Stochastic variables. Each (excep jam_locations) requires a list with [distribution type, [min val, max val], number of decimals]
    'stochVars': { # 
        'Frontthick': ['uniform', [0.2, 0.8], 2], # Ice cover thickness, [m]
        'Q': ['uniform', [23.9, 37.1], 1], # River discharge, [m3 / s]
        'friction_angle': ['uniform', [30, 60], 0], # friction angle [degrees]
        'porosity': ['uniform', [0.4, 0.4], 2], # 0.4 Ice cover porosity [-]
        'ice_cover_n' : ['uniform', [0.01, 0.03], 4], # Stable ice cover manning's n [-]
        'jam_locations': jam_locations_list, # Lists of lists with specified ice-jam head and toe in format [[ice_jam_1_head,ice_jam_1_toe], [ice_jam_2_head,ice_jam_2_toe], etc]
        'ds_elevation' : ['uniform', [198.0, 200.0], 1], # Downstream boundary water surface elevation [m]
    }
}

# Seed file with the stochastic parameters used in a previous run 
seed=[os.path.join(cwd,'Batch_sim_parameters_exemple_4x4.csv'), # stochastic parameters file path (produced in a previous run)
    ['Q','Frontthick','phi','porosity','jam_loc_downstream']] # Variables to keep fixed (i.e., won't be rerolled) 

cleanup_after_run = True # Erase processor files after the run, keep only the ensemble results folder 

# Run without a seed file
stochastique=ice.stochHECRAS_parallel.StochHECRASParallel(src_folder,script_path,n_procs,params,cleanup_after_run=cleanup_after_run)


# Run WITH a seed file (uncomment the line below and comment the line above)
# stochastique=ice.stochHECRAS_parallel.StochHECRASParallel(src_folder,script_path,n_procs,params,seed=seed,cleanup_after_run=cleanup_after_run)