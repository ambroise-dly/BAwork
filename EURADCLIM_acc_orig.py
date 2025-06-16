####
# EURADCLIM accumulation, projection and create a csv file
####

from AccumulateRadarHDF5ODIMListCount import accumulate_radar_hdf5
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import h5py
from pyproj import Proj
import os
from datetime import datetime
import h5py
import sys
from scipy.interpolate import griddata
from VisualizeDF5ODIMCartopy import visualize_hdf5_odim_cartopy
import site
# Get the user site-packages directory
user_site_packages = site.getusersitepackages()

# Add it to sys.path if it's not already there
if user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

# Now import the package installed with --user
import natsort  # Replace with the package you want to import


def accumulation (
    output,
    file_path,
    end_date,
    end_time,
    name,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    output_accumulation
    
    
):

    ## from https://github.com/overeem11/EURADCLIM-tools/tree/main
    
    accumulate_radar_hdf5(
    output_filename= output_accumulation,
    input_filenames=file_path,
    date = end_date,
    time = end_time,
    conversion_factor = 1.0,
    min_images =1 ,
    input_filename_nodata='/home/adelaly/BA_work/events/RAD_OPERA_RAINFALL_RATE_201812110715.h5',   
    path_or_filenames = 'path'
    )

   
    ## make a csv file from the accumulate
    # Define input file and dataset path
    input_filename = output_accumulation
    dataset_nr = "/dataset1"
    
    # Read HDF5 file
    with h5py.File(input_filename, mode='r') as f:
        # Get dimensions
        Ncols = int(f['/where'].attrs['xsize'])
        Nrows = int(f['/where'].attrs['ysize'])
    
        # Get scaling and offset
        ATTR_NAME = dataset_nr + '/what'
        zscale = f[ATTR_NAME].attrs['gain']
        zoffset = f[ATTR_NAME].attrs['offset']
        nodata = f[ATTR_NAME].attrs['nodata']
        undetect = f[ATTR_NAME].attrs['undetect']
    
        # Read precipitation data
        DATAFIELD_NAME = dataset_nr + '/data1/data'
        dset = f[DATAFIELD_NAME][:]
        RArray = zoffset + zscale * dset  # Apply scaling and offset
    
    # Read coordinates
    Grid = np.array(pd.read_csv("CoordinatesHDF5ODIMWGS84.dat", delimiter=" ", dtype="float", header=None))
    Xcoor = Grid[:, 0]  # Longitude
    Ycoor = Grid[:, 1]  # Latitude
    # Filter data
    filtered_longitudes = []
    filtered_latitudes = []
    filtered_precipitation = []
    
    for j in range(Nrows):
        for i in range(Ncols):
            lon = Xcoor[i + j * Ncols]
            lat = Ycoor[i + j * Ncols]
            precip = RArray[j, i]
    
            # Apply filtering
            if (begin_long <= lon <= end_long) and (begin_lat <= lat <= end_lat):
                filtered_longitudes.append(lon)
                filtered_latitudes.append(lat)
                filtered_precipitation.append(precip)
    
    # Convert to numpy arrays
    filtered_longitudes = np.array(filtered_longitudes)
    filtered_latitudes = np.array(filtered_latitudes)
    filtered_precipitation = np.array(filtered_precipitation)
    
    # Create DataFrame
    df = pd.DataFrame({
        'longitude': filtered_longitudes,
        'latitude': filtered_latitudes,
        'precipitation': filtered_precipitation
    })
    df.to_csv(output + 'EURADCLIM_orig.csv', index = False)
    return df