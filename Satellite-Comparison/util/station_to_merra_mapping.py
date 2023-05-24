# Program used to create input for the merra_scraping program. Its purpose is to find all the weather stations that
# map to all the same grid spaces using the Merra data resolution. The output is a printed line of size 3 tuples that
# in the format ('station names', lat, long). The output can be moved into a modified version of merra_scraping that
# downloads data for every one of those locations. The methods are taken directly from merra_scraping.py, used to create
# the mapping between real coordinates and the merra grid.

import numpy as np
import pandas as pd


# Translate lat/lon into coordinates that MERRA-2 understands
def translate_lat_to_geos5_native(latitude):
    """
    The source for this formula is in the MERRA2
    Variable Details - File specifications for GEOS pdf file.
    The Grid in the documentation has points from 1 to 361 and 1 to 576.
    The MERRA-2 Portal uses 0 to 360 and 0 to 575.
    latitude: float Needs +/- instead of N/S
    """
    return ((latitude + 90) / 0.5)


def translate_lat_to_geos5_native_back(latitude):
    """
    The source for this formula is in the MERRA2
    Variable Details - File specifications for GEOS pdf file.
    The Grid in the documentation has points from 1 to 361 and 1 to 576.
    The MERRA-2 Portal uses 0 to 360 and 0 to 575.
    latitude: float Needs +/- instead of N/S
    """
    return ((latitude * 0.5) - 90)


def translate_lon_to_geos5_native(longitude):
    """See function above"""
    return ((longitude + 180) / 0.625)


def translate_lon_to_geos5_native_back(longitude):
    """See function above"""
    return ((longitude * 0.625) - 180)


def find_closest_coordinate(calc_coord, coord_array):
    """
    Since the resolution of the grid is 0.5 x 0.625, the 'real world'
    coordinates will not be matched 100% correctly. This function matches
    the coordinates as close as possible.
    """
    # np.argmin() finds the smallest value in an array and returns its
    # index. np.abs() returns the absolute value of each item of an array.
    # To summarize, the function finds the difference closest to 0 and returns
    # its index.
    index = np.abs(coord_array - calc_coord).argmin()
    return coord_array[index]


lat_coords = np.arange(0, 361, dtype=int)
lon_coords = np.arange(0, 576, dtype=int)

# load station metadata into a dataframe
df = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
count = 0
# dict is a variables that have keys equal to coord in the merra grid, and a value of all the stations in those coord
coord_dict = {}

for index, station in df.iterrows():
    if station["SN"] < 109:
        # in my case I don't want any stations made after 2018
        lat = station["LatDD"]
        lon = station["LongDD"]

        # get coordinate and translate it to merra style coord
        lat_coord = translate_lat_to_geos5_native(lat)
        lon_coord = translate_lon_to_geos5_native(lon)

        lat_closest = translate_lat_to_geos5_native_back(find_closest_coordinate(lat_coord, lat_coords))
        lon_closest = translate_lon_to_geos5_native_back(find_closest_coordinate(lon_coord, lon_coords))

        # if new coord on the grid, add it, otherwise append to the string
        if (lat_closest, lon_closest) not in coord_dict.keys():
            coord_dict[(lat_closest, lon_closest)] = []
        coord_dict[(lat_closest, lon_closest)].append(station["StationName"])

# Print the results in a format that can be copied into code.
print("\n\n")
for key in coord_dict.keys():
    names = ""
    for name in coord_dict[key]:
        names = names + name + " "
    names = names.strip()
    print("('" + names + "', " + str(key[0]) + ", " + str(key[1]) + "), ", end="")

