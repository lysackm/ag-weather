# simple program that parses a netCDF file from the ERA5-Land files.
# Prints one coordinate's worth of data. Uses for testing and getting
# human-readable data.

import netCDF4
from netCDF4 import num2date
import os
import pandas as pd
import xarray as xr

attributes = {}

file_location = './data.nc'
variable = 'ssrd'
output_location = './single_table.csv'

da = xr.open_dataarray(file_location)
print(da.dims)

# select all data for the point (49.8, -97.63)
da = da.loc[:, 49.8, -97.63]

df = da.to_pandas()
df.to_csv(output_location)
