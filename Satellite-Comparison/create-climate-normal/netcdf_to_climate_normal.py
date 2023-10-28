import pytz
import xarray as xr
import pandas as pd
import numpy as np
import glob
import pytz


def capitalize_names():
    stn_metadata = pd.read_csv("StationList.csv")
    stn_metadata["StationName"] = stn_metadata["StationName"].str.upper()
    print(stn_metadata["StationName"])
    stn_metadata.to_csv("StationList.csv")


def p(t):
    k = 1

    if t < 7:
        return t * 0
    elif 7 <= t < 21:
        return k * (1 - ((t - 21) ** 2 / (21 - 7) ** 2))
    elif 21 <= t < 30:
        return k * (1 - ((t - 21) ** 2 / (30 - 21) ** 2))
    elif 30 <= t:
        return t * 0

    print("fatal error, outside of defined behaviour in p(t)")
    exit(1)


def calculate_p_day(t):
    t_min = t.min()
    t_max = t.max()

    t1 = p(t_min)
    t2 = p(((2 * t_min) + t_max)/3)
    t3 = p((t_min + (2 * t_max))/3)
    t4 = p(t_max)

    return (1/24) * (5 * t1 + 8 * t2 + 8 * t3 + 3 * t4)


def calculate_chu(t_min, t_max):

    chu = (1.8 * (t_min - 4.4) + 3.33 * (t_max - 10) - 0.084 * (t_max - 10) ** 2) / 2.0
    return chu.clip(0)


def calculate_gdd(t):
    t_min = t.min()
    t_max = t.max()

    conditional = (t_min + t_max)/2 - 5

    if conditional > 0:
        return conditional
    elif conditional <= 0:
        return t_min * 0


def netcdf_to_climate_normal(ds):
    ds["time"] = pd.DatetimeIndex(ds['time'].values)

    climate_normal_ds = xr.Dataset()

    climate_normal_ds["Tavg"] = ds["t2m_corr"].resample(time="1D").mean()
    climate_normal_ds["Tmax"] = ds["t2m_corr"].resample(time="1D").max()
    climate_normal_ds["Tmin"] = ds["t2m_corr"].resample(time="1D").min()

    climate_normal_ds["PPT"] = ds["tp_corr"].resample(time="1D").sum()

    climate_normal_ds["PDay"] = ds["t2m_corr"].resample(time="1D").map(calculate_p_day)
    climate_normal_ds["GDD"] = ds["t2m_corr"].resample(time="1D").map(calculate_gdd)
    climate_normal_ds["CHU"] = calculate_chu(climate_normal_ds["Tmin"], climate_normal_ds["Tmax"])

    df_climate_normal = climate_normal_ds.to_dataframe()
    df_climate_normal["NormYY"] = pd.to_datetime(df_climate_normal.index.to_frame()["time"]).dt.year
    df_climate_normal["NormMM"] = pd.to_datetime(df_climate_normal.index.to_frame()["time"]).dt.month.map('{:0>2d}'.format)
    df_climate_normal["NormDD"] = pd.to_datetime(df_climate_normal.index.to_frame()["time"]).dt.day.map('{:0>2d}'.format)
    df_climate_normal["JD"] = pd.to_datetime(df_climate_normal.index.to_frame()["time"]).dt.dayofyear
    df_climate_normal["DateDT"] = pd.to_datetime(df_climate_normal.index.to_frame()["time"])

    # format of NormLocation
    # AAAAOOOO
    # where A is for lAtitude and O is for lOngitude
    # insert a decimal place between the 3rd and 4th letter
    # leading space is padded with 0's
    # negitive is implied with longitude
    # so 05711078 is 57.1 Latitude, -107.8 Longitude
    lat = df_climate_normal.index.to_frame()["latitude"].abs() * 10
    lon = df_climate_normal.index.to_frame()["longitude"].abs() * 10
    df_climate_normal["NormLocation"] = lat.map('{:0>4.0f}'.format) + lon.map('{:0>4.0f}'.format)

    df_climate_normal["lat"] = df_climate_normal.index.to_frame()["latitude"]
    df_climate_normal["lon"] = df_climate_normal.index.to_frame()["longitude"]

    return df_climate_normal


def filter_climate_normal(df):
    stn_metadata = pd.read_csv("StationList.csv")
    latitudes = stn_metadata["LatDD"].values.round(1)
    longitudes = stn_metadata["LongDD"].values.round(1)

    stn_metadata["latitude"] = latitudes
    stn_metadata["longitude"] = longitudes

    stn_metadata = stn_metadata[["latitude", "longitude", "StationName", "StnID"]]

    match_lat = df['lat'].isin(latitudes)
    match_lon = df['lon'].isin(longitudes)

    match = np.logical_and(match_lat, match_lon)

    df = df.loc[match]

    df = df.merge(stn_metadata, how="inner", on=["latitude", "longitude"])
    df["Location"] = df["StationName"]

    df = df[
        ["StnID", "Location", "NormYY", "NormMM", "NormDD", "DateDT", "JD", "Tmax", "Tmin", "Tavg", "PPT", "CHU", "GDD",
         "PDay", "NormLocation"]]

    return df


def filter_climate_normal_era5(df):
    stn_metadata = pd.read_csv("StationList.csv")
    latitudes = stn_metadata["LatDD"].values.round(1)
    longitudes = stn_metadata["LongDD"].values.round(1)

    stn_metadata["lat"] = latitudes
    stn_metadata["lon"] = longitudes

    stn_metadata = stn_metadata[["lat", "lon", "StationName", "StnID"]]

    df["lat"] = df["lat"].values.round(1)
    df["lon"] = df["lon"].values.round(1)

    match_lat = df['lat'].isin(latitudes)
    match_lon = df['lon'].isin(longitudes)

    match = np.logical_and(match_lat, match_lon)

    df = df.loc[match]

    df = df.merge(stn_metadata, how="inner", on=["lat", "lon"])

    df["Location"] = df["StationName"]

    df = df[
        ["StnID", "Location", "NormYY", "NormMM", "NormDD", "DateDT", "JD", "Tmax", "Tmin", "Tavg", "PPT", "CHU", "GDD",
         "PDay", "NormLocation"]]

    return df


def corrected_climate_normal_to_average(era5=False):
    # load 1980 into a generic "sum" df. Load each df, then add it to the
    # sum df. After summing all years, divide the sum df by the number years
    # to get the average.

    if era5:
        print("Using ERA5 uncorrected data")
    else:
        print("Using corrected ERA5 data")

    start_year = 1980
    end_year = 2000

    if era5:
        files = glob.glob('../../../data/climate_normal_era5/*.csv')
        cummulative_df = pd.read_csv('../../../data/climate_normal_era5/' + str(end_year) + '.csv')
    else:
        files = glob.glob('../../../data/climate_normal/*.csv')
        cummulative_df = pd.read_csv('../../../data/climate_normal/' + str(end_year) + '.csv')

    cummulative_df["counter"] = [1] * len(cummulative_df["Tmax"])

    for file in files:
        if era5:
            year = int(file.replace('../../../data/climate_normal_era5\\', "").replace(".csv", ""))
        else:
            year = int(file.replace('../../../data/climate_normal\\', "").replace(".csv", ""))

        if end_year > year >= start_year:
            year_df = pd.read_csv(file)

            print(file)

            merged_df = cummulative_df.merge(year_df, how="outer", on=["Location", "JD"])

            merged_df["counter"] = merged_df["counter"] + 1
            merged_df["counter"].fillna(1, inplace=True)
            merged_df.fillna(0, inplace=True)

            # columns: Tmax, Tmin, Tavg, PPT, CHU, GDD, PDay
            # cummulative_df[["Tmax", "Tmin", "Tavg", "PPT", "CHU", "GDD", "PDay"]] = merged_df[["Tmax_x", "Tmin_x", "Tavg_x", "PPT_x", "CHU_x", "GDD_x", "PDay_x"]] + merged_df[["Tmax_y", "Tmin_y", "Tavg_y", "PPT_y", "CHU_y", "GDD_y", "PDay_y"]]

            cummulative_df["Tmax"] = merged_df["Tmax_x"] + merged_df["Tmax_y"]
            cummulative_df["Tmin"] = merged_df["Tmin_x"] + merged_df["Tmin_y"]
            cummulative_df["Tavg"] = merged_df["Tavg_x"] + merged_df["Tavg_y"]
            cummulative_df["PPT"] = merged_df["PPT_x"] + merged_df["PPT_y"]
            cummulative_df["CHU"] = merged_df["CHU_x"] + merged_df["CHU_y"]
            cummulative_df["GDD"] = merged_df["GDD_x"] + merged_df["GDD_y"]
            cummulative_df["PDay"] = merged_df["PDay_x"] + merged_df["PDay_y"]
            cummulative_df["counter"] = merged_df["counter"]

    cummulative_df["Tmax"] = cummulative_df["Tmax"] / cummulative_df["counter"]
    cummulative_df["Tmin"] = cummulative_df["Tmin"] / cummulative_df["counter"]
    cummulative_df["Tavg"] = cummulative_df["Tavg"] / cummulative_df["counter"]
    cummulative_df["PPT"] = cummulative_df["PPT"] / cummulative_df["counter"]
    cummulative_df["CHU"] = cummulative_df["CHU"] / cummulative_df["counter"]
    cummulative_df["GDD"] = cummulative_df["GDD"] / cummulative_df["counter"]
    cummulative_df["PDay"] = cummulative_df["PDay"] / cummulative_df["counter"]
    print(cummulative_df["counter"])
    print(cummulative_df[["Tmax", "Tmin", "Tavg", "PPT", "CHU", "GDD", "PDay"]])

    if era5:
        cummulative_df.to_csv("../../../data/climate_normal_avg/" + str(end_year) + "_era5.csv")
    else:
        cummulative_df.to_csv("../../../data/climate_normal_avg/" + str(end_year) + ".csv")


def corrected_files_to_climate_normal():
    files = glob.glob('../../../data/historical_era5/corrected_netcdf/*.nc')
    for file in files:
        ds = xr.open_dataset(file)
        print(file)
        output_file = file.replace("/historical_era5/corrected_netcdf", "/climate_normal").replace(".nc", ".csv")
        df = netcdf_to_climate_normal(ds)
        df = filter_climate_normal(df)

        df.to_csv(output_file)


def era5_files_to_climate_normal():
    files = glob.glob('../../../data/historical_era5/yearly/*.nc')
    for file in files:
        print(file)
        year = file[-7:-3]

        ds = xr.open_dataset(file)
        # time = pd.date_range(start=year + '-01-01', end=year + '-12-31 23:00:00', freq='H', tz='America/Winnipeg')
        #
        # ds['time_local'] = ('time', time)
        #
        # ds = ds.set_index(time="time_local")

        ds["t2m_corr"] = ds["t2m"] - 273.15
        ds["tp_corr"] = ds["tp"] * 100

        output_file = file.replace("/historical_era5/yearly", "/climate_normal_era5").replace(".nc", ".csv")
        df = netcdf_to_climate_normal(ds)
        df = filter_climate_normal_era5(df)

        df.to_csv(output_file)


# corrected_files_to_climate_normal()
era5_files_to_climate_normal()
# capitalize_names()
corrected_climate_normal_to_average(True)
