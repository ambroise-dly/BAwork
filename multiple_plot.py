import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import matplotlib.colors as colors
import numpy as np

def multiple_plots_comparison(
    output,
    original_datasets,
    regridded_datasets,
    name,
    begin_long,
    end_long,
    begin_lat,
    end_lat,
    label,
    values,
    scale_global=False,
    colormap=None,
    vmin=None,
    vmax=None,
    vcenter=None
):
    """
    Generates a 3x4 plot comparing original and regridded datasets with refined layout.

    """

    
    # Define the colors and their positions if no colormap is provided
    if colormap is None:
        color = [
            (1.0, 1.0, 1.0),      # White for 0.3 mm
            (0.9, 1.0, 0.9),      # Very light green for 2 mm
            (0.7, 1.0, 0.9),      # Pastel cyan for 5 mm
            (0.5, 1.0, 0.8),      # Pastel green for 10 mm
            (0.3, 0.8, 1.0),      # Pastel blue for 20 mm
            (0.0, 0.5, 1.0),      # Dark blue for 35 mm
            (0.0, 0.0, 0.8),      # Darker blue for 50 mm
            (0.5, 0.0, 0.5),      # Dark red for 70 mm
            (0.8, 0.0, 0.0),      # Dark red for 90 mm
            (1.0, 0.5, 0.0),      # Pastel orange for 120 mm
            (1.0, 0.7, 0.3),      # Lighter pastel orange for 150 mm
            (1.0, 0.8, 0.5),      # Very light pastel orange for 180 mm
        ]
        cmap = LinearSegmentedColormap.from_list("custom_colormap", color)
    else:
        cmap = colormap

    # Set the projection
    projection = ccrs.LambertConformal(central_longitude=10, central_latitude=50)
    extent = [begin_long, end_long, begin_lat, end_lat]

    # Pivot the datasets and prepare titles
    all_data = []
    titles = []
    num_datasets = len(original_datasets)
    for i in range(num_datasets):
        original = original_datasets[i].pivot_table(index="latitude", columns="longitude", values=values)
        regridded = regridded_datasets[i].pivot_table(index="latitude", columns="longitude", values=values)
        all_data.extend([original, regridded])
        titles.append(f"({chr(ord('a') + 2*i)}) {original_datasets[i].name} original")
        titles.append(f"({chr(ord('b') + 2*i)}) {regridded_datasets[i].name} regridded")

    # Determine global scaling if requested
    if scale_global:
        all_values = [df.values.flatten() for df in all_data]
        global_min = np.nanmin(np.concatenate(all_values))
        global_max = np.nanmax(np.concatenate(all_values))
        if vcenter is not None and global_min < vcenter < global_max:
            norm = TwoSlopeNorm(vmin=global_min, vcenter=vcenter, vmax=global_max)
        else:
            norm = colors.Normalize(vmin=global_min, vmax=global_max)
    else:
        norm = None

    # Set up the figure and grid layout (3 rows, 4 columns)
    fig = plt.figure(figsize=(37, 32)) # Adjust figure size for better aspect
    gs = fig.add_gridspec(3, 5, width_ratios=[1, 1, 0.025, 1,1], hspace=0.001) # Adjust wspace and hspace

    axes = []
    for i in range(3):
        for j in range(5):
            # Adjust column spacing for the gap
            if j == 2:
                ax = fig.add_subplot(gs[i, j])
                ax.axis('off')
            else:
                ax = fig.add_subplot(gs[i, j], projection=projection)
            axes.append(ax)

    # Create the plots
    for i, (df, title) in enumerate(zip(all_data, titles)):

        if i == 0 or i == 1:
            ax = axes[i]
        if i == 2 or i == 3 or i == 4 or i == 5:
            ax = axes[i+1]
        if i == 6 or i == 7 or i == 8 or i == 9:
            ax = axes[i+2]
        if i == 10 or i == 11:
            ax = axes[i+3]
        lon, lat = np.meshgrid(df.columns, df.index)

        if norm is not None and scale_global:
            mesh = ax.pcolormesh(lon, lat, df.values, cmap=cmap, transform=ccrs.PlateCarree(), norm=norm)
        elif vmin is not None and vmax is not None:
            if vcenter is not None and vmin < vcenter < vmax:
                current_norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
            else:
                current_norm = colors.Normalize(vmin=vmin, vmax=vmax)
            mesh = ax.pcolormesh(lon, lat, df.values, cmap=cmap, transform=ccrs.PlateCarree(), norm=current_norm)
        else:
            mesh = ax.pcolormesh(lon, lat, df.values, cmap=cmap, transform=ccrs.PlateCarree())

        ax.set_title(' ' + title, loc='left',y = 0.94, fontsize=28,fontweight='extra bold') # Title on top left, larger font
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.set_extent([begin_long, end_long, begin_lat, end_lat], crs=ccrs.PlateCarree())
        if i%2 == 0:
            gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
        else:
            gl = ax.gridlines(draw_labels=False, linestyle='--', alpha=0.5)
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 23}
        gl.ylabel_style = {'size': 23}

    # Add a single colorbar at the bottom
    cbar_ax = fig.add_axes([0.35, 0.05, 0.3, 0.02]) # [left, bottom, width, height]
    cbar = fig.colorbar(mesh, cax=cbar_ax, orientation='horizontal', label=label)
    cbar.set_label(label, fontsize=37, labelpad = -160) # Larger label font
    cbar.ax.tick_params(labelsize=35) # Larger tick font

    
    plt.savefig(output + name, dpi=300, bbox_inches='tight')
    plt.savefig(output + name + '.pdf', bbox_inches='tight')
    plt.show()