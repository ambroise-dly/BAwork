## Accumulated all ERA5 datset from a path


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap

def accumulation(
    file_path,
    begin_date,
    end_date,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    name,
    output
):

    
    
    #E-OBS specific dates and location filter
    ERA5_file = xr.open_dataset(file_path)
    
    #define variabale of EOBS
    time = ERA5_file['time']
    precipitations = ERA5_file["tp"]
    lat = ERA5_file["latitude"]
    lon = ERA5_file["longitude"]

    begin_date = pd.to_datetime(begin_date) # adjust the time bcs ERA-5 is not like E-OBS
    end_date = pd.to_datetime(end_date)

    # Filter dates
    valid_dates = (time >= begin_date) & (time <= end_date)
    
    # Filter latitude and longitude
    valid_lat = (lat >= begin_lat) & (lat <= end_lat)
    valid_lon = (lon >= begin_long) & (lon <= end_long)
    
    # Apply the filters to the dataset
    filtered_ERA5 = ERA5_file.tp.sel(
        time=valid_dates,
        latitude=valid_lat,
        longitude=valid_lon
    )
    
    
    
    filtered_ERA5 = filtered_ERA5*1000 # because of the units in depth m to mm
    df = filtered_ERA5.to_dataframe(name = 'Precip')
    df = df.reset_index()

    # Sum precipitation 
    grouped_precip = df.groupby(['latitude', 'longitude'])
    
    summed_precip= grouped_precip['Precip'].sum()
    summed_precip = summed_precip.reset_index()
    
    # Rename the summed column 
    df_summed = summed_precip.rename(columns={'Precip': 'precipitation'})

    
    df_summed.to_csv(output + 'ERA5_orig.csv', index= False)
    