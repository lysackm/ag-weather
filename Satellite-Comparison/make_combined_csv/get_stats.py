import glob
import json

import pandas as pd
import numpy as np
import plotly.express as px
from enum import Enum
import matplotlib.pyplot as plt


# enum which represents the types of data which statistics can
# be created for
class DataType(Enum):
    raw = "raw"
    lin_reg = "linear_regression"
    mean_err = "mean_error"
    rand_forest = "random_forest"


attr_names = {"output\\AvgAir_T_output.csv": "Air Temperature", "output\\AvgWS_output.csv": "Wind Speed",
              "output\\Pluvio_Rain_output.csv": "Precipitation", "output\\Press_hPa_output.csv": "Pressure",
              "output\\RH_output.csv": "Relative Humidity"}


# generic_performance
#
# Find the root-mean-square of the entire attribute, over all stations
# over all time
# returns a single number
def generic_performance(df, col):
    return np.sqrt(df[col].mean())


# generic_performance_mbe
#
# Find the mean-bias-error of the entire attributes, over all stations
# over all time
# returns a single number
def generic_performance_mbe(df, col):
    mbe = df[col].mean()
    return mbe


# seasonal_breakdown
#
# Break down data into seasons of 3 months. Then find the root-mean-square error
# for each of the seasons over all the years.
#
# Seasons are defined as:
# January - March
# April - June
# July - September
# October - December
def seasonal_breakdown(df, col):
    df["time"] = pd.to_datetime(df["time"])
    df.set_index(df["time"], inplace=True)
    all_years = df.groupby(pd.Grouper(freq='3MS', origin='start'))[col].mean()

    seasons = [[], [], [], []]
    counter = 0
    for avg in all_years:
        seasons[counter].append(avg)
        counter = (counter + 1) % 4
    for i in range(4):
        seasons[i] = np.sqrt(np.nanmean(seasons[i]))

    return seasons


# monthly_breakdown
#
# Break down data for each month. Then find the root-mean-square error
# for each of the months over all the years.
def monthly_breakdown(df, col):
    df["time"] = pd.to_datetime(df["time"])
    # df.set_index(df["time"], inplace=True)
    all_years = np.sqrt(df.groupby([df["time"].dt.month])[col].mean())

    return all_years.to_list()


# monthly_mbe_breakdown
#
# Break down data for each month. Then find the mean bias error
# for each of the months over all the years.
def monthly_mbe_breakdown(df, col):
    df["time"] = pd.to_datetime(df["time"])
    # df.set_index(df["time"], inplace=True)
    all_years = df.groupby([df["time"].dt.month])[col].mean()

    return all_years.to_list()


# spacial_correlation
#
# Data format is a dictionary where the keys are the station names
# and the values are the mean for that station. Data is average for every year for
# each station.
# Set show_graph to be true to generate graphs to represent the data on a map of
# Manitoba.
#
def spacial_correlation(df, col, show_graph=False, output_file="", title=""):
    stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata-old.csv")
    stn_metadata["StationName"] = stn_metadata["StationName"].apply(
        lambda x: x.lower().strip().replace('.', '').replace(' ', ''))

    stn_names = stn_metadata["StationName"]
    df["time"] = pd.to_datetime(df["time"])

    # is a set rn make it a dict
    stn_data = {}

    for station in stn_names:

        stn_df = df[df["Station"] == station]

        try:
            stn_long = stn_df["stn_long"].iloc[0]
            stn_lat = stn_df["stn_lat"].iloc[0]
        except Exception as e:
            print(e)

        stn_data[station] = (stn_lat, stn_long, stn_df[col].mean())

    stats_df = pd.DataFrame.from_dict(stn_data, orient='index', columns=["lat", "long", "value"])

    if show_graph:
        stats_df = stats_df.dropna()

        color_scale = [(0, 'blue'), (1, 'red')]
        fig = px.scatter_mapbox(stats_df,
                                lat="lat",
                                lon="long",
                                hover_name=stats_df.index.tolist(),
                                color="value",
                                color_continuous_scale=color_scale,
                                size=np.abs(stats_df["value"]),
                                size_max=25,
                                opacity=0.60)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 80, "l": 0, "b": 0})
        fig.write_html(output_file)

    return stn_data


# Takes the output of monthly stats and formats the string for
# LaTeX formatting.
def format_seasonal_stats(monthly_stats):
    output = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    files = glob.glob("output/*.csv")

    for file in files:
        if file in monthly_stats.keys():
            print(file)

            months = monthly_stats[file]

            for i in range(12):
                output[i] += " & " + str(months[i])

    for month in output:
        print(month + "\\\\")


# formatting the data for table one
# RMSE, MBE, PCC (pierson correlation constant) generic means
# over all hours, one value per
def format_table_one(merra_rmse, era5_rmse, merra_mbe, era5_mbe, merra_pcc, era5_pcc, merra_ex, era5_ex):
    for i in merra_rmse.keys():
        attr_name = attr_names[i]
        row = attr_name + " & " + str(merra_rmse[i]) + " & " + str(merra_mbe[i]) + " & " + str(merra_pcc[i]) + " & " + \
              str(merra_ex[i]) + " & " + str(era5_rmse[i]) + " & " + str(era5_mbe[i]) + " & " + str(era5_pcc[i]) \
              + " & " + str(era5_ex[i]) + "\\\\"
        print(row)


# formatting the data for table 2
# For each mean bias correction, linear regression, and random forest,
# show the RMSE and MBE, for Merra and Era5
def format_table_two(merra_mean_rmse, era5_mean_rmse, merra_mean_mbe, era5_mean_mbe, merra_lin_rmse, era5_lin_rmse,
                     merra_lin_mbe, era5_lin_mbe, merra_for_rmse, era5_for_rmse, merra_for_mbe, era5_for_mbe):
    for i in merra_mean_rmse.keys():
        attr_name = attr_names[i]

        row = attr_name + " & " + str(merra_mean_rmse[i]) + " & " + str(merra_mean_mbe[i]) + " & " + str(
            merra_lin_rmse[i]) + " & " + \
              str(merra_lin_mbe[i]) + " & " + str(merra_for_rmse[i]) + " & " + str(merra_for_mbe[i])

        row += "\n" + attr_name + " & " + str(era5_mean_rmse[i]) + " & " + str(era5_mean_mbe[i]) + " & " + str(
            era5_lin_rmse[i]) + " & " + \
               str(era5_lin_mbe[i]) + " & " + str(era5_for_rmse[i]) + " & " + str(era5_for_mbe[i])
        print(row)


def print_table_two():
    mean_data = print_stats(DataType.mean_err)
    lin_data = print_stats(DataType.lin_reg)
    for_data = print_stats(DataType.rand_forest)

    format_table_two(mean_data["merra_rmse"], mean_data["era5_rmse"], mean_data["merra_mbe"], mean_data["era5_mbe"],
                     lin_data["merra_rmse"], lin_data["era5_rmse"], lin_data["merra_mbe"], lin_data["era5_mbe"],
                     for_data["merra_rmse"], for_data["era5_rmse"], for_data["merra_mbe"], for_data["era5_mbe"])


def print_table_three():
    uncorrected = print_stats(DataType.raw)
    mean = print_stats(DataType.mean_err)
    lin = print_stats(DataType.lin_reg)
    rand = print_stats(DataType.rand_forest)

    format_table_three(uncorrected["monthly_merra_rmse"],
                       mean["monthly_merra_rmse"],
                       lin["monthly_merra_rmse"],
                       rand["monthly_merra_rmse"], )


def print_table_four():
    uncorrected = print_stats(DataType.raw)
    mean = print_stats(DataType.mean_err)
    lin = print_stats(DataType.lin_reg)
    rand = print_stats(DataType.rand_forest)

    format_table_three(uncorrected["monthly_era5_rmse"],
                       mean["monthly_era5_rmse"],
                       lin["monthly_era5_rmse"],
                       rand["monthly_era5_rmse"], )


def make_percent_improvements_bar_chart():
    attrs = ["Air Temperature (°C)", "Wind Speed (m/s)", "Precipitation (mm)", "Pressure (hPa)",
             "Relative Humidity (%)"]

    # percents = {
    #     "MERRA2 Mean Bias": [8.81, 11.19, -0.1, 2.65, 22.06],
    #     "MERRA2 Linear Reg": [10.14, 18.49, 4.71, 2.96, 36.68],
    #     "MERRA2 RF": [112.99, 72.87, 15.53, 432.11, 168.18],
    #     "ERA-5 Land Mean Bias": [10.61, 5.75, 0.12, 0.76, 10.68],
    #     "ERA-5 Land Linear Reg": [12.06, 7.28, 5.73, 0.87, 14.31],
    #     "ERA-5 Land RF": [83.62, 60.21, 10, 152.53, 83.79]
    # }
    # percents = {
    #     "MERRA-2 Mean Bias Correction": [9, 11, 0, 3, 22],
    #     "MERRA-2 Linear Regression Correction": [10, 18, 5, 3, 37],
    #     "MERRA-2 Random Forest Correction": [113, 73, 16, 432, 168],
    #     "ERA5-Land Mean Bias Correction": [11, 6, 0, 1, 11],
    #     "ERA5-Land Linear Regression Correction": [12, 7, 6, 1, 14],
    #     "ERA5-Land Random Forest Correction": [84, 60, 10, 153, 84]
    # }
    percents = {
        "MERRA-2 Mean Bias Correction": [8, 11, 0, 4, 18],
        "MERRA-2 Linear Regression Correction": [8, 17, 0, 4, 27],
        "MERRA-2 Random Forest Correction": [54, 44, 0, 80, 63],
        "ERA5-Land Mean Bias Correction": [10, 6, 0, 0, 10],
        "ERA5-Land Linear Regression Correction": [10, 13, 0, 0, 13],
        "ERA5-Land Random Forest Correction": [43, 38, 0, 62, 46]
    }
    # percents = {
    #     "MERRA-2 Mean Bias Correction": [8, 10, 0, 3, 18],
    #     "MERRA-2 Linear Regression Correction": [9, 16, 5, 3, 27],
    #     "MERRA-2 Random Forest Correction": [53, 42, 14, 81, 63],
    #     "ERA5-Land Mean Bias Correction": [10, 5, 0, 1, 10],
    #     "ERA5-Land Linear Regression Correction": [11, 6.8, 5, 0, 13],
    #     "ERA5-Land Random Forest Correction": [46, 38, 9, 60, 40]
    # }

    colors = {
        "MERRA-2 Mean Bias Correction": "bisque",
        "MERRA-2 Linear Regression Correction": "orange",
        "MERRA-2 Random Forest Correction": "maroon",
        "ERA5-Land Mean Bias Correction": "deepskyblue",
        "ERA5-Land Linear Regression Correction": "blue",
        "ERA5-Land Random Forest Correction": "darkblue"
    }

    # air_temp = [8.81, 10.14, 112.99, 10.61, 12.06, 83.62]
    # ws = [11.19, 18.49, 72.87, 5.75,  7.28, 60.21]
    # precip = [-0.1, 4.71, 15.53, 0.12,  5.73, 10]
    # pressure = [2.65, 2.96, 432.11, 0.76,   0.87, 152.53]
    # rh = [22.06, 36.68, 168.18, 10.68, 14.31, 83.79]

    x = np.arange(len(attrs))  # the label locations
    width = 0.15  # the width of the bars
    multiplier = 0

    plt.style.use("ggplot")
    plt.rcParams['font.size'] = 20
    # plt.rc('font', small=22)
    plt.rcParams['axes.facecolor'] = 'w'
    plt.rcParams['axes.edgecolor'] = 'dimgrey'
    plt.rcParams['grid.color'] = 'lightgrey'
    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in percents.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute])
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percent Improvement', color="black")
    ax.set_xticks(x + 2.5 * width, attrs, color="black")
    ax.legend(loc='upper left', ncols=2, prop={"size": 18})

    ax.set_ylim(0, 100)
    # plt.yscale("log")

    plt.show()


def format_table_three(uncorrected, mean, lin, randFor):
    output = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    files = glob.glob("output/*.csv")

    for file in files:
        if file in ["output\\AvgAir_T_output.csv", "output\\AvgWS_output.csv", "output\\Pluvio_Rain_output.csv",
                    "output\\Press_hPa_output.csv", "output\\RH_output.csv"]:
            uncorrected_months = uncorrected[file]
            mean_months = mean[file]
            lin_months = lin[file]
            randFor_months = randFor[file]

            for i in range(12):
                output[i] += " & " + str(uncorrected_months[i]) + " & " + str(mean_months[i]) + " & " + str(
                    lin_months[i]) + " & " + str(randFor_months[i]) + "\n"

    for month in output:
        print(month + "\\\\")

    print("\n")

    # output = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
    #           "November", "December"]
    # for file in files:
    #     if file in ["output\\Press_hPa_output.csv", "output\\RH_output.csv"]:
    #         uncorrected_months = uncorrected[file]
    #         mean_months = mean[file]
    #         lin_months = lin[file]
    #         randFor_months = randFor[file]
    #
    #         for i in range(12):
    #             output[i] += " & " + str(uncorrected_months[i]) + " & " + str(mean_months[i]) + " & " + str(
    #                 lin_months[i]) + " & " + str(randFor_months[i])
    #
    # for month in output:
    #     print(month + "\\\\")


# change a filename to get the attribute or column name from it
def get_column_name(file, prefix=""):
    return prefix + file.replace("output\\", "").replace("_output.csv", "")


# given a df and 2 columns, calculate the correlation constant
# between them via the pearson method.
def correlation_coefficient(df, col1, col2):
    two_column_df = df[[col1, col2]]
    correlation = two_column_df.corr(method="pearson")
    print(correlation)
    print("\n\n")
    return correlation[col1][col2]


def extreme_rmse(df, attribute, col1, col2):
    if attribute in ["AvgWS", "Pluvio_Rain"]:
        print(attribute + "Extreme rmse\n\n\n", df[col1].quantile(q=0.95))
        df = df[df[col1] > df[col1].quantile(q=0.95)]
        return np.sqrt(df[col2].mean())
    elif attribute in ["AvgAir_T", "Press_hPa"]:
        print(attribute + "Extreme rmse\n\n\n", df[col1].quantile(q=0.975), df[col1].quantile(q=0.025))
        df_1 = df[df[col1] > df[col1].quantile(q=0.975)]
        df_2 = df[df[col1] < df[col1].quantile(q=0.025)]
        df = pd.concat([df_1, df_2])
        return np.sqrt(df[col2].mean())
    elif attribute in ["RH"]:
        print(attribute + "Extreme rmse\n\n\n", df[col1].quantile(q=0.05))
        df = df[df[col1] < df[col1].quantile(q=0.05)]
        return np.sqrt(df[col2].mean())


# apply_corrections
#
# Given a df apply the corrections to the df using the specified method
# that is in dataType. The specified merra and era5 columns will be modified
# to represent the new corrected data.
# operation is not done in place, returns modified dataframe.
def apply_corrections(df, attr, stn_col, merra_col, era5_col, data_type):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])

    if data_type == DataType.lin_reg:
        with open("../error_correction/monthly_linear_regression.json", "r") as f:
            linear_reg = json.load(f)

    elif data_type == DataType.mean_err:
        with open("../error_correction/monthly_mean_error.json", "r") as f:
            mean_err = json.load(f)

    if data_type == DataType.mean_err:
        if "merra_err" in df.columns:
            # merra correction
            merra_dict = mean_err["merra"][attr]
            merra_err_df = pd.DataFrame.from_dict(merra_dict, orient="index", columns=["merra_corr"])
            merra_err_df = merra_err_df.set_index(pd.to_numeric(merra_err_df.index))

            df = df.merge(merra_err_df, how="left", left_on=df["time"].dt.month, right_index=True)

            df["merra_err"] = df[stn_col] - (df[merra_col] - df["merra_corr"])
            df["merra_sqr_err"] = (df[stn_col] - (df[merra_col] - df["merra_corr"])) ** 2

        if "era5_err" in df.columns:
            # era5 correction
            era5_dict = mean_err["era5"][attr]
            era5_err_df = pd.DataFrame.from_dict(era5_dict, orient="index", columns=["era5_corr"])
            era5_err_df = era5_err_df.set_index(pd.to_numeric(era5_err_df.index))

            df = df.drop(columns=["key_0"])

            df = df.merge(era5_err_df, how="left", left_on=df["time"].dt.month, right_index=True)

            df["era5_err"] = df[stn_col] - (df[era5_col] - df["era5_corr"])
            df["era5_sqr_err"] = (df[stn_col] - (df[era5_col] - df["era5_corr"])) ** 2

    elif data_type == DataType.lin_reg:
        if "merra_err" in df.columns:
            # merra correction
            merra_dict = linear_reg["merra"][attr]
            merra_err_df = pd.DataFrame.from_dict(merra_dict, orient="index",
                                                  columns=["merra_slope", "merra_intercept"])
            merra_err_df = merra_err_df.set_index(pd.to_numeric(merra_err_df.index))

            df = df.merge(merra_err_df, how="left", left_on=df["time"].dt.month, right_index=True)

            df["merra_err"] = df[stn_col] - (df["merra_slope"] * df[merra_col] + df["merra_intercept"])
            df["merra_sqr_err"] = (df[stn_col] - (df["merra_slope"] * df[merra_col] + df["merra_intercept"])) ** 2

        if "era5_err" in df.columns:
            # era5 correction
            era5_dict = linear_reg["era5"][attr]
            era5_err_df = pd.DataFrame.from_dict(era5_dict, orient="index", columns=["era5_slope", "era5_intercept"])
            era5_err_df = era5_err_df.set_index(pd.to_numeric(era5_err_df.index))

            df = df.drop(columns=["key_0"])

            df = df.merge(era5_err_df, how="left", left_on=df["time"].dt.month, right_index=True)

            df["era5_err"] = df[stn_col] - (df["era5_slope"] * df[era5_col] + df["era5_intercept"])
            df["era5_sqr_err"] = (df[stn_col] - (df["era5_slope"] * df[era5_col] + df["era5_intercept"])) ** 2

    return df


def print_stats(data_type):
    files = glob.glob("output/*.csv")
    root_path = "D:\\data\\graphs\\interesting\\manitoba_map\\"

    generic_merra_all = {}
    generic_mbe_merra_all = {}
    generic_era5_all = {}
    generic_mbe_era5_all = {}
    monthly_merra_all = {}
    monthly_mbe_merra_all = {}
    monthly_era5_all = {}
    monthly_mbe_era5_all = {}
    spacial_merra_all = {}
    spacial_era5_all = {}

    merra_pcc = {}
    era5_pcc = {}

    merra_ex = {}
    era5_ex = {}

    for file in files:
        df = pd.read_csv(file)
        print(file)

        if "Pluvio_Rain" in file:
            print(df["merra_sqr_err"].mean())

        attr = get_column_name(file)
        stn_col = get_column_name(file, "stn_")
        merra_col = get_column_name(file, "merra_")
        era5_col = get_column_name(file, "era5_")

        if data_type != DataType.raw:
            df = apply_corrections(df, attr, stn_col, merra_col, era5_col, data_type)

        if "merra_sqr_err" in df.columns:
            generic_merra = generic_performance(df, "merra_sqr_err")
            generic_merra_all[file] = generic_merra
        if "era5_sqr_err" in df.columns:
            generic_era5 = generic_performance(df, "era5_sqr_err")
            generic_era5_all[file] = generic_era5

        if "merra_err" in df.columns:
            generic_mbe_merra = generic_performance_mbe(df, "merra_err")
            generic_mbe_merra_all[file] = generic_mbe_merra
        if "era5_err" in df.columns:
            generic_mbe_era5 = generic_performance_mbe(df, "era5_err")
            generic_mbe_era5_all[file] = generic_mbe_era5

        # print(file, generic_merra, generic_era5)

        if "merra_sqr_err" in df.columns:
            monthly_merra = monthly_breakdown(df, "merra_sqr_err")
            monthly_merra_all[file] = monthly_merra
        if "era5_sqr_err" in df.columns:
            monthly_era5 = monthly_breakdown(df, "era5_sqr_err")
            monthly_era5_all[file] = monthly_era5

        if "merra_err" in df.columns:
            monthly_mbe_merra = monthly_mbe_breakdown(df, "merra_err")
            monthly_mbe_merra_all[file] = monthly_mbe_merra
        if "era5_err" in df.columns:
            monthly_mbe_era5 = monthly_mbe_breakdown(df, "era5_err")
            monthly_mbe_era5_all[file] = monthly_mbe_era5

        # print(seasonal_merra, seasonal_era5)

        if "merra_sqr_err" in df.columns:
            output_file = root_path + file.replace("_output.csv", ".html").replace("output\\", "merra_")
            title = "merra " + file.replace("_output.csv", "").replace("output\\", "")

            spacial_merra = spacial_correlation(df, "merra_err", True, output_file, title)
            spacial_merra_all[file] = spacial_merra
        if "era5_sqr_err" in df.columns:
            output_file = root_path + file.replace("_output.csv", ".html").replace("output\\", "era5_")
            title = "era5 " + file.replace("_output.csv", "").replace("output\\", "")

            spacial_era5 = spacial_correlation(df, "era5_err", True, output_file, title)
            spacial_era5_all[file] = spacial_era5

        if merra_col in df.columns:
            merra_pcc[file] = correlation_coefficient(df, stn_col, merra_col)
        if era5_col in df.columns:
            era5_pcc[file] = correlation_coefficient(df, stn_col, era5_col)

        if merra_col in df.columns:
            merra_ex[file] = extreme_rmse(df, attr, stn_col, "merra_sqr_err")
        if era5_col in df.columns:
            era5_ex[file] = extreme_rmse(df, attr, stn_col, "era5_sqr_err")

    format_table_one(generic_merra_all, generic_era5_all, generic_mbe_merra_all, generic_mbe_era5_all, merra_pcc,
                     era5_pcc, merra_ex, era5_ex)

    # print(generic_merra_all, generic_era5_all)
    # print(monthly_merra_all, monthly_era5_all)
    #
    # print("\nmerra rmse")
    # format_seasonal_stats(monthly_merra_all)
    # print("\nmerra mbe")
    # format_seasonal_stats(monthly_mbe_merra_all)
    # print("\nEra5 rmse")
    # format_seasonal_stats(monthly_era5_all)
    # print("\nEra5 rmse")
    # format_seasonal_stats(monthly_era5_all)

    return {"merra_rmse": generic_merra_all, "era5_rmse": generic_era5_all,
            "merra_mbe": generic_mbe_merra_all, "era5_mbe": generic_mbe_era5_all,
            "monthly_merra_rmse": monthly_merra_all, "monthly_merra_mbe": monthly_mbe_merra_all,
            "monthly_era5_rmse": monthly_era5_all, "monthly_era5_mbe": monthly_mbe_era5_all,
            "spacial_merra_all": spacial_merra_all, "spacial_era5_all": spacial_era5_all}


data_type_run = DataType.raw
# print_stats(data_type_run)

# print_table_three()
# print("\ntable 4\n")
# print_table_four()

make_percent_improvements_bar_chart()
