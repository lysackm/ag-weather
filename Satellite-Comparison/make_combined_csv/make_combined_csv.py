import traceback
from datetime import date, timedelta
import xarray as xr
import pandas as pd
import numpy as np

# years which the analysis will be done
years = [2018, 2019, 2020, 2021, 2022]

stn_attrs = ['Air_T', 'AvgWS', 'RH', 'Soil_TP5_TempC', 'Soil_TP20_TempC', 'Soil_TP50_TempC', 'Soil_TP100_TempC',
             'SolarRad', ['TBRG_Rain', 'Pluvio_Rain'], 'Soil_TP5_VMC', 'Soil_TP20_VMC',
             ['Soil_TP50_VMC', 'Soil_TP100_VMC']]
era5_attrs = ['t2m', ['v10m', 'u10m'], None, 'st1', 'st2', 'st3', None, 'rad', 'totprec', 'sw1', 'sw2', 'sw3']
merra_attrs = ["T2M", ["V10M", "U10M"], "QV2M", "TSOIL1", "TSOIL2", "TSOIL3", "TSOIL4", "SWGDN", "PRECTOTLAND",
               "GWETTOP", "GWETROOT", "GWETPROF"]

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


def get_stn_filename(year):
    return "station-csv/MBAg-60min-" + str(year) + ".csv"


def merra_time_array(date):
    times = []
    for i in range(0, 24):
        times.append(date.isoformat() + "T%.2f:00:00" % i)
    return times


def locationNames():
    mapping = []
    for name in station_names:
        for x in range(24):
            mapping.append(name)

    return mapping

stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
# D:\PycharmProjects\Cleaning-Data\cleaning-data\util\station-metadata.csv
lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])
station_names = stn_metadata['StationName'].tolist()
station_index = locationNames()


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

            # handling one chunk of data written to the csv
            try:
                if isinstance(era5_attr, str) and era5_attr is not None:  # standard cases
                    merra_file = get_merra_filename(day, merra_attr)

                    # data set since multiple attributes per file
                    merra_ds = xr.open_dataset(data_dir + merra_file)

                    times = merra_time_array(day)
                    merra_data = merra_ds.sel(lon=long, lat=lat, time=times, method="nearest")
                    merra_data = merra_data[merra_attr]

                elif era5_attr is not None:  # special cases
                    str("handle array as input")

                else:  # missing data
                    continue
            except Exception as e:
                print(e)
                # traceback.print_exc()

            era5_data = era5_da.sel(longitude=long, latitude=lat, time=times, method="nearest")

            try:
                stn_df = stn_df[["StnID", "TMSTAMP", "Station", stn_attr]]
                # TODO why does this logic not work?
                stn_data = stn_df[(stn_df["TMSTAMP"] > start_date_str) & (stn_df["TMSTAMP"] < end_date_str)]
                print(stn_data)
            except Exception as e:
                print(e)

            # flattening arrays to be 1 dimensional
            merra_stacked = merra_data.stack(z=("location", "time"))
            merra_stacked_np = merra_stacked.to_numpy()
            merra_stacked_np = merra_stacked_np - 273.15

            era5_stacked = era5_data.stack(z=("location", "time"))
            era5_stacked_np = era5_stacked.to_numpy()
            era5_stacked_np = era5_stacked_np - 273.15

            # print("era", era5_stacked_np)
            # print("merra", merra_stacked_np)

            joined_data = np.vstack((merra_stacked_np, era5_stacked_np, station_index)).T
            # print(joined_data)
            # print("start")
            # for row in joined_data:
            #     print(row)
            # print("end")

            # https://stackoverflow.com/questions/72179103/xarray-select-the-data-at-specific-x-and-y-coordinates

            # station_data = db.select(select date, StnID, StationName, Latitude, Longitude, Elevation, attribute
            #           where date > date_start and date < date_end)

            # https://docs.xarray.dev/en/stable/generated/xarray.merge.html

            # mbagweather.ca/historical/CSV/
            # would have to dump 6 months or so of 2022

            # AC data
