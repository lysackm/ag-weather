import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import plotly.express as px


def process_data():
    df = pd.read_csv("Press_hPa_output.csv")

    df = df[["merra_err", "era5_err", "StnID", "stn_lat", "stn_long"]].groupby(["StnID", "stn_lat", "stn_long"]).mean()

    # merra
    df_merra = df
    df_merra["value"] = df_merra["merra_err"]
    df_merra = df_merra[["value"]]
    df_merra.to_csv("merra_pressure_means.csv")

    # era5
    df_era5 = df
    df_era5["value"] = df_era5["era5_err"]
    df_era5 = df_era5[["value"]]
    df_era5.to_csv("era5_pressure_means.csv")


def stn_metadata_preprocessing(stn_meta):
    stn_meta = stn_meta[['StationName', 'LongDD', 'LatDD', 'SN', "Elevation", "StnID"]]
    stn_meta = stn_meta.rename(columns={
        "StationName": "Station",
        "SN": "location",
        "TMSTAMP": "time",
        "Elevation": "elevation"})
    stn_meta["Station"] = stn_meta["Station"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))
    stn_meta["location"] = stn_meta["location"] - 1
    return stn_meta


def merra():
    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

    da = xr.open_dataset("merra2_geopotential.nc4")
    da = da.sel(lon=long, lat=lat, time="1980-01-15 12:00:00", method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["location", "Station", "elevation"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    df["PHIS"] = (6371229 * (df["PHIS"] / 9.80665)) / (6371229 - (df["PHIS"] / 9.80665))
    df = df.rename(columns={"PHIS": "merra_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["merra_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)
    df["abs_elevation"] = df["elevation_err"].abs()
    df = df.sort_values(by=["abs_elevation"], ascending=False)

    elevation_means = pd.read_csv("pressure_means.csv")
    elevation_means = elevation_means[["location", "value"]]
    df = df.merge(elevation_means, how="left", left_on="Station", right_on="location")

    df = df[["Station", "stn_elevation", "merra_elevation", "elevation_err", "value"]]

    df = df[df["value"].notna()]
    x = df["elevation_err"].tolist()
    y = df["value"].tolist()

    plt.scatter(x, y)
    a, b = np.polyfit(x, y, 1)
    print("Line of best fit")
    print(np.round(a, 2), "* x +", np.round(b, 2))
    plt.plot(x, np.multiply(a, x) + b)
    plt.ylabel("Mean Pressure Error (hPa)")
    plt.xlabel("Elevation Error (m)")
    plt.show()

    print("Pearson Correlation Coefficient")
    res = stats.pearsonr(x, y)
    print(res)


def era5():
    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])
    long = 360 + long

    da = xr.open_dataset("era5_geopot_grib.grib")
    da = da.sel(longitude=long, latitude=lat, method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["location", "Station", "elevation"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    # print(df["z"])

    # df["z"] = df["z"] / 9.80665
    df["z"] = (6371229 * (df["z"] / 9.80665)) / (6371229 - (df["z"] / 9.80665))
    df = df.rename(columns={"z": "era5_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["era5_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)
    df["abs_elevation"] = df["elevation_err"].abs()
    df = df.sort_values(by=["abs_elevation"], ascending=False)

    elevation_means = pd.read_csv("pressure_means.csv")
    elevation_means = elevation_means[["location", "value"]]
    df = df.merge(elevation_means, how="left", left_on="Station", right_on="location")

    df = df[["Station", "stn_elevation", "era5_elevation", "elevation_err", "value"]]

    df = df[df["value"].notna()]
    x = df["elevation_err"].tolist()
    y = df["value"].tolist()

    plt.scatter(x, y)
    a, b = np.polyfit(x, y, 1)
    print("Line of best fit")
    print(np.round(a, 2), "* x +", np.round(b, 2))
    plt.plot(x, np.multiply(a, x) + b)
    plt.ylabel("Mean Pressure Error (hPa)")
    plt.xlabel("Elevation Error (m)")
    plt.show()

    print("Pearson Correlation Coefficient")
    res = stats.pearsonr(x, y)
    print(res)


def pretty_merra_era():
    plt.style.use("ggplot")
    plt.rcParams['axes.facecolor'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'dimgrey'
    plt.rcParams['grid.color'] = 'lightgrey'

    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

    # Merra2
    da = xr.open_dataset("merra2_geopotential.nc4")
    da = da.sel(lon=long, lat=lat, time="1980-01-15 12:00:00", method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["StnID", "location", "Station", "elevation"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    df["PHIS"] = (6371229 * (df["PHIS"] / 9.80665)) / (6371229 - (df["PHIS"] / 9.80665))
    df = df.rename(columns={"PHIS": "merra_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["merra_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)
    df["abs_elevation"] = df["elevation_err"].abs()
    df = df.sort_values(by=["abs_elevation"], ascending=False)

    elevation_means = pd.read_csv("merra_pressure_means.csv")
    elevation_means = elevation_means[["StnID", "value"]]
    df = df.merge(elevation_means, how="left", left_on="StnID", right_on="StnID")

    df = df[["Station", "stn_elevation", "merra_elevation", "elevation_err", "value"]]

    df = df[df["value"].notna()]
    x = df["elevation_err"].tolist()
    y = df["value"].tolist()

    plt.scatter(x, y, linewidths=0, s=10, c=["orange"], label="MERRA-2")
    a, b = np.polyfit(x, y, 1)
    print("Merra2 Line of best fit")
    print(np.round(a, 2), "* x +", np.round(b, 2))
    print("Pearson Correlation Coefficient")
    res = stats.pearsonr(x, y)
    print(res)
    plt.plot(x, np.multiply(a, x) + b, c="orange", alpha=0.5)

    print(min(x), max(x))

    # era5
    long = 360 + long
    da = xr.open_dataset("era5_geopot_grib.grib")
    da = da.sel(longitude=long, latitude=lat, method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    df = df.merge(stn_metadata, how="left", on="location")

    df["z"] = (6371229 * (df["z"] / 9.80665)) / (6371229 - (df["z"] / 9.80665))
    df = df.rename(columns={"z": "era5_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["era5_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)
    df["abs_elevation"] = df["elevation_err"].abs()
    df = df.sort_values(by=["abs_elevation"], ascending=False)

    elevation_means = pd.read_csv("era5_pressure_means.csv")
    elevation_means = elevation_means[["StnID", "value"]]
    df = df.merge(elevation_means, how="left", left_on="StnID", right_on="StnID")

    df = df[["Station", "stn_elevation", "era5_elevation", "elevation_err", "value"]]

    df = df[df["value"].notna()]
    x = df["elevation_err"].tolist()
    y = df["value"].tolist()

    plt.scatter(x, y, linewidths=0, s=10, c=["blue"], label="ERA5-Land", alpha=0.5)
    a, b = np.polyfit(x, y, 1)
    print("Era5 Line of best fit")
    print(np.round(a, 2), "* x +", np.round(b, 2))
    print("Pearson Correlation Coefficient")
    res = stats.pearsonr(x, y)
    print(res)
    plt.plot(x + [-158.6, 97.9], np.multiply(a, x + [-158.6, 97.9]) + b, c="blue", alpha=0.5)

    # plt.title("Correlation of Station's Elevation Error and Pressure MBE")
    plt.ylabel("Pressure MBE (hPa)")
    plt.xlabel("Elevation Error (m)")
    plt.legend()
    plt.show()


def mapped_merra():
    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

    da = xr.open_dataset("merra2_geopotential.nc4")
    da = da.sel(lon=long, lat=lat, time="1980-01-15 12:00:00", method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["location", "Station", "elevation", "LatDD", "LongDD"]]
    stn_metadata[["stn_lat", "stn_lon"]] = stn_metadata[["LatDD", "LongDD"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    df["PHIS"] = (6371229 * (df["PHIS"] / 9.80665)) / (6371229 - (df["PHIS"] / 9.80665))
    df = df.rename(columns={"PHIS": "merra_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["merra_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)

    print(df.columns)

    color_scale = [(0, 'blue'), (1, 'red')]
    fig = px.scatter_mapbox(df,
                            lat="stn_lat",
                            lon="stn_lon",
                            hover_name=df.Station.tolist(),
                            color="elevation_err",
                            color_continuous_scale=color_scale,
                            size=np.abs(df["elevation_err"]),
                            size_max=25,
                            opacity=0.60)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 80, "l": 0, "b": 0})
    fig.write_html("merra_elevation_err.html")


def mapped_era5():
    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])
    long = 360 + long

    da = xr.open_dataset("era5_geopot_grib.grib")
    da = da.sel(longitude=long, latitude=lat, method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["location", "Station", "elevation", "LatDD", "LongDD"]]
    stn_metadata[["stn_lat", "stn_lon"]] = stn_metadata[["LatDD", "LongDD"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    df["z"] = (6371229 * (df["z"] / 9.80665)) / (6371229 - (df["z"] / 9.80665))
    df = df.rename(columns={"z": "era5_elevation"})
    df["elevation_err"] = df["stn_elevation"] - df["era5_elevation"]
    df["elevation_err"] = df["elevation_err"].round(1)

    print(df.columns)

    color_scale = [(0, 'blue'), (1, 'red')]
    fig = px.scatter_mapbox(df,
                            lat="stn_lat",
                            lon="stn_lon",
                            hover_name=df.Station.tolist(),
                            color="elevation_err",
                            color_continuous_scale=color_scale,
                            size=np.abs(df["elevation_err"]),
                            size_max=25,
                            opacity=0.60)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 80, "l": 0, "b": 0})
    fig.write_html("era5_elevation_err.html")


def mapped_elevation():
    # An array which holds metadata that is not recorded in the hourly table.
    # Includes name, id (station number), longitude, and latitude
    stn_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata = stn_metadata_preprocessing(stn_metadata)

    # lat and long are pairs of the stations latitude and longitude
    # coordinates. Each list is in order so that if you access index
    # i of each array then it will be the coordinate for the ith
    # weather station
    lat = xr.DataArray(stn_metadata['LatDD'].tolist(), dims=['location'])
    long = xr.DataArray(stn_metadata['LongDD'].tolist(), dims=['location'])

    da = xr.open_dataset("merra2_geopotential.nc4")
    da = da.sel(lon=long, lat=lat, time="1980-01-15 12:00:00", method="nearest")
    df = da.to_dataframe()
    df = df.reset_index()

    stn_metadata = stn_metadata[["location", "Station", "elevation"]]
    stn_metadata = stn_metadata.rename(columns={"elevation": "stn_elevation"})

    df = df.merge(stn_metadata, how="left", on="location")

    df["PHIS"] = (6371229 * (df["PHIS"] / 9.80665)) / (6371229 - (df["PHIS"] / 9.80665))
    df = df.rename(columns={"PHIS": "merra_elevation"})
    df["merra_elevation"] = df["merra_elevation"].round(2)
    df["merra_elevation_err"] = (df["stn_elevation"] - df["merra_elevation"]).round(2)

    long = 360 + long
    da = xr.open_dataset("era5_geopot_grib.grib")
    da = da.sel(longitude=long, latitude=lat, method="nearest")
    df_era5 = da.to_dataframe()
    df_era5 = df_era5.reset_index()

    df = df.merge(df_era5, how="outer", on="location")

    df["z"] = (6371229 * (df["z"] / 9.80665)) / (6371229 - (df["z"] / 9.80665))
    df = df.rename(columns={"z": "era5_elevation"})
    df["era5_elevation"] = df["era5_elevation"].round(2)
    df["era5_elevation_err"] = (df["stn_elevation"] - df["era5_elevation"]).round(2)

    df = df[
        ["Station", "stn_elevation", "merra_elevation", "merra_elevation_err", "era5_elevation", "era5_elevation_err"]]

    df.to_csv("mapped_elevation.csv", index=False)


if __name__ == "__main__":
    process_data()
    # merra()
    # era5()
    # pretty_merra_era()
    # mapped_merra()
    # mapped_era5()
    mapped_elevation()
