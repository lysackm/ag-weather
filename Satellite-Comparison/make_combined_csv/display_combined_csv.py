import glob
import math
from datetime import date, datetime

import pandas as pd
from dateutil import relativedelta

stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
stn_metadata["StationName"] = stn_metadata["StationName"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))

stn_names = stn_metadata["StationName"]

files = glob.glob("D:/data/processed-data/*.csv")

delta = relativedelta.relativedelta(months=1)
start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
end_date = datetime.strptime("2022-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")

merra_df = pd.DataFrame()
era5_df = pd.DataFrame()

for file in files:
    attr_df = pd.read_csv(file)
    attr_df["time"] = pd.to_datetime(attr_df["time"])

    for station in stn_names:
        index = []
        merra_col = []
        era5_col = []

        stn_df = attr_df[attr_df["Station"] == station]
        while start_date <= end_date:
            start_date += delta
            date_df = stn_df[(stn_df["time"] >= start_date) & (stn_df["time"] < (start_date + delta))]

            if "merra_err" in date_df.columns:
                merra_monthly_rmse = date_df["merra_err"].mean()
                merra_col.append(merra_monthly_rmse)
            if "era5_err" in date_df.columns:
                era5_monthly_rmse = date_df["era5_err"].mean()
                era5_col.append(era5_monthly_rmse)

            index.append(start_date)

        start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

        if "merra_err" in date_df.columns:
            merra_df[station] = merra_col
        if "era5_err" in date_df.columns:
            era5_df[station] = era5_col
        # add column

    # save csv with the data in it
    merra_filename = "./err/merra_" + file.replace("D:/data/processed-data\\", "")
    era5_filename = "./err/era5_" + file.replace("D:/data/processed-data\\", "")
    print(merra_filename)
    print(era5_filename)
    era5_df.to_csv(era5_filename)
    merra_df.to_csv(merra_filename)
