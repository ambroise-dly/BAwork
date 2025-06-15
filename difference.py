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
import rasterio
import osgeo
from osgeo import gdal
from rasterio.transform import from_origin
import rasterio
from rasterio.plot import show 
from matplotlib import colors
from projection import multiple_plots

def visualize(
    df,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    output,
    dataset_name
):
    
    pivot_df = df.pivot_table(
        index="latitude",  # Rows = latitude
        columns="longitude",  # Columns = longitude
        values="difference"  # Values = precipitation
    )
    
    # Extract the 2D arrays for latitude, longitude, and precipitation
    longitude_grid, latitude_grid = np.meshgrid(pivot_df.columns, pivot_df.index)
    precipitation_grid = pivot_df.values
    
    
    # Define a Lambert projection in Europe
    projection = ccrs.LambertConformal(central_longitude=10, central_latitude=50)
    
    # Create a figure
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': projection})
    ax.set_title(f"Precipitations difference (mm) during the event with {dataset_name}")
    
    # Add some border and coastline
    ax.add_feature(cfeature.BORDERS, linestyle=":", linewidth=1)
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    
    
    # Define limit to europe
    ax.set_extent([begin_long, end_long, begin_lat, end_lat], crs=ccrs.PlateCarree())

    norm = colors.TwoSlopeNorm( vmin= -150, vcenter=0, vmax = 150)
    # Plot the precipitation values as discrete grid cells
    mesh = ax.pcolormesh(
        longitude_grid,  # 2D longitude grid
        latitude_grid,   # 2D latitude grid
        precipitation_grid,  # 2D precipitation grid
        cmap='coolwarm',  # Colormap (e.g., "viridis", "plasma", "coolwarm")
        transform=ccrs.PlateCarree(),
        norm = norm
        
    )
    
    # Add a colorbar
    cbar = plt.colorbar(mesh, ax=ax, orientation="horizontal", pad=0.1)
    cbar.set_label("Total Precipitation difference(mm)")
    
    # Add a gridline
    ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5)
   
    
    plt.savefig( output+ dataset_name +'_diff2mean.png',dpi = 300)
    
    plt.show()


def difference2mean(
    datasets,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    output,
    vmax,
    vmin,
    vcenter,
    event,
    save,
    plot
    
    
):
    sum = 0
    for i in datasets:
        i['precipitation'] = np.where(i['precipitation'] == 0, np.nan, i['precipitation'])
        sum += i['precipitation']
    mean = sum / len(datasets)

    for i in datasets:
        diff = i['precipitation'] - mean
        i['difference'] = diff
        i['squared_diff'] = diff**2

    if plot:
        multiple_plots(
        datasets = datasets,
        name = 'difference',
        begin_long = begin_long,
        end_long = end_long,
        begin_lat = begin_lat,
        end_lat = end_lat,
        scale_global = False,
        ind_colorbar = False,
        colormap = 'coolwarm',
        label = 'Total precipitation difference (mm)',
        output = output,
        vmax = vmax,
        vmin = vmin,
        vcenter = vcenter,
        values = 'difference'
        
        )

    data_diff = []
    for i in datasets:
        i = i.assign(dataset = i.name, event = event)
        data_diff.append(i)
    data_diff = pd.concat(data_diff)
    data_diff = pd.DataFrame(data_diff)
    datat_diff = data_diff.reset_index()

    if save :
        data_diff.to_csv(output + event +'_diff.csv')