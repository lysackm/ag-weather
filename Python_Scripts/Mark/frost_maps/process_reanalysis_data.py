import xarray as xr
import pandas as pd
from datetime import timedelta, date

data_dir = "../../../../merra/merra_temp_1993-2023/"
base_dir_era5 = "../../../../data/era5/"
base_dir_nrcan = "../../../../data/nrcan/"


def get_merra_filename(cur_date):
    # format date
    date_str = cur_date.strftime("%Y%m%d")

    return "tavg1_2d_slv_Nx." + date_str + ".nc4"


def merra_time_array(cur_date):
    times = []
    for i in range(0, 24):
        times.append(cur_date.isoformat() + "T%.2f:00:00" % i)
    return times


def stn_metadata_preprocessing(stn_meta):
    stn_meta = stn_meta[['StationName', 'LongDD', 'LatDD', 'SN']]
    stn_meta = stn_meta.rename(columns={
        "StationName": "Station",
        "SN": "location",
        "TMSTAMP": "time"})
    stn_meta["Station"] = stn_meta["Station"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))
    stn_meta["location"] = stn_meta["location"] - 1
    return stn_meta


# Used to align the timescale for the merra_data to be inline with
# the other time scales, ie era5 and station data. Sets the time to
# be the end of the averaged time. That is to add 30 minutes to the
# recorded time stamp
def shift_merra_timescale(merra_data):
    merra_data['time'] = pd.to_datetime(merra_data['time']) + timedelta(hours=0.5)
    return merra_data


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


# global variables

# An array which holds metadata that is not recorded in the hourly table.
# Includes name, id (station number), longitude, and latitude
stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
stn_metadata = stn_metadata_preprocessing(stn_metadata)

# lat and long are pairs of the stations latitude and longitude
# coordinates. Each list is in order so that if you access index
# i of each array then it will be the coordinate for the ith
# weather station
lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])


# load and return a singular days worth of merra data of attribute
# merra_attr
def load_merra_data(day):
    try:
        merra_file = get_merra_filename(day)
        # data set since multiple attributes per file
        merra_ds = xr.open_dataset(data_dir + merra_file)

        merra_times = merra_time_array(day)
        merra_data = merra_ds.sel(lon=long, lat=lat, time=merra_times, method="nearest")

        merra_data = shift_merra_timescale(merra_data)
        merra_df = merra_data.to_dataframe()

    except FileNotFoundError as file_not_found:
        print("load_merra_data", file_not_found)
        exit(1)

    merra_df["T2M"] = merra_df["T2M"].apply(kelvin_to_celsius)
    merra_df = merra_df.rename(columns={"lat": "merra_lat", "lon": "merra_lon", "T2M": "merra_air_temp"})
    return merra_df


def merge_merra():
    merra_dfs = []

    # initialize the start and end date
    start_date = date(1994, 1, 1)
    end_date = date(2023, 12, 31)
    time_delta = end_date - start_date

    for i in range(time_delta.days + 1):
        day = start_date + timedelta(days=i)

        merra_df = load_merra_data(day)
        merra_dfs.append(merra_df)

    df_merged = pd.concat(merra_dfs)

    df_merged.reset_index(inplace=True)
    df_merged["time"] = pd.to_datetime(df_merged["time"])
    df_merged["time"] = df_merged["time"].dt.tz_localize(tz="UTC").dt.tz_convert(tz="America/Winnipeg")
    df_merged = df_merged.where((df_merged.time.dt.year != 2024) & (df_merged.time.dt.year != 1993))
    df_merged = df_merged[df_merged["time"].notna()]

    df_merged.to_csv("./data/merra_temp_data.csv", index=False)
    print(df_merged)


def add_station_column(reanalysis_product="era5"):
    stn_df = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

    if reanalysis_product == "merra":
        df = pd.read_csv("./data/merra_temp_data.csv")
    elif reanalysis_product == "era5":
        df = pd.read_csv("./data/era5_temp_data.csv")
    elif reanalysis_product == "nrcan":
        df = pd.read_csv("./data/nrcan_temp_data.csv")

    df["location"] = df["location"] + 1
    stn_df = stn_df[["SN", "StnID", "StationName"]]
    df = df.merge(stn_df, how="left", left_on="location", right_on="SN")

    if reanalysis_product == "merra":
        df = df[["time", "SN", "StnID", "StationName", "merra_lon", "merra_lat", "merra_air_temp"]]
        df.to_csv("./data/merra_temp_data.csv", index=False)
    elif reanalysis_product == "era5":
        df = df[["time", "SN", "StnID", "StationName", "era5_lon", "era5_lat", "era5_air_temp"]]
        df.to_csv("./data/era5_temp_data.csv", index=False)
    elif reanalysis_product == "nrcan":
        df = df[["time", "SN", "StnID", "StationName", "nrcan_lon", "nrcan_lat", "nrcan_mint", "nrcan_maxt"]]
        df.to_csv("./data/nrcan_temp_data.csv", index=False)
    print(df)


def merge_era5():
    dfs = []

    for year in range(1994, 2024):
        print(year)
        file = base_dir_era5 + "t2m" + str(year) + ".nc/data.nc"
        era5_da = xr.open_dataarray(file)

        era5_data = era5_da.sel(longitude=long, latitude=lat, method="nearest")
        era5_df = era5_data.to_dataframe()
        era5_df["t2m"] = era5_df["t2m"].apply(kelvin_to_celsius)

        dfs.append(era5_df)

    df = pd.concat(dfs)

    df.reset_index(inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    df["time"] = df["time"].dt.tz_localize(tz="UTC").dt.tz_convert(tz="America/Winnipeg")
    df = df.where((df.time.dt.year != 2024) & (df.time.dt.year != 1993))
    df = df[df["time"].notna()]
    df = df.rename(columns={"latitude": "era5_lat", "longitude": "era5_lon", "t2m": "era5_air_temp"})

    df.to_csv("./data/era5_temp_data.csv", index=False)


def merge_nrcan():
    dfs = []

    for year in range(1994, 2021):
        file_mint = base_dir_nrcan + "mint_dly_" + str(year) + "_deflated.nc"
        file_maxt = base_dir_nrcan + "maxt_dly_" + str(year) + "_deflated.nc"
        print(file_mint)
        nrcan_mint_ds = xr.open_dataset(file_mint)["mint"]
        nrcan_maxt_ds = xr.open_dataset(file_maxt)["maxt"]

        nrcan_mint_data = nrcan_mint_ds.sel(lon=long, lat=lat, method="nearest")
        nrcan_maxt_data = nrcan_maxt_ds.sel(lon=long, lat=lat, method="nearest")
        nrcan_mint_df = nrcan_mint_data.to_dataframe()
        nrcan_maxt_df = nrcan_maxt_data.to_dataframe()
        nrcan_df = nrcan_mint_df.merge(nrcan_maxt_df, how="outer", on=["time", "location"])

        dfs.append(nrcan_df)

    df = pd.concat(dfs)
    df.reset_index(inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    df["time"] = df["time"].dt.tz_localize(tz="UTC").dt.tz_convert(tz="America/Winnipeg")
    df = df.where((df.time.dt.year != 2024) & (df.time.dt.year != 1993))
    df = df[df["time"].notna()]
    df = df.rename(columns={"lat_x": "nrcan_lat", "lon_x": "nrcan_lon", "mint": "nrcan_mint", "maxt": "nrcan_maxt"})
    df = df.drop(columns=["lat_y", "lon_y"])

    df.to_csv("./data/nrcan_temp_data.csv", index=False)


def main():
    # merge_merra()
    # merge_era5()
    merge_nrcan()
    add_station_column(reanalysis_product="nrcan")


if __name__ == "__main__":
    main()
