### from https://earthinversion.com/geophysics/pygmt-high-resolution-topographic-map-in-python/

import numpy as np 
import pygmt
import matplotlib.pyplot as plt
import pandas as pd
############
# if plot stations, need in grid_st a Dataframe with "longitude" & "latitude"

def topo_map(
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    begin_date,
    end_date,
    grid_st,
    name,
    other,
    output,
    plot = False,
    save = False,
    plot_eobs = False,
    plot_opera = False
):
    minlon, maxlon = begin_long, end_long
    minlat, maxlat = begin_lat, end_lat
    center_lon = (minlon+maxlon)/2
     
    ## take EOBS
    if plot_eobs:
        colspecs = [
        (0, 8),    # STATION
        (11, 50),   # NAME
        (54, 69),  # COUNTRY
        (87, 92), # LAT
        (96, 101),  # LON
        (104, 111), # ELEV
        (114, 124), # START
        (127,137) #STOP
        ]
        metadata = pd.read_fwf('stations_info_rr_v30.0e.txt', encoding='latin-1', header = 0, colspecs = colspecs) #read the txt of E-OBS stations location
        metadata['START'] = pd.to_datetime(metadata['START'])
        
        metadata['STOP'] = pd.to_datetime(metadata['STOP'], format = 'mixed')
        
        begin_date = pd.to_datetime(begin_date) #6UTC the day before until 6UTC 
        end_date = pd.to_datetime(end_date)
        
        
        # Filter dates
        valid_dates = ( metadata['STOP']>= begin_date) & (metadata['START'] <= end_date)
        
        # Filter latitude and longitude
        valid_lat = (metadata['LAT'] >= begin_lat) & (metadata['LAT'] <= end_lat)
        valid_lon = (metadata['LON'] >= begin_long) & (metadata['LON'] <= end_long)
        
        combined_condition = valid_dates & valid_lat & valid_lon
        
        # Apply the filter to create a new DataFrame
        filtered_metadata = metadata[combined_condition]
    
        
        lons = filtered_metadata['LON']
        lats = filtered_metadata['LAT']
        
    if plot_opera:
        df_opera = pd.read_pickle('/home/adelaly/BA_work/raw_data/OPERA_loc.pkl') #read the pkl file with opera location

        df_opera['startyear'] = pd.to_datetime(df_opera['startyear'])
        valid_dates = (df_opera['startyear'] <= begin_date)

        valid_lat = (pd.to_numeric(df_opera['latitude']) >= begin_lat) & (pd.to_numeric(df_opera['latitude']) <= end_lat)
        valid_lon = (pd.to_numeric(df_opera['longitude']) >= begin_long) & (pd.to_numeric(df_opera['longitude']) <= end_long)

        combined_cond = valid_dates & valid_lat & valid_lon
        filtered_opera = df_opera[combined_cond]
        long = pd.to_numeric(filtered_opera['longitude'])
        lat = pd.to_numeric(filtered_opera['latitude'])

    
    # Initialize figure
    fig = pygmt.Figure()
    pygmt.makecpt(cmap="geo", series=[-500, 4500])
    # Define region (e.g., Europe)
    region = [begin_long, end_long, begin_lat, end_lat]  # West, East, South, North
    
    # Plot high-res relief (ETOPO1) with hillshading
    fig.grdimage(
        grid="@earth_relief_30s",  # 5 arc-minute resolution
        region=region,
        projection="L"+str(center_lon)+"/45/30/60/8i",  # Plates carre Conformal
        shading=True  # Hillshading effect
           # Color palette
        #frame=True,    # Enable frame (customized below)
    )
    
    # Customize frame (black only, no fill)
    with pygmt.config(FONT_ANNOT_PRIMARY="17p"):  # Change "14p" to your desired font size
        fig.basemap(
            frame=["a", "g", "WSne"],  # Annotated borders
        )
    
    # Add land borders (country boundaries)
    fig.coast(
        borders=["1/2p,black"],  # Country borders (1=level, 0.5p=thickness)
        lakes="blue",              # Color for lakes
        shorelines="0.5p,black",   # Coastlines
    )
    
    
    # plot data points
    
    if plot:
        fig.plot(
            x=grid_st['longitude'],
            y=grid_st['latitude'], 
            style='i0.17i', 
            fill='#ff66cc', 
            pen='black', 
            label= other + ' stations',
            )
    if plot_opera:
        fig.plot(
            x=long,
            y=lat, 
            style='d0.25i', 
            fill='#ccff00', 
            pen='black', 
            label='OPERA stations',
            )
    if plot_eobs:
        fig.plot(
            x=lons,
            y=lats, 
            style='c0.15i', 
            fill='#E10600', 
            pen='black', 
            label='E-OBS stations',
            )
    with pygmt.config(FONT_ANNOT_PRIMARY="20p", FONT_LABEL = "20p"):
        fig.legend()
    with pygmt.config(FONT_ANNOT_PRIMARY="12p", FONT_LABEL = "20p"):
        fig.colorbar(frame=["a500f4000","x+lElevation","y+lm"])
    fig.show()
    if save: 
        fig.savefig(output + name + "_topographic.png", crop=True, dpi=500)
        fig.savefig(output + name + "_topographic.pdf")