import traceback
from datetime import date, timedelta
from math import sqrt

from numpy import atan, pi

import xarray as xr
import pandas as pd
import numpy as np

# years which the analysis will be done
years = [2018, 2019, 2020, 2021, 2022]

# column names for manitoba weather station data
stn_attrs = ['AvgAir_T', 'AvgWS', 'RH', 'Soil_TP5_TempC', 'Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC',
             'SolarRad', ['TBRG_Rain', 'Pluvio_Rain'], 'Soil_TP5_VMC', 'Soil_TP20_VMC',
             ['Soil_TP50_VMC', 'Soil_TP100_VMC']]

# attribute names for era5
era5_attrs = ['t2m', ['v10m', 'u10m'], None, 'st1', 'st2', 'st3', None, 'rad', 'totprec', 'sw1', 'sw2', 'sw3']
# attribute names for merra2
merra_attrs = ["T2M", ["V10M", "U10M"], "QV2M", "TSOIL1", "TSOIL2", "TSOIL3", "TSOIL4", "SWGDN", "PRECTOTLAND",
               "GWETTOP", "GWETROOT", "GWETPROF"]

# attribute names for merra broken down by database
M2T1NXSLV = ["T2M", ["V10M", "U10M"], "QV2M"]
M2T1NXLND = ["TSOIL1", "TSOIL2", "TSOIL3", "TSOIL4", "PRECTOTLAND", "GWETPROF", "GWETROOT", "GWETTOP"]
M2T1NXRAD = ["SWGDN"]


# attribute is assumed to be the name of the merra_attr
def get_merra_filename(date, attribute):
    folder = ""
    tag = ""
    if attribute in M2T1NXSLV:
        folder = "M2T1NXSLV"
        tag = "slv"
    elif attribute in M2T1NXLND:
        folder = "M2T1NXLND"
        tag = "lnd"
    elif attribute in M2T1NXRAD:
        folder = "M2T1NXRAD"
        tag = "rad"

    # format date
    date_str = date.strftime("%Y%m%d")

    return "merra/" + folder + "/MERRA2_400.tavg1_2d_" + tag + "_Nx." + date_str + ".SUB.nc"


# Assumed it is an attribute from the era5_attr list
def get_era_filename(year, attribute):
    return "conpernicus/ERA5-Land/" + attribute + str(year) + "/data.nc"


# returns file name for station data for our station data
def get_stn_filename(year):
    return "station-csv/MBAg-60min-" + str(year) + ".csv"


def merra_time_array(date):
    times = []
    for i in range(0, 24):
        times.append(date.isoformat() + "T%.2f:00:00" % i)
    return times


def era5_time_array(date):
    times = []
    for i in range(1, 24):
        times.append(date.isoformat() + "T%.2f:00:00" % i)
    tomorrow = date + timedelta(days=1)
    times.append(tomorrow.isoformat() + "T00:00:00")
    return times


# creates duplicates each name of each station in station_names
# 24 times in a row in an array and returns said array. Used to
# make an array that is able to be mapped to the final array which
# will have 24 rows for each station
def location_names():
    mapping = []
    for name in station_names:
        for x in range(24):
            mapping.append(name)

    return mapping


# Averages the merra data so that it is taking centered readings around
# the hour mark, instead of averaging over an hour.
def avg_merra_data(merra_data, start_date, end_date):
    end_date = end_date + timedelta(hours=-1)
    merra_data = merra_data.interp(
        time=pd.date_range(start_date, end_date, periods=24),
        kwargs={"fill_value": "extrapolate"})
    return merra_data


# Used to align the timescale for the merra_data to be inline with
# the other time scales, ie era5 and station data. Sets the time to
# be the end of the averaged time. That is to add 30 minutes to the
# recorded time stamp
# TODO this should be at the end of the time, since our weather station data is of the past hour
def shift_merra_timescale(merra_data):
    merra_data['time'] = pd.to_datetime(merra_data['time']) + timedelta(hours=0.5)
    return merra_data


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


# given two vectorized components of wind which are perpendicular
# to each other find the wind direction in degrees
def wind_vector_to_direction(u, v):
    if v > 0:
        return (180 / pi) * atan(u / v) + 180
    if u < 0 & v < 0:
        return (180 / pi) * atan(u / v) + 0
    if u > 0 & v < 0:
        return (180 / pi) * atan(u / v) + 360


# given two vectorized components of wind which are perpendicular
# to each other find the scalar wind speed
def wind_vector_to_scalar(u, v):
    # is this fast?
    return sqrt(np.power(u, 2) + np.power(v, 2))


# takes in watts per meter squared and need to multiplied by the time
# elapsed measured in seconds. That is 1 hour = 60 * 60 = 3600 seconds
def watts_to_millijoules(wm2):
    return float(wm2 * 3600) * 1000


# is actually used for joules per meter squared but the conversion
# is the same
def joules_to_millijoules(j):
    return j * 1000


def meters_to_mm(m):
    return m * 1000


# mapping of attribute names to correct conversion function
# special cases (like wind, which reads two columns at a time)
# are not included
conversions = {
    "t2m": kelvin_to_celsius,
    "st1": kelvin_to_celsius,
    "st2": kelvin_to_celsius,
    "st3": kelvin_to_celsius,
    "rad": joules_to_millijoules,
    "totprec": meters_to_mm,
    "TM": kelvin_to_celsius,
    "TSOIL1": kelvin_to_celsius,
    "TSOIL2": kelvin_to_celsius,
    "TSOIL3": kelvin_to_celsius,
    "TSOIL4": kelvin_to_celsius,
    "SWGDN": watts_to_millijoules,
    "PRECTOTLAND": meters_to_mm,
}


stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

# lat and long are pairs of the stations latitude and longitude
# coordinates. Each list is in order so that if you access index
# i of each array then it will be the coordinate for the ith
# weather station
lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

# plain text names for all the stations in order. Each index is
# will be the same as the index mapping in lat and long
station_names = stn_metadata['StationName'].tolist()

# index to have the correct plaintext station name for every row
station_index = location_names()

# An array which holds metadata that is not recorded in the hourly
# table.
# Includes name, id (station number), longitude, and latitude
stn_metadata = stn_metadata[['StationName', 'LongDD', 'LatDD', 'SN']]
stn_metadata = stn_metadata.rename(columns={"StationName": "Station", "SN": "location", "TMSTAMP": "time"})
stn_metadata["Station"] = stn_metadata["Station"].apply(lambda x: x.lower().strip().replace('.', '').replace(' ', ''))
stn_metadata["location"] = stn_metadata["location"] - 1

# relative directory for where data is being held on this machine.
# outside this GitHub repo. Change if needed
data_dir = "../../../../data/"


# loop through the named attributes of each of the different file types
# all the attributes should be a mapping to each other.
for stn_attr, era5_attr, merra_attr in zip(stn_attrs, era5_attrs, merra_attrs):
    for year in years:

        # era5 has files per attribute per year
        if isinstance(era5_attr, str) and era5_attr is not None:
            era5_file = get_era_filename(year, era5_attr)
            # data array since 1 attribute per file
            era5_da = xr.open_dataarray(data_dir + era5_file)
            # print(data_dir + era5_file)
        else:
            # print("This is a special case")
            str("do nothing")

        # station data is per year
        if isinstance(stn_attr, str) and stn_attr is not None:
            stn_file = get_stn_filename(year)
            stn_df = pd.read_csv(data_dir + stn_file)
            stn_df = stn_df.rename(columns={"TMSTAMP": "time"})
        else:
            # print("This is a special case")
            str("do nothing")

        # initialize the start and end date
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = end_date.strftime("%Y%m%d")
        time_delta = end_date - start_date

        for i in range(time_delta.days + 1):
            day = start_date + timedelta(days=i)
            merra_data = []
            timestamp_today = pd.Timestamp(day + timedelta(hours=1))
            timestamp_tomorrow = pd.Timestamp(day + timedelta(days=1))

            # handling one chunk of data written to the csv
            try:
                if isinstance(era5_attr, str) and era5_attr is not None:  # standard cases
                    merra_file = get_merra_filename(day, merra_attr)

                    # data set since multiple attributes per file
                    merra_ds = xr.open_dataset(data_dir + merra_file)

                    merra_times = merra_time_array(day)
                    merra_data = merra_ds.sel(lon=long, lat=lat, time=merra_times, method="nearest")
                    merra_data = merra_data[merra_attr]
                    # merra_data = avg_merra_data(merra_data, timestamp_today, timestamp_tomorrow)
                    merra_data = shift_merra_timescale(merra_data)
                    # print(merra_data)

                elif era5_attr is not None:  # special cases
                    str("handle array as input")

                else:  # missing data
                    continue
            except Exception as e:
                print(e)
                # traceback.print_exc()

            era5_times = era5_time_array(day)
            era5_data = era5_da.sel(longitude=long, latitude=lat, time=era5_times, method="nearest")
            # print(era5_data.time)

            try:
                stn_data = stn_df[["StnID", "time", "Station", stn_attr]]
                stn_data["time"] = pd.to_datetime(stn_data["time"])
                # TODO where I left off
                stn_data["time"] = stn_data["time"] + pd.DateOffset(hours=-1)
                stn_data = stn_data[(stn_data["time"] >= timestamp_today) & (stn_data["time"] < timestamp_tomorrow)]
                stn_data = stn_data.merge(stn_metadata, on=["Station"], how="left")
                # print(stn_data)
            except Exception as e:
                print(e)

            # print(stn_data)
            # flattening arrays to be 1 dimensional
            # merra_stacked = merra_data.stack(z=("location", "time"))
            # merra_stacked_np = merra_stacked.to_numpy()
            # merra_stacked_np = merra_stacked_np - 273.15

            era5_df = era5_data.to_dataframe()
            # conversions.get(merra_attr, lambda x: x)
            era5_df = era5_df.rename(
                columns={"latitude": "era5_lat", "longitude": "era5_long", "t2m": "era5_" + stn_attr})

            merra_df = merra_data.to_dataframe()
            merra_df = merra_df.rename(columns={"lat": "merra_lat", "lon": "merra_lon", "T2M": "merra_" + stn_attr})

            stn_data = stn_data.rename(columns={"LatDD": "stn_lat", "LongDD": "stn_long", stn_attr: "stn_" + stn_attr})

            merged_df = era5_df.merge(merra_df, on=["location", "time"], how="outer")
            merged_df = merged_df.merge(stn_data, on=["location", "time"], how="left")
            merged_df.to_csv("./testing.csv")
            stn_data.to_csv("./stn.csv")

            # era5_stacked = era5_data.stack(z=("location", "time"))
            # era5_stacked_np = era5_stacked.to_numpy()
            # era5_stacked_np = era5_stacked_np - 273.15

            # should try using xarray combine or merge
            era5_data = era5_data.rename({'latitude': 'lat', 'longitude': 'lon'})
            # joined_xr = xr.combine_by_coords([era5_data, merra_data], coords=['lat', 'lon'], compat='override')
            # joined_xr = joined_xr.rename({era5_attr: "era5_" + stn_attr, merra_attr: "merra_" + stn_attr})
            # print(joined_xr.merra_AvgAir_T - joined_xr.era5_AvgAir_T)
            # print(joined_xr.lon)

            # stacked = joined_xr.stack(z=("location", "time"))
            # print(stacked - 273.15)

            # print("era", era5_stacked_np)
            # print("merra", merra_stacked_np)

            # joined_np = np.vstack((merra_stacked_np, era5_stacked_np, station_index)).T
            # joined_df = pd.DataFrame(joined_np, columns=['era5', 'merra', 'location'])
            # print(joined_xr)

            # https://stackoverflow.com/questions/72179103/xarray-select-the-data-at-specific-x-and-y-coordinates

            # station_data = db.select(select date, StnID, StationName, Latitude, Longitude, Elevation, attribute
            #           where date > date_start and date < date_end)

            # https://docs.xarray.dev/en/stable/generated/xarray.merge.html

            # mbagweather.ca/historical/CSV/
            # would have to dump 6 months or so of 2022

            # AC data
