import glob
import os
from datetime import date, timedelta, datetime
from numpy import arctan, pi
import xarray as xr
import pandas as pd
import pytz
from pytz.exceptions import NonExistentTimeError, AmbiguousTimeError

pd.options.mode.chained_assignment = None  # default='warn'

# years which the analysis will be done
years = [2018, 2019, 2020, 2021, 2022]

# column names for manitoba weather station data
# stn_attrs = ['AvgAir_T', 'AvgWS', 'RH', 'Soil_TP5_TempC', 'Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC',
#              'SolarRad', ['TBRG_Rain', 'Pluvio_Rain'], 'Soil_TP5_VMC', 'Soil_TP20_VMC',
#              ['Soil_TP50_VMC', 'Soil_TP100_VMC'], "Press_hPa"]
#
# # attribute names for era5
# era5_attrs = ['t2m', ['v10m', 'u10m'], None, 'stl1', 'stl2', 'stl3', 'ssrd', 'tp', 'swvl1', 'swvl2', 'swvl3',
#               'sp', 'd2m']
# # attribute names for merra2
# merra_attrs = ["T2M", ["V10M", "U10M"], "QV2M", "TSOIL1", "TSOIL2", "TSOIL3", "TSOIL4", "SWGDN", "PRECTOTLAND",
#                "SFMC", "RZMC", "PRMC", "PS", "T2MDEW"]


# For testing purposes
stn_attrs = ['Soil_TP5_VMC']
era5_attrs = ['swvl1']
merra_attrs = ["SFMC"]


# attribute names for merra broken down by database
# _2 folders were there since they were added outside the
# original data scope and had to be downloaded later
M2T1NXSLV = ["T2M", ["V10M", "U10M"], "QV2M"]
M2T1NXSLV_2 = ["PS", "T2MDEW"]
M2T1NXLND = ["TSOIL1", "TSOIL2", "TSOIL3", "TSOIL4", "PRECTOTLAND"]
M2T1NXLND_2 = ["SFMC", "RZMC", "PRMC"]
M2T1NXRAD = ["SWGDN"]


# attribute is assumed to be the name of the merra_attr
def get_merra_filename(cur_date, attribute):
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
    elif attribute in M2T1NXSLV_2:
        folder = "M2T1NXSLV-2"
        tag = "slv"
    elif attribute in M2T1NXLND_2:
        folder = "M2T1NXLND-2"
        tag = "lnd"

    # format date
    date_str = cur_date.strftime("%Y%m%d")

    return "merra/" + folder + "/MERRA2_400.tavg1_2d_" + tag + "_Nx." + date_str + ".SUB.nc"


# Assumed it is an attribute from the era5_attr list
def get_era_filename(year, attribute):
    return "conpernicus/ERA5-Land/" + attribute + str(year) + "/data.nc"


# returns file name for station data for our station data
def get_stn_filename(year):
    return "station-csv/MBAg-60min-" + str(year) + ".csv"


def merra_time_array(cur_date):
    times = []
    for i in range(0, 24):
        times.append(cur_date.isoformat() + "T%.2f:00:00" % i)
    return times


def era5_time_array(cur_date):
    times = []
    for i in range(1, 24):
        times.append(cur_date.isoformat() + "T%.2f:00:00" % i)
    tomorrow = cur_date + timedelta(days=1)
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
def shift_merra_timescale(merra_data):
    merra_data['time'] = pd.to_datetime(merra_data['time']) + timedelta(hours=0.5)
    return merra_data


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


# given two vectorized components of wind which are perpendicular
# to each other find the wind direction in degrees
def wind_vector_to_direction(v, u):
    if v > 0:
        return (180 / pi) * arctan(u / v) + 180
    if u < 0 & v < 0:
        return (180 / pi) * arctan(u / v) + 0
    if u > 0 & v < 0:
        return (180 / pi) * arctan(u / v) + 360


# given two vectorized components of wind which are perpendicular
# to each other find the scalar wind speed
def wind_vector_to_scalar(v, u, v_col, u_col):
    # is this fast?
    v[v_col] = (v[v_col] ** 2 + u[u_col] ** 2) ** (1/2)
    v = v.rename(columns={v_col: "AvgWS"})
    return v


# takes in watts per meter squared and need to multiplied by the time
# elapsed measured in seconds. That is 1 hour = 60 * 60 = 3600 seconds
def watts_to_megajoules(wm2):
    return float(wm2 * 3600) / 1000000.0


# is actually used for joules per meter squared but the conversion
# is the same
def joules_to_megajoules(j):
    return j / 1000000.0


def meters_to_mm(m):
    return m * 1000


def pa_to_hpa(pa):
    return pa / 100.0


def decimal_to_percent(dec):
    return dec * 100


# mapping of attribute names to correct conversion function
# special cases (like wind, which reads two columns at a time)
# are not included
conversions = {
    "t2m": kelvin_to_celsius,
    "stl1": kelvin_to_celsius,
    "stl2": kelvin_to_celsius,
    "stl3": kelvin_to_celsius,
    "ssrd": joules_to_megajoules,
    "tp": meters_to_mm,
    "d2m": kelvin_to_celsius,
    "sp": pa_to_hpa,
    "swvl1": decimal_to_percent,
    "swvl2": decimal_to_percent,
    "swvl3": decimal_to_percent,
    "T2M": kelvin_to_celsius,
    "TSOIL1": kelvin_to_celsius,
    "TSOIL2": kelvin_to_celsius,
    "TSOIL3": kelvin_to_celsius,
    "TSOIL4": kelvin_to_celsius,
    "SWGDN": watts_to_megajoules,
    "PRECTOTLAND": meters_to_mm,
    "T2MDEW": kelvin_to_celsius,
    "PS": pa_to_hpa,
    "SFMC": decimal_to_percent,
    "RZMC": decimal_to_percent,
    "PRMC": decimal_to_percent,
}


def stn_metadata_preprocessing(stn_meta):
    stn_meta = stn_meta[['StationName', 'LongDD', 'LatDD', 'SN', "Elevation"]]
    stn_meta = stn_meta.rename(columns={
        "StationName": "Station",
        "SN": "location",
        "TMSTAMP": "time",
        "Elevation": "elevation"})
    stn_meta["Station"] = stn_meta["Station"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))
    stn_meta["location"] = stn_meta["location"] - 1
    return stn_meta


def load_era5_wind_data(era5_attr, year):
    v_file = get_era_filename(year, era5_attr[0])
    u_file = get_era_filename(year, era5_attr[1])

    v_da = xr.open_dataarray(data_dir + v_file)
    u_da = xr.open_dataarray(data_dir + u_file)

    return [v_da, u_da]


# load era5 data from the file and return a xarray data array
def load_era5_data(era5_attr, year):
    # era5 has files per attribute per year
    if isinstance(era5_attr, str) and era5_attr is not None:
        era5_file = get_era_filename(year, era5_attr)
        # data array since 1 attribute per file
        era5_da = xr.open_dataarray(data_dir + era5_file)
        return era5_da
    else:
        # handle special cases
        if era5_attr[0] == "v10m":
            return load_era5_wind_data(era5_attr, year)


# TODO this isnt necessarily complete. For instance what if a station got a pluvio station during the middle of the year
# It would select pluvio still even thought it would have bad data for half of the year. Not sure what the best way to
# do this is.
def get_rain_column(stn_df, year):
    start_time = datetime.strptime(str(year) + "-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(str(year) + "-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")
    # Pluvio_Rain is preferable to TBRG_Rain
    # stn_data = stn_data[(stn_data["time"] >= early_bound) & (stn_data["time"] < late_bound)]
    year_df = stn_df[(stn_df["time"] >= start_time) & (stn_df["time"] < end_time)]
    pluvio = year_df["Pluvio_Rain"].sum()
    tbrg_rain = year_df["TBRG_Rain"].sum()

    if pluvio != 0:
        return "Pluvio_Rain"
    elif tbrg_rain != 0:
        return "TBRG_Rain"
    else:
        print("no precipitation values for all years, something is probably broken. Sorry!")
        exit(1)


# load station data from the csv and return it as a dataframe
def load_stn_data(year):
    # station data is per year

    stn_file = get_stn_filename(year)
    stn_df = pd.read_csv(data_dir + stn_file, na_values="\\N")
    stn_df = stn_df.rename(columns={"TMSTAMP": "time"})
    stn_df["time"] = pd.to_datetime(stn_df["time"])
    return stn_df


def load_merra_wind_data(merra_attr, merra_data):
    merra_data = shift_merra_timescale(merra_data)

    v_df = merra_data[merra_attr[0]].to_dataframe()
    u_df = merra_data[merra_attr[1]].to_dataframe()

    merra_df = wind_vector_to_scalar(v_df, u_df, "V10M", "U10M")
    return merra_df


# load and return a singular days worth of merra data of attribute
# merra_attr
def load_merra_data(merra_attr, day, stn_attr):
    try:
        merra_file = get_merra_filename(day, merra_attr)
        # data set since multiple attributes per file
        merra_ds = xr.open_dataset(data_dir + merra_file)

        merra_times = merra_time_array(day)
        merra_data = merra_ds.sel(lon=long, lat=lat, time=merra_times, method="nearest")

        if isinstance(merra_attr, str) and merra_attr is not None:  # standard cases
            merra_data = merra_data[merra_attr]
            merra_data = shift_merra_timescale(merra_data)
            merra_df = merra_data.to_dataframe()

        elif merra_attr is not None:  # special cases
            str("handle array as input")
            if stn_attr == "AvgWS":
                merra_df = load_merra_wind_data(merra_attr, merra_data)
                merra_attr = stn_attr

        else:  # missing data
            # raise error that there is missing data when important
            raise AttributeError
    except Exception as e:
        print("load_merra_data", e)
        exit(1)
        # traceback.print_exc()

    merra_df[merra_attr] = merra_df[merra_attr].apply(conversions.get(merra_attr, lambda x: x))
    merra_df = merra_df.rename(columns={"lat": "merra_lat", "lon": "merra_lon", merra_attr: "merra_" + stn_attr})
    return merra_df


# Given a years worth of station data in stn_df return a singular days worth of data on
# attribute stn_attr
def filter_stn_by_day(stn_df, day, stn_attr):
    timestamp_today = pd.Timestamp(day + timedelta(hours=1), tz=pytz.utc)
    timestamp_tomorrow = pd.Timestamp(day + timedelta(days=1), tz=pytz.utc)
    early_bound = pd.Timestamp(day + timedelta(hours=-6))
    late_bound = pd.Timestamp(day + timedelta(hours=(24 + 8)))

    try:
        stn_data = stn_df[["StnID", "time", "Station", stn_attr]]
        stn_data["time"] = stn_data["time"] + pd.Timedelta(hours=-1)
        stn_data = stn_data[(stn_data["time"] >= early_bound) & (stn_data["time"] < late_bound)]

        local = pytz.timezone('America/Winnipeg')
        stn_data["time"] = stn_data["time"].dt.tz_localize(local, ambiguous='infer')
        stn_data["time"] = stn_data["time"].apply(lambda x: x.astimezone(pytz.utc))

        stn_data = stn_data[(stn_data["time"] >= timestamp_today) & (stn_data["time"] <= timestamp_tomorrow)]

        stn_data = stn_data.merge(stn_metadata, on=["Station"], how="left")
        stn_data = stn_data.rename(columns={"LatDD": "stn_lat", "LongDD": "stn_long", stn_attr: "stn_" + stn_attr})
        return stn_data
    except (NonExistentTimeError, AmbiguousTimeError) as time_error:
        print("filter_stn_by_day (time_error)", time_error)
        # want to skip this day if there is a non-existent or an ambiguousTimeError time error raised
        raise AttributeError
    except Exception as e:
        print("filter_stn_by_day", e)
        # traceback.print_exc()


# Given a years worth of data in era5_da get the current days worth of data from the era dataset
# returns a dataframe with data for era5_attr for the hourly time in day
def filter_era5_by_day(day, era5_da, era5_attr, stn_attr):
    era5_times = era5_time_array(day)

    if isinstance(era5_attr, str) and era5_attr is not None:  # standard cases
        era5_data = era5_da.sel(longitude=long, latitude=lat, time=era5_times, method="nearest")
        era5_df = era5_data.to_dataframe()
        era5_df[era5_attr] = era5_df[era5_attr].apply(conversions.get(era5_attr, lambda x: x))
    else:
        if stn_attr == 'AvgWS':
            v_data = era5_da[0].sel(longitude=long, latitude=lat, time=era5_times, method="nearest")
            u_data = era5_da[1].sel(longitude=long, latitude=lat, time=era5_times, method="nearest")

            v_df = v_data.to_dataframe()
            u_df = u_data.to_dataframe()

            era5_df = wind_vector_to_scalar(v_df, u_df, "v10", "u10")
            era5_attr = stn_attr

    era5_df = era5_df.rename(
        columns={"latitude": "era5_lat", "longitude": "era5_long", era5_attr: "era5_" + stn_attr})
    # print(era5_df)
    return era5_df


# merge together data from era5, merra, and our station data
# Joins on time and location. For example every data point can be
# identified by a time and specific station at it.
def merge_data(merra_df, era5_df, stn_data):
    try:
        merged_df = era5_df.merge(merra_df, on=["location", "time"], how="outer")
        # df_index = merged_df.index.to_frame()

        stn_data["time"] = stn_data["time"].dt.tz_localize(tz=None)

        merged_df = stn_data.merge(merged_df, on=["location", "time"], how="inner")
        return merged_df
    except Exception as e:
        print('merge_data', e)


def calculate_sqr_error(merged_df, stn_attr):
    merra_col = "merra_" + stn_attr
    era5_col = "era5_" + stn_attr
    stn_col = "stn_" + stn_attr

    merged_df["merra_sqr_err"] = (merged_df[stn_col] - merged_df[merra_col]) ** 2
    merged_df["era5_sqr_err"] = (merged_df[stn_col] - merged_df[era5_col]) ** 2
    return merged_df


def append_csv(merged_df, stn_attr):
    output_file = "./output/" + stn_attr + "_output.csv"
    merged_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)


def clear_output():
    files = glob.glob('./output')
    for file in files:
        os.remove(file)


# global variables

# An array which holds metadata that is not recorded in the hourly table.
# Includes name, id (station number), longitude, and latitude
stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
stn_metadata = stn_metadata_preprocessing(stn_metadata)

# lat and long are pairs of the stations latitude and longitude
# coordinates. Each list is in order so that if you access index
# i of each array then it will be the coordinate for the ith
# weather station
lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

# plain text names for all the stations in order. Each index is
# will be the same as the index mapping in lat and long
station_names = stn_metadata['Station'].tolist()

# index to have the correct plaintext station name for every row
station_index = location_names()

# relative directory for where data is being held on this machine.
# outside this GitHub repo. Change if needed
data_dir = "../../../../data/"


def main():
    # loop through the named attributes of each of the different file types
    # all the attributes should be a mapping to each other.
    for stn_attr, era5_attr, merra_attr in zip(stn_attrs, era5_attrs, merra_attrs):
        for year in years:

            # da = data array, df = dataframe
            era5_da = load_era5_data(era5_attr, year)
            stn_df = load_stn_data(year)

            if stn_attr == ['TBRG_Rain', 'Pluvio_Rain']:
                stn_attr = get_rain_column(stn_df, year)

            # initialize the start and end date
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            time_delta = end_date - start_date

            for i in range(time_delta.days + 1):
                day = start_date + timedelta(days=i)

                # handling one chunk of data written to the csv
                try:
                    merra_df = load_merra_data(merra_attr, day, stn_attr)
                    era5_df = filter_era5_by_day(day, era5_da, era5_attr, stn_attr)
                    stn_data = filter_stn_by_day(stn_df, day, stn_attr)
                except AttributeError:
                    print("main", day)
                    continue

                merged_df = merge_data(merra_df, era5_df, stn_data)
                try:
                    merged_df = calculate_sqr_error(merged_df, stn_attr)
                    append_csv(merged_df, stn_attr)
                except TypeError as e:
                    print("main", e)


# bootstrap
main()
