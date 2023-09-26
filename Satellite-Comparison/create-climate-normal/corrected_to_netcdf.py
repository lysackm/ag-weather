import sqlite3
import glob
import pandas as pd
import xarray as xr


def merge_netcdf():
    files = glob.glob('../../../data/historical_era5/corrected_netcdf/*.nc')

    datasets = [xr.open_dataset(file) for file in files]

    merged_dataset = xr.concat(datasets, dim=["time", "latitude", "longitude"])
    merged_dataset.to_netcdf("merged_dataset.nc")


def csv_to_netcdf():
    attrs = ["_AvgAir_T", "_AvgWS", "_Pluvio_Rain", "_Press_hPa", "_RH", "_SolarRad"]

    data_dir = '../../../data/historical_era5/'

    for year in range(1980, 2023):

        datasets = []

        for attr_name in attrs:
            # load as a dataframe
            df = pd.read_csv(data_dir + "corrected/" + str(year) + attr_name + ".csv")
            # index by time, lat, long
            # transform to dataset
            ds = df.set_index(['time', 'latitude', 'longitude']).to_xarray()
            datasets.append(ds)

        # merge (xarray merge) datasets together
        ds_merged = xr.merge(datasets)
        # save as netcdf file
        ds_merged.to_netcdf(data_dir + "corrected_netcdf/" + str(year) + ".nc")


csv_to_netcdf()
# merge_netcdf()
