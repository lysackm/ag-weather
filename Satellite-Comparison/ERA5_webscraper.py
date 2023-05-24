# This file is sourced from https://confluence.ecmwf.int/display/CKB/How+to+convert+NetCDF+to+CSV and is a program that
# automatically sends a request to the conpernicus server with a request for ERA5-Land data. It then retrieves said data
#
# To get or modify the json request body, you are able to get examples of the api body by going to the conpernicus
# website, building a query, then select "Show API request" in the bottom left corner. You can follow or modify this to
# get the requests body.
# To install the cdsapi library you will need a config file called .cdsapirc containing something similar to below. You
# are able to get your UID and API key from this link: https://cds.climate.copernicus.eu/user. I had to refresh it
# before I was able to get the key properly. (Maybe clearing caches helps)
# source: https://pypi.org/project/cdsapi/

# url: https://cds.climate.copernicus.eu/api/v2
# key: <UID>:<API key>
# verify: 1


import cdsapi
import netCDF4
from netCDF4 import num2date
import numpy as np
import os
import pandas as pd


# variables is the name that it is in the database, specific and well known
variables = ['2m_temperature', 'soil_temperature_level_1',
            'soil_temperature_level_2', 'soil_temperature_level_3', 'surface_solar_radiation_downwards',
            'total_precipitation', 'volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2',
            'volumetric_soil_water_layer_3', '10m_v_component_of_wind', '10m_u_component_of_wind']
# variable =  # used to download single attribute


# attr_names are the name that the file will be called, arbitrary
attr_names = ['t2m', 'st1', 'st2', 'st3', 'rad', 'totprec', 'sw1', 'sw2', 'sw3', 'v10m', 'u10m']
# attr_names = [] # used to download single attribute

# what years need to be downloaded
years = ['2018', '2019', '2020', '2021', '2022']


for variable, attr_name in zip(variables, attr_names):
    for year in years:
        # Retrieve data and store as netCDF4 file
        c = cdsapi.Client()
        file_location = './' + attr_name + year + '.nc.zip'
        c.retrieve(
            'reanalysis-era5-land',
            {
                'variable': variable,
                'year': year,
                'month': [
                    '01', '02', '03',
                    '04', '05', '06',
                    '07', '08', '09',
                    '10', '11', '12',
                ],
                'day': [
                    '01', '02', '03',
                    '04', '05', '06',
                    '07', '08', '09',
                    '10', '11', '12',
                    '13', '14', '15',
                    '16', '17', '18',
                    '19', '20', '21',
                    '22', '23', '24',
                    '25', '26', '27',
                    '28', '29', '30',
                    '31',
                ],
                'time': [
                    '00:00', '01:00', '02:00',
                    '03:00', '04:00', '05:00',
                    '06:00', '07:00', '08:00',
                    '09:00', '10:00', '11:00',
                    '12:00', '13:00', '14:00',
                    '15:00', '16:00', '17:00',
                    '18:00', '19:00', '20:00',
                    '21:00', '22:00', '23:00',
                ],
                'area': [
                    52.34, -102.03, 49,
                    -95,
                ],
                'format': 'netcdf.zip',
            },
            file_location)
