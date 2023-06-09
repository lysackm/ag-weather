import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import NaN


# graph_mean
#
# Used to generate graphs which take a mean value of all the stations over the given time period
# Will graph based off of the data in the directories called daily, err, and sqr-err where this
# file is. Output is in a separate directory
def graph_mean(is_sqr=False, is_daily=False):
    # file directory of where data is for each type of
    if is_daily:
        if is_sqr:
            file_loc = "daily/sqr-err/*.csv"
        else:
            file_loc = "daily/err/*.csv"
    else:
        if is_sqr:
            file_loc = "sqr-err/*.csv"
        else:
            file_loc = "err/*.csv"

    files = glob.glob(file_loc)

    for file in files:
        x = []

        if is_daily:
            df = pd.read_csv(file, parse_dates={"date": ["time", "time.1", "time.2"]})
        else:
            df = pd.read_csv(file)

        for date_delta in df.index:
            # drop index column
            try:
                if is_daily:
                    df_no_index = df.drop(columns="date")
                else:
                    df_no_index = df.drop(columns="Unnamed: 0")
            except KeyError:
                df_no_index = df

            month_df = df_no_index.loc[date_delta]
            no_nan_df = month_df.dropna()

            # append mean of all values if values exist
            if no_nan_df.size == 1:
                x.append(NaN)
            else:
                x.append(no_nan_df.mean(axis=0, skipna=True))

        # get index
        if is_daily:
            dates = df["date"]
        else:
            dates = pd.date_range(start="2018-01-01", periods=60, freq="M")

        # plot data
        plt.plot(dates, x)

        # label graph appropriately
        if is_sqr:
            plt.title(file.replace("./sqr-err\\", "").replace("_output.csv", ""))
            plt.ylabel("root mean square error")
        else:
            plt.title(file.replace("./err\\", "").replace("_output.csv", ""))
            plt.ylabel("mean error")

        plt.xlabel("time")
        plt.grid()

        # absolute path, change variable for local machine
        root_path = "D:\\data\\graphs\\"

        if is_daily:
            if is_sqr:
                filename = root_path + file.replace("_output.csv", ".png").replace("./sqr-err", "")\
                    .replace("daily", "daily\\mean")
            else:
                filename = root_path + file.replace("_output.csv", ".png").replace("./err", "")\
                    .replace("daily", "daily\\mean")
        else:
            if is_sqr:
                filename = root_path + "mean\\" + file.replace("_output.csv", ".png").replace("./err", "")
            else:
                filename = root_path + "mean\\" + file.replace("_output.csv", ".png").replace("./err", "")
        print(filename)

        # if the graph isn't empty save it
        if not np.isnan(x).all():
            plt.savefig(filename)
        plt.clf()


# graph all the stations onto one graph.
# Will graph based off of the data in the directories called daily, err, and sqr-err where this
# file is. Output is in a separate directory
def graph_all_stns(is_sqr=False, is_daily=False):
    if is_daily:
        if is_sqr:
            file_loc = "daily/sqr-err/*.csv"
        else:
            file_loc = "daily/err/*.csv"
    else:
        if is_sqr:
            file_loc = "sqr-err/*.csv"
        else:
            file_loc = "err/*.csv"

    files = glob.glob(file_loc)

    for file in files:
        if is_daily:
            df = pd.read_csv(file, parse_dates={"date": ["time", "time.1", "time.2"]})
        else:
            df = pd.read_csv(file)

        for station in df.columns:
            if station != "Unnamed: 0" and station != "date":

                # get data and graph each station
                if is_daily:
                    # dates = pd.date_range(start="2018-01-01", periods=len(df[station]), freq="D")
                    dates = df["date"]
                else:
                    dates = pd.date_range(start="2018-01-01", periods=60, freq="M")

                plt.plot(dates, df[station], label=station)
                # plt.title(station)
                # plt.show()

        if is_sqr:
            plt.title(file.replace("./sqr-err\\", "").replace("_output.csv", ""))
            plt.ylabel("root mean square error")
        else:
            plt.title(file.replace("./err\\", "").replace("_output.csv", ""))
            plt.ylabel("mean error")

        plt.xlabel("time")
        plt.grid()

        root_path = "D:\\data\\graphs\\"
        if is_sqr:
            filename = root_path + file.replace("_output.csv", ".png").replace("./sqr-err", "")
        else:
            filename = root_path + file.replace("_output.csv", ".png").replace("./err", "")
        print(filename)
        if not np.isnan(df).all().all():
            plt.savefig(filename)
        plt.clf()


# Get the root-mean-square error data averaged over the 5 years for varying time
# differences. Can be set to be yearly average, monthly average, daily average,
# or hourly average (single point). If you want to change the time then some slight
# modifications of the function will have to be made
def get_averaged_time():
    dates = pd.date_range(start="2018-01-01", periods=744, freq="H")
    files = glob.glob("D:/data/processed-data/*.csv")
    root_path = "D:\\data\\graphs\\interesting\\month_hourly_avg\\"

    data_fetched = ["era5_err", "merra_err"]

    for file in files:
        attr_df = pd.read_csv(file)
        attr_df["time"] = pd.to_datetime(attr_df["time"])

        columns = attr_df.columns

        # get the right columns depending on the attr
        if "merra_err" in columns and "era5_err" in columns:
            filtered = attr_df[
                ["Station", "stn_long", "stn_lat", "merra_err", "merra_sqr_err", "era5_err", "era5_sqr_err"]]
            mean_cols = ["merra_err", "merra_sqr_err", "era5_err", "era5_sqr_err"]
        elif "merra_err" in columns:
            filtered = attr_df[["Station", "stn_long", "stn_lat", "merra_err", "merra_sqr_err"]]
            mean_cols = ["merra_err", "merra_sqr_err"]
        elif "era5_err" in columns:
            filtered = attr_df[["Station", "stn_long", "stn_lat", "era5_err", "era5_sqr_err"]]
            mean_cols = ["era5_err", "era5_sqr_err"]
        else:
            print("no comparison to merra or era dont, this should not happen")
            exit(1)

        date_index = filtered.set_index(attr_df["time"])

        # change this line to change where the average is happening
        result = date_index.groupby([date_index.index.day, date_index.index.hour])[mean_cols].mean()
        print(file)

        for attr in data_fetched:
            if attr in columns:
                # plot both err and sqr-err
                filename = root_path + "err\\" + file.replace("_output.csv", ".png").replace(
                    "D:/data/processed-data\\", attr)
                plt.plot(dates, result[attr], linewidth=0.5)
                plt.title(file.replace("D:/data/processed-data\\", "").replace("_output.csv", "") + " " + attr)
                plt.savefig(filename)
                plt.clf()

                filename = root_path + "sqr-err\\" + file.replace("_output.csv", ".png").replace(
                    "D:/data/processed-data\\", attr)
                plt.plot(dates, np.sqrt(result[attr.replace("_err", "_sqr_err")]), linewidth=0.5)
                plt.title(file.replace("D:/data/processed-data\\", "").replace("_output.csv", "") + " " + attr.replace(
                    "_err", "_sqr_err"))
                plt.savefig(filename)
                plt.clf()


def generate_all_graphs():
    graph_all_stns(True, False)
    graph_all_stns(True, True)
    graph_all_stns(False, False)
    graph_all_stns(False, True)

    graph_mean(True, False)
    graph_mean(True, True)
    graph_mean(False, False)
    graph_mean(False, True)


generate_all_graphs()
get_averaged_time()
