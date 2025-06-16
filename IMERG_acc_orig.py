## Accumulated some IMERG files from a path into a csv unique file


import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import h5py
from glob import glob
import os
from matplotlib.colors import LinearSegmentedColormap


def accumulation(
    file_path,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    name,
    output
):
    
    
    # code from https://github.com/nasa/gesdisc-tutorials/blob/main/notebooks/How_to_Read_IMERG_Data_Using_Python.ipynb


    files_names = glob( file_path + '/*.HDF5*' )
    input_dir = file_path
   
    
    accumulated_precip = None
    for x in files_names:
        df = xr.open_mfdataset(x, group = 'Grid')
        precip = df['precipitation'][0,:,:].values
        precip = np.transpose(precip)
        precip = precip/2
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
    #print(df)

 
    df.to_csv(output + 'IMERG_orig.csv', index= False)