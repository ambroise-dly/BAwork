#####
#this python script as two function: make a projection with the MSWEP raw_data and create a array file with precipitation acccumulation on every cell
#####

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset
from glob import glob
from matplotlib.colors import LinearSegmentedColormap

def accumulation(
    input_dir,
    output,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    name
):
   
    
    files_names = glob(input_dir + '/*.nc*')
    accumulated_precip = None

    # extract from each files the localisation and the precipitations values
    for x in files_names:
        df = xr.open_dataset(x)
        precip = df['precipitation'][0,:].values
        #precip = np.transpose(precip)
        theLats = df['lat'].values
        theLons = df['lon'].values
        
    
        lat_filter = ( theLats>= begin_lat) & (theLats <= end_lat)
        lon_filter = (theLons >= begin_long) & (theLons <= end_long)
        precip_filtered = np.zeros_like(precip)
        precip_filtered[:, lon_filter] = precip[ :, lon_filter]
        precip_filtered[lat_filter,:] = precip[lat_filter,:]
        
     # Accumulate precipitation
        if accumulated_precip is None:
            accumulated_precip = np.zeros_like(precip_filtered)
            accumulated_precip = precip_filtered
        else:
            accumulated_precip += precip_filtered

    filtered_lats = theLats[lat_filter]
    filtered_lons = theLons[lon_filter]
    total_precipitation = accumulated_precip[lat_filter,:][:,lon_filter]

    # Create a DataFrame
    rows = []
    for i, lat in enumerate(filtered_lats):
        for j, lon in enumerate(filtered_lons):
            rows.append({
                'precipitation': total_precipitation[i, j],
                'longitude': lon,
                'latitude': lat
            })
    
    df = pd.DataFrame(rows)
    

    df.to_csv(output + 'MSWEP_orig.csv', index = False)
