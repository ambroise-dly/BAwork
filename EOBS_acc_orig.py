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
    EOBS_file = xr.open_dataset(file_path)
    
    #define variabale of EOBS
    time = EOBS_file['time']
    precipitations = EOBS_file["rr"]
    lat = EOBS_file["latitude"]
    lon = EOBS_file["longitude"]

    # Define the filtering ranges
    begin_date = pd.to_datetime(begin_date) #6UTC the day before until 6UTC 
    end_date = pd.to_datetime(end_date)
    
    
    # Filter dates
    valid_dates = (time >= begin_date) & (time <= end_date)
    
    # Filter latitude and longitude
    valid_lat = (lat >= begin_lat) & (lat <= end_lat)
    valid_lon = (lon >= begin_long) & (lon <= end_long)
    
    # Apply the filters to the dataset
    filtered_EOBS = EOBS_file.rr.sel(
        time=valid_dates,
        latitude=valid_lat,
        longitude=valid_lon
    )
    
    df = filtered_EOBS.to_dataframe(name = 'Precip')
    df = df.reset_index()

    # Sum precipitation 
    summed_precip = filtered_EOBS.sum(dim='time')
    
    # Convert to pandas DataFrame
    df_summed = summed_precip.to_dataframe(name='precipitation')
    
    df_summed = df_summed.reset_index()

    df_summed.to_csv(output + 'EOBS_orig.csv', index = False)
