import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import pandas as pd
import numpy as np

from metpy.interpolate import interpolate_to_grid, remove_nan_observations
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import shapely.vectorized
import geopandas
import cmasher as cmr
import time

'''
1. Name of the shape file being used
2. The espg number of our shape file
3. the url link where we gonna read our data from
'''
#1.
shape_file1 = 'MB_MunicipalBndrs_2015.shp'
shape_file2 = 'MB_AGregion_Perim_South.shp'
shape_file3 = 'MB_Large_Rivers.shp'

#2.
espg_number = 26914

#3.
url = 'https://mbagweather.ca/partners/agol/./hourly-data.csv'

#4.
color_to_use = 'nipy_spectral'
'''
----------------------------------------------------------------------------------------------------------------------
'''

'''
Basic set up for our plot
'''

# Set up our projection
canada_east = -95.7
canada_west = -101.38
canada_north = 52.17
canada_south = 48.85

central_lon = (canada_east + canada_west) / 2  # lon is x and lat is y
central_lat = (canada_north + canada_south) / 2

crs = ccrs.LambertConformal(central_longitude=central_lon, central_latitude=central_lat, standard_parallels=(33, 45))

'''
----------------------------------------------------------------------------------------------------------------------
'''

"""
HELPER FUNCTIONS 
"""


# This function take in a colormap cmap from matplotlib and return a dictionary of colormaps
# where each colormap in the dictionary is a subset of cmap

def making_cmap_dict(baro_press_min):
    cmap_return = cmr.get_sub_cmap(color_to_use, 0, 1)

    if baro_press_min >= 0:
        cmap_return = cmr.get_sub_cmap(color_to_use, 0.1, 0.65)
    if baro_press_min >= 10:
        cmap_return = cmr.get_sub_cmap(color_to_use, 0.25, 0.72)


    return cmap_return


'''
-----------------------------------------------------------------------------------------------------------------------
'''

'''
Retrieving, sanitizing and interpolating data
'''

# Getting the data we r interested in

df = pd.read_csv(url)

# 4 arrays of lat and lon of each weather station, and the station id and the barometric pressure at that station
# df['StnID'].values means taking all data at the column names 'StnID' (and so on)
id = df['StnID'].values
lat = df['Lat'].values
lon = df['Long'].values
baro_press = df['BarPres(hpa)'].values.astype(float)

#
# Creating dummy data point to extend our color box
#


lon_max_index = np.argmax(lon)
lon_min_index = np.argmin(lon)
lat_max_index = np.argmax(lat)

baro_press_at_extreme_east = baro_press[lon_max_index]
baro_press_at_extreme_west = baro_press[lon_min_index]
baro_press_at_extreme_north = baro_press[lat_max_index]

dummy_extreme_east_lon = lon[lon_max_index] + 0.1
dummy_extreme_east_lat = lat[lon_max_index]
dummy_extreme_west_lon = lon[lon_min_index] - 0.1
dummy_extreme_west_lat = lat[lon_min_index]
dummy_extreme_north_lon = lon[lat_max_index]
dummy_extreme_north_lat = lat[lat_max_index] + 0.4

lon = np.append(lon, dummy_extreme_east_lon)
lon = np.append(lon, dummy_extreme_west_lon)
lon = np.append(lon, dummy_extreme_north_lon)
lat = np.append(lat, dummy_extreme_east_lat)
lat = np.append(lat, dummy_extreme_west_lat)
lat = np.append(lat, dummy_extreme_north_lat)

baro_press = np.append(baro_press, baro_press_at_extreme_east)
baro_press = np.append(baro_press, baro_press_at_extreme_west)
baro_press = np.append(baro_press, baro_press_at_extreme_north)

# x projection and y projection
# convert from ccrs.LambertConformal() to ccrs.PlateCarree()
xp, yp, _ = crs.transform_points(ccrs.PlateCarree(), lon, lat).T
xp, yp, baro_press = remove_nan_observations(xp, yp, baro_press)

# Interpolating data using barnes interpolation
# The higher the hres value is, the more points are interpolated in the grid
# search_radius is adjusted accordingly
alt_x, alt_y, data = interpolate_to_grid(xp, yp, baro_press, minimum_neighbors=2, search_radius=240000,
                                         interp_type='barnes', hres=1000)

'''
Plotting the data onto our map
'''

# Create the figure and grid for subplots
fig = plt.figure(figsize=(17, 12))
ax = plt.subplot(111, projection=crs)

ax.set_extent([canada_west, canada_east, canada_south, canada_north], ccrs.PlateCarree())

# Adding province borders and country borders
provinces_bdr = cfeature.NaturalEarthFeature(category='cultural',
                                             name='admin_1_states_provinces_lines',
                                             scale='50m',
                                             linewidth=0.6,
                                             facecolor='none',
                                             )  # variable to add provinces border

country_bdr = cfeature.NaturalEarthFeature(category='cultural',
                                           name='admin_0_boundary_lines_land',
                                           scale='50m',
                                           linewidth=1.5,
                                           facecolor='none',
                                           edgecolor='k')  # variable to add country border

ax.add_feature(provinces_bdr, linestyle='--')
ax.add_feature(country_bdr, linestyle='--')

# ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)

ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS)

# Show the baro_press (in text) at each weather station on the plot

baro_press = np.round(baro_press, 0)  # Round the temperature data to 1 decimal place

# Loop through the temperature array and show it on the plot using the corresponding lat and lon
for i in range(len(baro_press) - 2):
    if (i != lon_min_index):
        plt.annotate(str(baro_press[i]), (xp[i], yp[i]), size=7)
    else:
        plt.annotate(str(baro_press[i]), (xp[i] - 1, yp[i]), size=7)

# Read the shape file and draw it on our map with cartopy
shape_feature1 = ShapelyFeature(Reader(shape_file1).geometries(), ccrs.epsg(espg_number),
                               linewidth=0.3, facecolor=(1, 1, 1, 0),
                               edgecolor=(0.5, 0.5, 0.5, 1))

shape_feature2 = ShapelyFeature(Reader(shape_file3).geometries(), ccrs.epsg(espg_number),
                               linewidth=0.05, facecolor=(np.array((152, 183, 226)) / 256),
                               edgecolor=(0.5, 0.5, 0.5, 1))
ax.add_feature(shape_feature1)
ax.add_feature(shape_feature2)

# Then read our shape file again with geopandas and making a mask with it
gdf_lambert1 = geopandas.read_file(shape_file1).to_crs(crs=crs)# Convert our shp to crs  coordinate system (lat/lon
                                                             # coordination system) where our crs is declared at line 47
gdf_lambert2 = geopandas.read_file(shape_file2).to_crs(crs=crs)

# Making the mask by checking if each interpolated data point falls into the polygons of the shape file or not
# Return true if a point falls into the polygons, false otherwise
# So mask is just a 2-d boolean array

# mask = shapely.vectorized.contains(gdf_lambert.dissolve().geometry.item(), alt_x, alt_y)
mask1 = shapely.vectorized.contains(gdf_lambert1.dissolve().geometry.item(), alt_x, alt_y)
mask2 = shapely.vectorized.contains(gdf_lambert2.dissolve().geometry.item(), alt_x, alt_y)
mask = np.logical_or(mask1, mask2)

# Get a dictionary of all color map we make using the helper function
# then we will choose what color map to use base on the current minimum barometric pressure
min_baro_press = np.min(baro_press)           # The minimum barometric pressure
cmap_dict = making_cmap_dict(min_baro_press)

cmap_to_use = cmr.get_sub_cmap(color_to_use, 0.1, 0.9)
# Using pcolormesh to color the area that are not masked, then make a color bar
cf = ax.pcolormesh(alt_x, alt_y, np.where(mask, data, np.nan),
                   cmap=cmap_to_use)
cb = fig.colorbar(cf, orientation='horizontal', aspect=25, shrink=0.635, pad=0.05,
                  extendrect='True')

# Set the label name and label size for the color bar
cb.set_label('hpa', size='x-large')

# Set the font size, and number of minor ticks in the color bar
cb.ax.tick_params(labelsize=8, which='both')
cb.ax.xaxis.set_minor_locator(AutoMinorLocator(3))

# The name of the plot is in the form: barometric_pressure_plot_Hour-Minute_Year-Month-Day.png, where Hour-Minute_Year-Month-Day is the
# time and date the plot is made
# By changing the extension variable, we can have different types of image format. Here we choose png

plot_name = 'barometric_pressure_plot'

plt.savefig(plot_name, dpi=300) # Save the plot with dpi = 300

# Uncomment the line of code below to show the plot after the code finish running
plt.show()

'''
----------------------------------------------------------------------------------------------------------------------
'''
