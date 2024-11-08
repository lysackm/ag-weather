from datetime import datetime
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import nan


# graph the mean bias for all the attributes. One graph will have both
# data from MERRA and ERA5-Land. The data spans all 5 years and one point in
#  the scatter plot represents the average of the mean bias for tha single day
def graph_mean_comparison():
    root_path = "D:\\data\\graphs\\scatter_plots\\"
    attrs = ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH"]
    titles = ['Air Temperature ($^\circ$C)', "Wind Speed (m/s)", "Precipitation (mm)",
              "Pressure (hPa)", "Relative Humidity (%)"]
    y_titles = ["$^\circ$C", "m/s", "mm", "hPa", "%"]

    plt.style.use("ggplot")
    plt.rcParams['axes.facecolor'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'dimgrey'
    plt.rcParams['grid.color'] = 'lightgrey'
    i = 0
    for attr, title, y_title in zip(attrs, titles, y_titles):
        print(attr)

        x = []
        # graph era5
        file = "daily/err/merra_" + attr + "_output.csv"
        df = pd.read_csv(file, parse_dates={"date": ["time", "time.1", "time.2"]})
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

        dates = df.index
        x_axis = pd.date_range(start="2018-01-01", periods=365*5 + 1, freq="d")

        for date in x_axis:
            try:
                daily_df = df[df.index == date]

                x.append(daily_df.iloc[0].mean(axis=0, skipna=True))
                # print(no_nan_df.mean(axis=0, skipna=True))
            except (KeyError, IndexError):
                x.append(np.nan)

        i += 1
        ax = plt.subplot(2, 3, i)
        ax.scatter(x_axis, x, linewidths=0, s=10, c=["orange"], label="MERRA-2")

        x = []
        file = "daily/err/era5_" + attr + "_output.csv"
        df = pd.read_csv(file, parse_dates={"date": ["time", "time.1", "time.2"]})

        dates = df["date"]

        for date in df.index:

            # drop index column
            try:
                df_no_index = df.drop(columns="date")
            except KeyError:
                df_no_index = df

            daily_df = df_no_index.loc[date]
            no_nan_df = daily_df.dropna()

            # append mean of all values if values exist
            if no_nan_df.size == 1:
                x.append(nan)
            else:
                x.append(no_nan_df.mean(axis=0, skipna=True))

        ax.scatter(dates, x, linewidths=0, s=10, c=["blue"], label="ERA5-Land", alpha=0.5)
        ax.set_title(title)
        ax.set(xlim=[datetime(2017, 10, 1), datetime(2023, 4, 1)], ylabel=y_title)
        # plt.xlim([datetime(2017, 10, 1), datetime(2023, 4, 1)])
        # plt.ylabel(y_title)
        # plt.legend()
        # plt.savefig(root_path + attr + ".png")
        # plt.clf()

    leg = plt.legend(prop={"size": 15})
    leg.set_draggable(True)
    plt.show()


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
                x.append(nan)
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
                filename = root_path + file.replace("_output.csv", ".png").replace("./sqr-err", "") \
                    .replace("daily", "daily\\mean")
            else:
                filename = root_path + file.replace("_output.csv", ".png").replace("./err", "") \
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
                    dates = pd.date_range(start="2018-01-01", periods=60, freq="ME")

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
    titles = {"AvgAir_T": 'Air Temperature ($^\\circ$C)', "AvgWS": "Wind Speed (m/s)", "Pluvio_Rain": "Precipitation (mm)",
              "Press_hPa": "Pressure (hPa)", "RH": "Relative Humidity (%)", "SolarRad": "Solar Radiation (mJ/m$^2$)"}
    y_titles = {"AvgAir_T": '$^\\circ$C', "AvgWS": "m/s", "Pluvio_Rain": "mm",
                "Press_hPa": "hPa", "RH": "%", "SolarRad": "mJ/m$^2$"}

    x_axis = range(24)
    files = glob.glob("output/*.csv")
    root_path = "D:\\data\\graphs\\interesting\\hourly_avg\\"

    data_fetched = ["merra_err", "era5_err"]
    plt.style.use("ggplot")
    plt.rcParams['axes.facecolor'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'dimgrey'
    plt.rcParams['grid.color'] = 'lightgrey'
    i = 0
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
        result = date_index.groupby([date_index.index.hour])[mean_cols].mean()
        print(file)

        orange = result[data_fetched[0]].tolist()
        orange = orange[-6:] + orange[:-6]
        print("Merrra", orange)
        blue = result[data_fetched[1]].tolist()
        blue = blue[-6:] + blue[:-6]
        print("era5", blue)

        # plot both err and sqr-err
        filename = root_path + "err\\hourly_" + file.replace("_output.csv", ".png").replace(
            "D:/data/processed-data\\", "").replace("output\\", "")
        i += 1
        ax = plt.subplot(2, 3, i)
        ax.plot(x_axis, orange, c="orange")
        ax.plot(x_axis, blue, c="blue")
        ax.set_title(titles[file.replace("D:/data/processed-data\\", "").replace("_output.csv", "").replace("output\\", "")])
        ax.set(xlabel="Hour of Day (CST)", ylabel=y_titles[file.replace("D:/data/processed-data\\", "").replace("_output.csv", "").replace("output\\", "")])

        print("Merra", max(result[data_fetched[0]]) - min(result[data_fetched[0]]))
        print("Era5", max(result[data_fetched[1]]) - min(result[data_fetched[1]]))
        #
        # filename = root_path + "sqr-err\\hourly_" + file.replace("_output.csv", ".png").replace(
        #     "D:/data/processed-data\\", "").replace("output\\", "")
        # plt.plot(x_axis, np.sqrt(result[data_fetched[0].replace("_err", "_sqr_err")]), c="orange")
        # plt.plot(x_axis, np.sqrt(result[data_fetched[1].replace("_err", "_sqr_err")]), c="blue")
        # plt.title(titles[file.replace("D:/data/processed-data\\", "").replace("_output.csv", "").replace("output\\", "")])
        # plt.legend(["MERRA-2", "ERA5-Land"])
        # plt.savefig(filename)
        # plt.clf()

    leg = plt.legend(["MERRA-2", "ERA5-Land"], prop={"size": 15})
    leg.set_draggable(True)
    plt.show()


def generate_all_graphs():
    graph_all_stns(True, False)
    graph_all_stns(True, True)
    graph_all_stns(False, False)
    graph_all_stns(False, True)

    graph_mean(True, False)
    graph_mean(True, True)
    graph_mean(False, False)
    graph_mean(False, True)


# generate_all_graphs()
get_averaged_time()
# graph_mean_comparison()

