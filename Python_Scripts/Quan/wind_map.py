import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

import matplotlib.pyplot as plt
import matplotlib.colors as clr
from matplotlib.ticker import AutoMinorLocator

import pandas as pd
import numpy as np

from metpy.interpolate import interpolate_to_grid, remove_nan_observations
from metpy.units import units
from metpy.calc import wind_components

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

def making_cmap_dict(cmap):
    above_30 = cmr.get_sub_cmap(cmap, 0.60, 0.95)
    above_25 = cmr.get_sub_cmap(cmap, 0.56, 0.92)
    above_15 = cmr.get_sub_cmap(cmap, 0.5, 0.85)
    above_0 = cmr.get_sub_cmap(cmap, 0.4, 0.78)
    above_minus_10 = cmr.get_sub_cmap(cmap, 0.22, 0.7)
    above_minus_30 = cmr.get_sub_cmap(cmap, 0.12, 0.52)
    above_minus_50 = cmr.get_sub_cmap(cmap, 0.05, 0.5)
    cmap_dict = {-50: above_minus_50, -30: above_minus_30, -10: above_minus_10, 0: above_0, 15: above_15, 25: above_25,
                 30: above_30}
    return cmap_dict


'''
-----------------------------------------------------------------------------------------------------------------------
'''

'''
Retrieving, sanitizing and interpolating data
'''

# Getting the data we r interested in

df = pd.read_csv(url)

# 4 arrays of lat and lon of each weather station, the station id, the wind speed and direction at that station
# df['StnID'].values means taking all data at the column names 'StnID' (and so on)
id = df['StnID'].values
lat = df['Lat'].values
lon = df['Long'].values
wind_s = np.round_( df['AvgWindSpeed(km/h)'].values, 1 )     # Use this list to plot data point (can't use wind_speed list
                                                            # as converting cause problem for
wind_direction = df['AvgWindDirection(degrees)'].values


#
# Creating dummy data point to extend our color box
#


lon_max_index = np.argmax(lon)
lon_min_index = np.argmin(lon)
lat_max_index = np.argmax(lat)

wind_speed_at_extreme_east = wind_s[lon_max_index]
wind_speed_at_extreme_west = wind_s[lon_min_index]
wind_speed_at_extreme_north = wind_s[lat_max_index]

wind_direction_at_extreme_east = wind_direction[lon_max_index]
wind_direction_at_extreme_west = wind_direction[lon_min_index]
wind_direction_at_extreme_north = wind_direction[lat_max_index]

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

wind_s = np.append(wind_s, wind_speed_at_extreme_east)
wind_s = np.append(wind_s, wind_speed_at_extreme_west)
wind_s = np.append(wind_s, wind_speed_at_extreme_north)

wind_direction = np.append(wind_direction, wind_direction_at_extreme_east)
wind_direction = np.append(wind_direction, wind_direction_at_extreme_west)
wind_direction = np.append(wind_direction, wind_direction_at_extreme_north)

wind_speed = wind_s * units('km/h')
wind_direction = wind_direction * units.degree      # Determine degree as the unit of this data

# x projection and y projection
# convert from ccrs.LambertConformal() to ccrs.PlateCarree()
xp, yp, _ = crs.transform_points(ccrs.PlateCarree(), lon, lat).T

# Filter out the nan observations
good_indices = np.where((~np.isnan(wind_direction)) & (~np.isnan(wind_speed)))

xp = xp[good_indices]
yp = yp[good_indices]
wind_speed = wind_speed[good_indices]
wind_s = wind_s[good_indices]
wind_direction = wind_direction[good_indices]



# Getting u and v components of wind and then interpolate both.
u_wind, v_wind = wind_components(wind_speed, wind_direction)
u_wind = np.array(u_wind)
v_wind = np.array(v_wind)

# Interpolating data using barnes interpolation
# The higher the hres value is, the more points are interpolated in the grid
# search_radius is adjusted accordingly
alt_x, alt_y, data = interpolate_to_grid(xp, yp, wind_speed, minimum_neighbors=2, search_radius=240000, interp_type='barnes',
                                         hres=1000)

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

# Show the wind speed (in text) at each weather station on the plot
# Loop through the wind_s array and show it on the plot using the corresponding lat and lon
for i in range(len(wind_s) - 2):
    if (i != lon_max_index):
        plt.annotate(str(wind_s[i]), (xp[i], yp[i]), size=7)
    else:
        plt.annotate(str(wind_s[i]), (xp[i] - 200, yp[i]), size=7)

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
                                                             # coordination system) where our crs is declared above
gdf_lambert2 = geopandas.read_file(shape_file2).to_crs(crs=crs)

# Making the mask by checking if each interpolated data point falls into the polygons of the shape file or not
# Return true if a point falls into the polygons, false otherwise
# So mask is just a 2-d boolean array

# mask = shapely.vectorized.contains(gdf_lambert.dissolve().geometry.item(), alt_x, alt_y)
mask1 = shapely.vectorized.contains(gdf_lambert1.dissolve().geometry.item(), alt_x, alt_y)
mask2 = shapely.vectorized.contains(gdf_lambert2.dissolve().geometry.item(), alt_x, alt_y)
mask = np.logical_or(mask1, mask2)

# Using pcolormesh to color the area that are not masked
cf = ax.pcolormesh(alt_x, alt_y, np.where(mask, data, np.nan),
                   cmap=plt.cm.viridis)  # , norm=normalize_form plt.cm.rainbow nipy_spectral jet

# Draw barbs
ax.barbs(xp, yp, u_wind, v_wind, alpha=.5, length=5)

# Make a color bar
cb = fig.colorbar(cf, orientation='horizontal', aspect=25, shrink=0.635, pad=0.05,
                  extendrect='True')

# Set the label name and label size for the color bar
cb.set_label('km/h', size='x-large')

# Set the font size, and number of minor ticks in the color bar
cb.ax.tick_params(labelsize=8, which='both')
cb.ax.xaxis.set_minor_locator(AutoMinorLocator(3))

# The name of the plot is in the form: wind_plot_Hour-Minute_Year-Month-Day.png, where Hour-Minute_Year-Month-Day is the
# time and date the plot is made
# By changing the extension variable, we can have different types of image format. Here we choose png

plot_name = 'wind_plot'

plt.savefig(plot_name, dpi=300) # Save the plot with dpi = 300

# Uncomment the line of code below to show the plot after the code finish running
#plt.show()

'''
----------------------------------------------------------------------------------------------------------------------
'''
