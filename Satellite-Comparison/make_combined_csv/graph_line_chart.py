import glob

import numpy
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
        if not numpy.isnan(x).all():
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
        if not numpy.isnan(df).all().all():
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
