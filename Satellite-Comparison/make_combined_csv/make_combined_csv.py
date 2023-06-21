import glob
import math
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
stn_attrs = ['AvgAir_T', 'AvgWS', 'Soil_TP5_TempC', ['Soil_TP5_TempC', 'Soil_TP20_TempC'], 'Soil_TP20_TempC',
             'Soil_TP50_TempC', ['Soil_TP50_TempC', 'Soil_TP100_TempC'],
             ['Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC'], 'SolarRad', ['TBRG_Rain', 'Pluvio_Rain'],
             "Press_hPa", 'Soil_TP5_VMC', 'Soil_TP20_VMC', ['Soil_TP20_VMC', 'Soil_TP50_VMC', 'Soil_TP100_VMC'],
             'Soil_TP100_VMC', 'RH']

# attribute names for era5
era5_attrs = ['t2m', ['v10m', 'u10m'], 'stl1', None, 'stl2',
              None, None,
              'stl3', 'ssrd', 'tp',
              'sp', 'swvl1', 'swvl2', 'swvl3',
              None, ['t2m', 'd2m'], 'd2m']
# attribute names for merra2
merra_attrs = ["T2M", ["V10M", "U10M"], None, "TSOIL1", "TSOIL2",
              "TSOIL3", "TSOIL4",
              None, "SWGDN", "PRECTOTLAND",
              "PS", "SFMC", None, None,
              "RZMC", ["T2M", "T2MDEW"], "T2MDEW"]


# For testing purposes
# stn_attrs = ['RH']
# era5_attrs = ['d2m']
# merra_attrs = ["T2MDEW"]

# attribute names for merra broken down by database
# _2 folders were there since they were added outside the
# original data scope and had to be downloaded later
M2T1NXSLV = ["T2M", ["V10M", "U10M"], "QV2M", "PS", "T2MDEW", ["T2M", "T2MDEW"]]
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
    v[v_col] = (v[v_col] ** 2 + u[u_col] ** 2) ** (1 / 2)
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
    "QV2M": decimal_to_percent,
}


# using the equation
# RH = 100 x [e^((17.625 * DP) / (243.04 + DP)) / e^((17.625 * T) / (243.04 + T))]
# taken from the website https://www.omnicalculator.com/physics/relative-humidity
def calculate_relative_humidity(temp, dew_point):
    rh_df = temp.copy()
    rh_df = rh_df.rename(columns={'t2m': "rh"})
    rh_df["rh"] = rh_df["rh"] * 0 + math.e

    temp["t2m"] = temp["t2m"].apply(kelvin_to_celsius)
    dew_point["d2m"] = dew_point["d2m"].apply(kelvin_to_celsius)

    numerator = rh_df["rh"].pow((17.625 * dew_point["d2m"]).div(243.04 + dew_point["d2m"]))
    denominator = rh_df["rh"].pow((17.625 * temp["t2m"]).div(243.04 + temp["t2m"]))

    col = numerator.div(denominator) * 100
    rh_df["rh"] = col
    return rh_df


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


def load_humidity_data(era5_attr, year):
    t2m = get_era_filename(year, era5_attr[0])
    d2m = get_era_filename(year, era5_attr[1])

    t2m_da = xr.open_dataarray(data_dir + t2m)
    d2m_da = xr.open_dataarray(data_dir + d2m)

    return [t2m_da, d2m_da]


# load era5 data from the file and return a xarray data array
def load_era5_data(era5_attr, year):
    # era5 has files per attribute per year
    if isinstance(era5_attr, str) and era5_attr is not None:
        era5_file = get_era_filename(year, era5_attr)
        # data array since 1 attribute per file
        era5_da = xr.open_dataarray(data_dir + era5_file)

        if era5_attr == "ssrd":
            era5_da = undo_cumulative_sum(era5_da)

        return era5_da
    else:
        # handle special cases
        if era5_attr is None:
            return None
        if era5_attr[0] == "v10m":
            return load_era5_wind_data(era5_attr, year)
        if era5_attr[0] == "t2m":
            return load_humidity_data(era5_attr, year)


# TODO this isnt necessarily complete. For instance what if a station got a pluvio station during the middle of the year
# It would select pluvio still even thought it would have bad data for half of the year. Not sure what the best way to
# do this is.

# Another reason this won't work is that it's not looking at specific stations, It's looking at all stations for the
# year
def get_rain_column(stn_df, year):
    start_time = datetime.strptime(str(year) + "-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(str(year) + "-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")
    # Pluvio_Rain is preferable to TBRG_Rain
    year_df = stn_df[(stn_df["time"] >= start_time) & (stn_df["time"] < end_time)]
    pluvio = year_df["Pluvio_Rain"].sum()
    tbrg_rain = year_df["TBRG_Rain"].sum()

    if pluvio != 0:
        return "Pluvio_Rain"
    elif tbrg_rain != 0:
        return "TBRG_Rain"
    else:
        print("no precipitation values for both Pluvio and TBRG, something is probably broken. Sorry!")
        print("date range: ", start_time, end_time)
        exit(1)


def get_soil_column(stn_df, stn_attr, col_name):
    if stn_attr == ['Soil_TP5_TempC', 'Soil_TP20_TempC']:
        stn_df[col_name] = (stn_df['Soil_TP5_TempC'] * 0.675 + stn_df['Soil_TP20_TempC'] * 0.325) / 2.0
    elif stn_attr == ['Soil_TP50_TempC', 'Soil_TP100_TempC']:
        stn_df[col_name] = (stn_df['Soil_TP50_TempC'] + stn_df['Soil_TP100_TempC']) / 2.0
    elif stn_attr == ['Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC']:
        stn_df[col_name] = (stn_df['Soil_TP20_TempC'] + stn_df['Soil_TP50_TempC'] + stn_df['Soil_TP100_TempC']) / 3.0
    elif stn_attr == ['Soil_TP20_VMC', 'Soil_TP50_VMC', 'Soil_TP100_VMC']:
        stn_df[col_name] = (stn_df['Soil_TP20_VMC'] + stn_df['Soil_TP50_VMC'] + stn_df['Soil_TP100_VMC']) / 3.0

    return stn_df


def get_soil_column_name(stn_attr):
    if stn_attr == ['Soil_TP5_TempC', 'Soil_TP20_TempC']:
        return "Soil_5_20_avg_TempC"
    elif stn_attr == ['Soil_TP50_TempC', 'Soil_TP100_TempC']:
        return "Soil_50_100_avg_TempC"
    elif stn_attr == ['Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC']:
        return "Soil_20_50_100_avg_TempC"
    elif stn_attr == ['Soil_TP20_VMC', 'Soil_TP50_VMC', 'Soil_TP100_VMC']:
        return "Soil_20_50_100_avg_VMC"


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


def load_merra_rh_data(merra_attr, merra_data, stn_attr):
    merra_data = shift_merra_timescale(merra_data)
    temp = merra_data[merra_attr[0]].to_dataframe()
    dew_point = merra_data[merra_attr[1]].to_dataframe()

    rh_df = temp.copy()
    rh_df = rh_df.rename(columns={'T2M': stn_attr})
    rh_df[stn_attr] = rh_df[stn_attr] * 0 + math.e

    temp["T2M"] = temp["T2M"].apply(kelvin_to_celsius)
    dew_point["T2MDEW"] = dew_point["T2MDEW"].apply(kelvin_to_celsius)

    numerator = rh_df[stn_attr].pow((17.625 * dew_point["T2MDEW"]).div(243.04 + dew_point["T2MDEW"]))
    denominator = rh_df[stn_attr].pow((17.625 * temp["T2M"]).div(243.04 + temp["T2M"]))

    col = numerator.div(denominator) * 100
    rh_df[stn_attr] = col
    return rh_df


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
            elif stn_attr == "RH":
                merra_df = load_merra_rh_data(merra_attr, merra_data, stn_attr)
                merra_attr = stn_attr

        else:  # missing data
            # raise error that there is missing data when important
            raise AttributeError
    except FileNotFoundError as file_not_found:
        if merra_attr is None:
            return None
        print("load_merra_data", file_not_found)
        exit(1)

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
        elif stn_attr == "RH":
            t2m_data = era5_da[0].sel(longitude=long, latitude=lat, time=era5_times, method="nearest")
            d2m_data = era5_da[1].sel(longitude=long, latitude=lat, time=era5_times, method="nearest")

            t2m_data = t2m_data.to_dataframe()
            d2m_data = d2m_data.to_dataframe()

            era5_df = calculate_relative_humidity(t2m_data, d2m_data)
            era5_attr = "rh"
        elif era5_attr is None:
            return None

    era5_df = era5_df.rename(
        columns={"latitude": "era5_lat", "longitude": "era5_long", era5_attr: "era5_" + stn_attr})
    # print(era5_df)
    return era5_df


# merge together data from era5, merra, and our station data
# Joins on time and location. For example every data point can be
# identified by a time and specific station at it.
def merge_data(merra_df, era5_df, stn_data):
    try:
        stn_data["time"] = stn_data["time"].dt.tz_localize(tz=None)

        merged_df = era5_df.merge(merra_df, on=["location", "time"], how="outer")
        # df_index = merged_df.index.to_frame()

        merged_df = stn_data.merge(merged_df, on=["location", "time"], how="inner")
        return merged_df
    except Exception as err:
        if merra_df is None:
            return stn_data.merge(era5_df, on=["location", "time"], how="inner")
        elif era5_df is None:
            return stn_data.merge(merra_df, on=["location", "time"], how="inner")
        else:
            print("merge data: uncaught", err)


def calculate_sqr_error(merged_df, stn_attr):
    merra_col = "merra_" + stn_attr
    era5_col = "era5_" + stn_attr
    stn_col = "stn_" + stn_attr

    if merra_col in merged_df.columns:
        merged_df["merra_err"] = (merged_df[stn_col] - merged_df[merra_col])
        merged_df["merra_sqr_err"] = (merged_df[stn_col] - merged_df[merra_col]) ** 2

    if era5_col in merged_df.columns:
        merged_df["era5_err"] = (merged_df[stn_col] - merged_df[era5_col])
        merged_df["era5_sqr_err"] = (merged_df[stn_col] - merged_df[era5_col]) ** 2
    return merged_df


def prune_missing_data(df, stn_attr):
    col = "stn_" + stn_attr
    drop_index = df[pd.isna(df[col])].index
    df.drop(drop_index, inplace=True)
    return df


def append_csv(merged_df, stn_attr):
    output_file = "./output/pre_cleaning/" + stn_attr + "_output.csv"
    merged_df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)


def clear_output():
    files = glob.glob('./output/pre_cleaning')
    for file in files:
        os.remove(file)


# used to undo the cumulative sum done on the column of data that is era5 for solar radiation
def undo_cumulative_sum(data_array):
    # xarray function, not pandas
    return data_array.diff("time")


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
            col_name = stn_attr

            # da = data array, df = dataframe
            era5_da = load_era5_data(era5_attr, year)
            stn_df = load_stn_data(year)

            if stn_attr == ['TBRG_Rain', 'Pluvio_Rain']:
                stn_attr = get_rain_column(stn_df, year)
                col_name = stn_attr
            elif (stn_attr == ['Soil_TP5_TempC', 'Soil_TP20_TempC']
                  or stn_attr == ['Soil_TP50_TempC', 'Soil_TP100_TempC']
                  or stn_attr == ['Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC']
                  or stn_attr == ['Soil_TP20_VMC', 'Soil_TP50_VMC', 'Soil_TP100_VMC']):
                col_name = get_soil_column_name(stn_attr)
                stn_df = get_soil_column(stn_df, stn_attr, col_name)

            # initialize the start and end date
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            time_delta = end_date - start_date

            for i in range(time_delta.days + 1):
                day = start_date + timedelta(days=i)

                # handling one chunk of data written to the csv
                try:
                    merra_df = load_merra_data(merra_attr, day, col_name)
                    era5_df = filter_era5_by_day(day, era5_da, era5_attr, col_name)
                    stn_data = filter_stn_by_day(stn_df, day, col_name)
                except AttributeError:
                    print("main", day)
                    continue

                merged_df = merge_data(merra_df, era5_df, stn_data)
                try:
                    merged_df = calculate_sqr_error(merged_df, col_name)
                    merged_df = prune_missing_data(merged_df, col_name)
                    append_csv(merged_df, col_name)
                except TypeError as e:
                    print("main", e)


# bootstrap
main()
