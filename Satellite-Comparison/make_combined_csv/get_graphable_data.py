import glob
import math
from datetime import datetime

import pandas as pd
from dateutil import relativedelta
from matplotlib import pyplot as plt


# get_line_chart_data
#
# Function that creates files that is able to graphed on a line graph. Format of the
# output file is that each column is representing a station and each index step represents
# one month. So the data is one-month steps starting from 2018-01-01 to 2023-01-01, with
# the monthly average being the value stored.
#
# The RMSE is calculated by taking the mean of the squared error for the month
# in question, then taking the square root of that mean.
def get_line_chart_data():
    stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
    stn_metadata["StationName"] = stn_metadata["StationName"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))

    stn_names = stn_metadata["StationName"]

    files = glob.glob("output/*.csv")

    delta = relativedelta.relativedelta(months=1)
    start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    merra_sqr_err_df = pd.DataFrame()
    era5_sqr_err_df = pd.DataFrame()
    merra_err_df = pd.DataFrame()
    era5_err_df = pd.DataFrame()

    for file in files:
        attr_df = pd.read_csv(file)
        attr_df["time"] = pd.to_datetime(attr_df["time"])

        for station in stn_names:
            index = []
            merra_sqr_col = []
            merra_err_col = []
            era5_sqr_col = []
            era5_err_col = []

            stn_df = attr_df[attr_df["Station"] == station]
            while start_date < end_date:
                start_date += delta
                date_df = stn_df[(stn_df["time"] >= start_date) & (stn_df["time"] < (start_date + delta))]

                if "merra_sqr_err" in date_df.columns:
                    merra_monthly_rmse = date_df["merra_sqr_err"].mean() ** 0.5
                    merra_sqr_col.append(merra_monthly_rmse)
                    merra_err_col.append(date_df["merra_err"].mean())
                if "era5_sqr_err" in date_df.columns:
                    era5_monthly_rmse = date_df["era5_sqr_err"].mean() ** 0.5
                    era5_sqr_col.append(era5_monthly_rmse)
                    era5_err_col.append(date_df["era5_err"].mean())

                index.append(start_date)

            start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

            if "merra_sqr_err" in date_df.columns:
                merra_sqr_err_df[station] = merra_sqr_col
                merra_err_df[station] = merra_err_col
            if "era5_sqr_err" in date_df.columns:
                era5_sqr_err_df[station] = era5_sqr_col
                era5_err_df[station] = era5_err_col
            # add column

        # save csv with the data in it
        if "era5_sqr_err" in date_df.columns:
            era5_sqr_err_filename = "./sqr-err/era5_" + file.replace("output\\", "")
            era5_err_filename = "./err/era5_" + file.replace("output\\", "")

            era5_sqr_err_df.to_csv(era5_sqr_err_filename, index=False)
            era5_err_df.to_csv(era5_err_filename, index=False)
            print(era5_sqr_err_filename)

        if "merra_sqr_err" in date_df.columns:
            merra_sqr_err_filename = "./sqr-err/merra_" + file.replace("output\\", "")
            merra_err_filename = "./err/merra_" + file.replace("output\\", "")

            merra_sqr_err_df.to_csv(merra_sqr_err_filename)
            merra_err_df.to_csv(merra_err_filename)
            print(merra_sqr_err_filename)


# get_line_chart_data_daily
#
# Function that creates graph-able data from the merged csvs. Data is formatted
# where columns are stations and the index represents one-day steps. Each value
# is a single days average for that station. Create files for both unmodified error
# and root-mean-square error values.
#
# The RMSE is calculated by taking the mean of the squared error for the day
# in question, then taking the square root of that mean.
def get_line_chart_data_daily():
    files = glob.glob("output/*.csv")

    for file in files:
        merra_sqr_err_df = pd.DataFrame()
        era5_sqr_err_df = pd.DataFrame()
        merra_err_df = pd.DataFrame()
        era5_err_df = pd.DataFrame()

        attr_df = pd.read_csv(file)
        attr_df["time"] = pd.to_datetime(attr_df["time"])
        attr_df.set_index(attr_df["time"], inplace=True)

        try:
            grouped_series = attr_df.groupby([attr_df.index.year,
                                              attr_df.index.month,
                                              attr_df.index.day,
                                              attr_df["Station"]])[["merra_err",
                                                                    "merra_sqr_err",
                                                                    "era5_err",
                                                                    "era5_sqr_err"]].mean()
            grouped_series[["merra_sqr_err", "era5_sqr_err"]] = grouped_series[["merra_sqr_err", "era5_sqr_err"]].pow(0.5)
        except:
            if "merra_sqr_err" in attr_df.columns:
                grouped_series = attr_df.groupby([attr_df.index.year,
                                                  attr_df.index.month,
                                                  attr_df.index.day,
                                                  attr_df["Station"]])[["merra_err", "merra_sqr_err"]].mean()
                grouped_series["merra_sqr_err"] = grouped_series["merra_sqr_err"].pow(0.5)

            if "era5_sqr_err" in attr_df.columns:
                grouped_series = attr_df.groupby([attr_df.index.year,
                                                  attr_df.index.month,
                                                  attr_df.index.day,
                                                  attr_df["Station"]])[["era5_err", "era5_sqr_err"]].mean()
                grouped_series["era5_sqr_err"] = grouped_series["era5_sqr_err"].pow(0.5)

            if "era5_sqr_err" not in attr_df.columns and "merra_sqr_err" not in attr_df.columns:
                print("This shouldnt happen, no comparison to merra or era5 done on this data")
                exit(1)

        grouped_series = grouped_series.reorder_levels(["Station", 0, 1, 2])

        for station in set(grouped_series.index.get_level_values('Station')):
            stn_df = grouped_series.loc[station]

            if "merra_sqr_err" in stn_df.columns:
                merra_sqr_err_df[station] = stn_df["merra_sqr_err"]
                merra_err_df[station] = stn_df["merra_err"]
            if "era5_sqr_err" in stn_df.columns:
                era5_sqr_err_df[station] = stn_df["era5_sqr_err"]
                era5_err_df[station] = stn_df["era5_err"]

        # save csv with the data in it
        if "era5_sqr_err" in attr_df.columns:
            era5_sqr_err_filename = "./daily/sqr-err/era5_" + file.replace("output\\", "")
            era5_err_filename = "./daily/err/era5_" + file.replace("output\\", "")

            era5_sqr_err_df.to_csv(era5_sqr_err_filename)
            era5_err_df.to_csv(era5_err_filename)

            print(era5_sqr_err_filename)

        if "merra_sqr_err" in attr_df.columns:
            merra_sqr_err_filename = "./daily/sqr-err/merra_" + file.replace("output\\", "")
            merra_err_filename = "./daily/err/merra_" + file.replace("output\\", "")

            merra_sqr_err_df.to_csv(merra_sqr_err_filename)
            merra_err_df.to_csv(merra_err_filename)

            print(merra_sqr_err_filename)


# get_map_data
#
# Function to create data files that is able to be mapped using the plotly library.
# Data format is rows of data with identifying information (date, station). All stations
# are in 1 file.
def get_map_data():
    stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
    stn_metadata["StationName"] = stn_metadata["StationName"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))

    stn_names = stn_metadata["StationName"]

    files = glob.glob("output/*.csv")

    delta = relativedelta.relativedelta(months=1)
    start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime("2022-12-31 00:00:00", "%Y-%m-%d %H:%M:%S")

    # df = pd.DataFrame(columns=["Station", "time", "stn_long", "stn_lat", "era5_err", "era5_sqr_err"])

    for file in files:
        attr_col = "stn_" + file.replace("_output.csv", "").replace("output\\", "")

        row_list = []
        attr_df = pd.read_csv(file)
        attr_df["time"] = pd.to_datetime(attr_df["time"])

        for station in stn_names:

            stn_df = attr_df[attr_df["Station"] == station]

            try:
                stn_long = stn_df["stn_long"].iloc[0]
                stn_lat = stn_df["stn_lat"].iloc[0]
            except Exception as e:
                print(e)
                print(stn_df)

            while start_date <= end_date:
                start_date += delta
                date_df = stn_df[(stn_df["time"] >= start_date) & (stn_df["time"] < (start_date + delta))]

                if "merra_sqr_err" in date_df.columns:
                    merra_rmse = math.sqrt(date_df["merra_sqr_err"].mean())
                    merra_err = date_df["merra_err"].mean()
                if "era5_sqr_err" in date_df.columns:
                    era5_rmse = math.sqrt(date_df["era5_sqr_err"].mean())
                    era5_err = date_df["era5_err"].mean()

                row_list.append({"Station": station,
                                 "time": start_date,
                                 "stn_long": stn_long,
                                 "stn_lat": stn_lat,
                                 "stn_attr": date_df[attr_col].mean(),
                                 "merra_err": merra_err,
                                 "era5_err": era5_err,
                                 "merra_sqr_err": merra_rmse,
                                 "era5_sqr_err": era5_rmse})

            start_date = datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

        df = pd.DataFrame(row_list)
        df.to_csv("./map_graph_data/" + file.replace("output\\", ""))
        print("./map_graph_data/" + file.replace("output\\", ""))


# call the function that you want to generate the new data

get_line_chart_data_daily()
get_map_data()
get_line_chart_data()
