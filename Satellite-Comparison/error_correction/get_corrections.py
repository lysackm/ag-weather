import json
import os
import time

import joblib
import pandas as pd
import xarray as xr
import glob

from sklearn import datasets, linear_model
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
import warnings
import pickle
import numpy as np
import statistics as stats

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import spearmanr, pearsonr

warnings.simplefilter(action='ignore', category=FutureWarning)


# raw data to stored np array
def process_data(attr_stn_col, attr_model_col, model):
    df = pd.read_csv("random_forest_data.csv")

    df["time"] = pd.to_datetime(df["time"])

    model_df = df[["Station", model + "_lat", model + "_lon", "elevation", model + "_AvgAir_T", model + "_AvgWS",
                   model + "_Pluvio_Rain", model + "_Press_hPa", model + "_RH", model + "_SolarRad", attr_stn_col]]
    model_df = model_df.assign(month=df["time"].dt.month)
    model_df = model_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the merra location
    model_df = model_df.assign(dist=((df["stn_long"] - df[model + "_lon"]) ** 2 +
                                     (df["stn_lat"] - df[model + "_lat"]) ** 2) ** 1 / 2)

    model_df[attr_stn_col] = model_df[attr_stn_col] - model_df[attr_model_col]

    model_df = model_df.dropna()

    return model_df


def time_fading(df):
    num_previous = 3
    model = "merra"
    df_past = df[[model + "_AvgAir_T", model + "_AvgWS", model + "_Pluvio_Rain",
                  model + "_Press_hPa", model + "_RH", model + "_SolarRad"]]

    for i in range(num_previous):
        str_num = str(i) + model
        new_col_names = [str_num + "_AvgAir_T", str_num + "_AvgWS", str_num + "_Pluvio_Rain",
                         str_num + "_Press_hPa", str_num + "_RH", str_num + "_SolarRad"]

        df[new_col_names] = (df_past
                             .groupby(df["Station"], group_keys=False)
                             .apply(lambda s: s.bfill().shift(-1)))
        df_past = df[new_col_names]

    return df


def load_data(attr, is_time_faded=False):
    model = "merra"
    attr_stn_col = "stn_" + attr
    attr_model_col = model + "_" + attr
    model_df = process_data(attr_stn_col, attr_model_col, model)

    if is_time_faded:
        model_df = time_fading(model_df)
        model_df = model_df.dropna()

        x_df = model_df.loc[:, model_df.columns != "Station"]
        x_df = x_df.loc[:, x_df.columns != attr_stn_col]
        x_arr = x_df.to_numpy()
        y_arr = model_df[attr_stn_col].to_numpy()

    else:
        x_arr = model_df.loc[:, model_df.columns != "Station"].to_numpy()
        y_arr = model_df[attr_stn_col].to_numpy()

    return x_arr, y_arr


def time_series_random_forest():
    x_arr, y_arr = load_data("AvgAir_T", True)

    train_random_forest(x_arr, y_arr, "merra_all_attrs", 100, 0.5, 1)


# merge_files
#
# Combine all data in output files together to improve performance
# for loading the csv files. Only has one copy of the metadata but
# keeps the data for all the attributes. Output is written to a file
# called random_forest_data.csv.
def merge_files():
    files = glob.glob("../make_combined_csv/output/*.csv")
    df_output = pd.read_csv("../make_combined_csv/output/AvgAir_T_output.csv")

    df_output = df_output[["merra_lat", "merra_lon", "stn_long", "stn_lat", "era5_lat", "era5_long", "elevation",
                           "merra_AvgAir_T", "stn_AvgAir_T", "era5_AvgAir_T", "time", "Station"]]

    print("start", len(df_output.index))

    for file in files:
        if "AvgAir_T" not in file:
            df = pd.read_csv(file)
            attr_name = file.replace("../make_combined_csv/output\\", "").replace("_output.csv", "")

            df = df[["stn_" + attr_name, "era5_" + attr_name, "merra_" + attr_name, "time", "Station"]]
            df_output = df_output.merge(df, on=["Station", "time"], how="inner")
            print(file, len(df_output.index))

    df_output = df_output.dropna(how="any")
    df_output.drop_duplicates(subset=['Station', 'time'], inplace=True)
    df_output.to_csv("random_forest_data.csv", index=False)


# def make_netcdf():
#     df = pd.read_csv("random_forest_data.csv")
#     df.drop_duplicates(subset=['Station', 'time'], inplace=True)
#     df = df.set_index(["Station", "time"])
#     print(df)
#
#     ds = xr.Dataset.from_dataframe(df)
#     print(ds)
#     ds.to_netcdf("data.netcdf")


def print_hourly_stats(random_forest, x_test, y_test):
    merged = np.c_[x_test, y_test]
    df = pd.DataFrame(merged)

    rmse_arr = []

    for hour in range(24):
        df_hour = df[df[10] == hour]
        y_hour = df_hour[12].to_numpy()
        x_hour = df_hour[range(12)].to_numpy()

        predicted_test = random_forest.predict(x_hour)

        rmse = np.sqrt(mean_squared_error(y_hour, predicted_test))
        rmse_arr.append(rmse)
        pearson = pearsonr(y_hour, predicted_test)

        # print(f'Root mean squared error: {rmse:.6}')
        # print(f'Test data Pearson correlation: {pearson[0]:.6}')

    print(rmse_arr)


def print_monthly_stats(random_forest, x_test, y_test):
    merged = np.c_[x_test, y_test]
    df = pd.DataFrame(merged)

    rmse_arr = []

    for month in range(1, 13):
        df_month = df[df[9] == month]
        y_month = df_month[12].to_numpy()
        x_month = df_month[range(12)].to_numpy()

        predicted_test = random_forest.predict(x_month)

        rmse = np.sqrt(mean_squared_error(y_month, predicted_test))
        rmse_arr.append(rmse)
        pearson = pearsonr(y_month, predicted_test)

        # print(f'Root mean squared error: {rmse:.6}')
        # print(f'Test data Pearson correlation: {pearson[0]:.6}')

    print(rmse_arr)


# given a 2D numpy array for the input and output of the random forest
# train a random forest on said data, and test it. Saves it using
# joblib in the directory random_forests
def train_random_forest(x_arr, y_arr, file_short_name, n_estimators, max_features, min_samples_leaf):
    # 80% for training, 20% for testing
    x_train, x_test, y_train, y_test = train_test_split(
        x_arr, y_arr, test_size=0.2, random_state=204)

    # store models in the directory random_forests
    output_file = "random_forests/" + file_short_name + ".joblib"
    if os.path.exists(output_file) and False:
        with open(output_file, "rb") as model_file:
            # model = pickle.load(model_file)
            model = joblib.load(model_file)

    else:
        print("training new model for ", file_short_name)
        # train model
        # n_estimators: number of trees in forest
        # n_jobs: processes to run in parallel (-1 is all available)
        # n_estimators = 100, n_jobs = -1, runtime 305 secs (~5 minutes)
        model = RandomForestRegressor(n_estimators=n_estimators, max_features=max_features,
                                      min_samples_leaf=min_samples_leaf, n_jobs=-1)
        model.fit(x_train, y_train)

        # try:
        #     # when saving random
        #     with open(output_file, "wb") as model_file:
        #         # pickle.dump(model, model_file)
        #         joblib.dump(model, model_file)
        # except Exception as e:
        #     print(e)

    # test model
    predicted_test = model.predict(x_test)
    rmse = np.sqrt(mean_squared_error(y_test, predicted_test))
    test_score = r2_score(y_test, predicted_test)
    spearman = spearmanr(y_test, predicted_test)
    pearson = pearsonr(y_test, predicted_test)

    print("Comprehensive Statistics")
    print(f'Root mean squared error: {rmse:.3}')
    print(f'Test data R-2 score: {test_score:>5.3}')
    print(f'Test data Spearman correlation: {spearman[0]:.3}')
    print(f'Test data Pearson correlation: {pearson[0]:.3}')

    print(model.feature_importances_)

    # print(model.predict(np.asarray([[-98.75, 49.5, 371.0, -28.830664062499977, 1, 6, 0.53]])))

    print("monthly stats")
    print_monthly_stats(model, x_test, y_test)
    print("hourly stats")
    print_hourly_stats(model, x_test, y_test)

    print("finished")


# train_random_forest
#
# Train and save a random forest based off of the following attributes:
# Latitude, Longitude (model), Month, Distance from observed, attribute value
# Elevation, Hour. Creates a model for both era5 and merra
def make_merra_era5_random_forest(df, attr_col, n_estimators, max_features, min_samples_leaf, all_attrs=False):
    # don't modify the dataframe, creates copy
    df = df.copy()

    attr_stn_col = "stn_" + attr_col
    merra_stn_col = "merra_" + attr_col
    era5_stn_col = "era5_" + attr_col

    # convert time to datetime to apply operations
    df["time"] = pd.to_datetime(df["time"])

    # merra random forest
    # get attributes wanted for random forest
    # input cols: merra_lat, merra_lon, time(.dt.month), time(.dt.hour), merra_stn_col, elevation
    if all_attrs:
        print("using all attrs")
        merra_df = df[["merra_lat", "merra_lon", "elevation", "merra_AvgAir_T", "merra_AvgWS",
                       "merra_Pluvio_Rain", "merra_Press_hPa", "merra_RH", "merra_SolarRad", attr_stn_col]]
    else:
        merra_df = df[["merra_lat", "merra_lon", "elevation", merra_stn_col, attr_stn_col]]
    merra_df = merra_df.assign(month=df["time"].dt.month)
    merra_df = merra_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the merra location
    merra_df = merra_df.assign(dist=((df["stn_long"] - df["merra_lon"]) ** 2 +
                                     (df["stn_lat"] - df["merra_lat"]) ** 2) ** 1 / 2)

    merra_df = merra_df.dropna(how="any")
    merra_df["y"] = merra_df[attr_stn_col] - merra_df[merra_stn_col]

    if all_attrs:
        x_merra_arr = merra_df[
            ["merra_lat", "merra_lon", "elevation", "merra_AvgAir_T", "merra_AvgWS", "merra_Pluvio_Rain",
             "merra_Press_hPa", "merra_RH", "merra_SolarRad", "month", "hour", "dist"]].to_numpy()
    else:
        x_merra_arr = merra_df[
            ["merra_lat", "merra_lon", "elevation", merra_stn_col, "month", "hour", "dist"]].to_numpy()

    y_merra_arr = merra_df["y"].to_numpy()
    # y_merra_arr = merra_df[attr_stn_col].to_numpy()

    # pass data to function to train model
    train_random_forest(x_merra_arr, y_merra_arr, attr_col + "_merra", n_estimators, max_features, min_samples_leaf)

    # train era5 model
    if all_attrs:
        print("using all attrs")
        era5_df = df[["era5_lat", "era5_long", "elevation", "era5_AvgAir_T", "era5_AvgWS", "era5_Pluvio_Rain",
                      "era5_Press_hPa", "era5_RH", "era5_SolarRad", attr_stn_col]]
    else:
        era5_df = df[["era5_lat", "era5_lon", "elevation", era5_stn_col, attr_stn_col]]
    era5_df = era5_df.assign(month=df["time"].dt.month)
    era5_df = era5_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the era5 location
    era5_df = era5_df.assign(dist=((df["stn_long"] - df["era5_long"]) ** 2 +
                                   (df["stn_lat"] - df["era5_lat"]) ** 2) ** 1 / 2)

    era5_df = era5_df.dropna(how="any")

    if all_attrs:
        x_era5_arr = era5_df[
            ["era5_lat", "era5_long", "elevation", "era5_AvgAir_T", "era5_AvgWS", "era5_Pluvio_Rain", "era5_Press_hPa",
             "era5_RH", "era5_SolarRad", "month", "hour", "dist"]].to_numpy()
    else:
        x_era5_arr = era5_df[["era5_lat", "era5_long", "elevation", era5_stn_col, "month", "hour", "dist"]].to_numpy()

    # y data is either the expected value or the error of the predicted and expected value
    # y_era5_arr = era5_df[attr_stn_col].to_numpy()
    y_era5_arr = (era5_df[attr_stn_col] - era5_df[era5_stn_col]).to_numpy()

    # pass data to train data
    train_random_forest(x_era5_arr, y_era5_arr, attr_col + "_era5", n_estimators, max_features, min_samples_leaf)


# iterate through several benchmarks to get stats on which
# random forest takes the longest
# This can take a long time
def random_forest_benchmarks(df, attr_col):
    for n_estimators in [100]:
        for max_features in [0.5]:
            for min_samples_leaf in [1]:
                print(n_estimators, max_features, min_samples_leaf)
                make_merra_era5_random_forest(df, attr_col, n_estimators, max_features, min_samples_leaf, True)


# linear_regression
#
# For every hour make a linear regression graph that has the x-axis be the
# model output, and the y-axis be the observed value. Output will be an equation
# for a linear graph that will take in the value and give a correction. Uses the
# scikit learn library to accomplish this
def linear_regression(df, x_col, y_col):
    output = {}
    df["time"] = pd.to_datetime(df["time"])
    month = 1

    for group_by_tuple in df.groupby([df["time"].dt.month]):
        try:
            index, month_df = group_by_tuple
        except Exception as e:
            month_df = group_by_tuple
            print(e)

        month_df = month_df.dropna()
        length = len(month_df.index)

        x = month_df[x_col].values
        y = month_df[y_col].values

        x = x.reshape(length, 1)
        y = y.reshape(length, 1)

        regression = linear_model.LinearRegression()
        regression.fit(x, y)

        # plot it as in the example at http://scikit-learn.org/
        # plotting takes a long time, commented out by default
        # plt.scatter(x, y, color='black')
        # plt.plot(x, regression.predict(x), color='blue', linewidth=3)
        # plt.xticks(())
        # plt.yticks(())
        # plt.show()

        slope = regression.coef_[0][0]
        intercept = regression.intercept_[0]
        output[month] = [slope, intercept]
        month += 1

        # print(f"y = %f x + %f" % (slope, intercept))
    return output


# monthly_breakdown
#
# Break down data for each month. Then find the root-mean-square error
# for each of the months over all the years.
def monthly_breakdown(df, col):
    df["time"] = pd.to_datetime(df["time"])
    df.set_index(df["time"], inplace=True)
    all_years = df.groupby([df.index.month])[col].mean() * -1

    month_mean_err = {}
    month_counter = 1
    for mean_err in all_years.to_list():
        month_mean_err[month_counter] = mean_err
        month_counter += 1

    return month_mean_err


# save_random_forest
#
# Go through all the files and create a random forest model and apply statistics to the result.
def save_random_forest():
    files = glob.glob("../make_combined_csv/output/*.csv")

    for file in files:
        df = pd.read_csv(file)
        attr_name = file.replace("../make_combined_csv/output\\", "").replace("_output.csv", "")

        # make_merra_era5_random_forest(df, attr_name, 100, None, 1)
        random_forest_benchmarks(df, attr_name)
        exit(0)


# create random forest using all attributes as input
def save_random_forest_all_attr():
    merge_files()
    df = pd.read_csv("random_forest_data.csv")
    # make_merra_era5_random_forest(df, "AvgAir_T", 100, 0.5, 1, True)
    # random_forest_benchmarks(df, "AvgAir_T")

    attrs = ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH", "SolarRad"]

    for attr in attrs:
        make_merra_era5_random_forest(df, attr, 100, 0.5, 1, True)


def main():
    files = glob.glob("../make_combined_csv/output/*.csv")

    # dictionary of lists (basically json format)
    mean_err_merra = {}
    mean_err_era5 = {}

    coefficients_merra = {}
    coefficients_era5 = {}

    for file in files:
        df = pd.read_csv(file)

        attr_name = file.replace("../make_combined_csv/output\\", "").replace("_output.csv", "")

        if "merra_err" in df.columns:
            mean_err_merra[attr_name] = monthly_breakdown(df, "merra_err")
        if "era5_err" in df.columns:
            mean_err_era5[attr_name] = monthly_breakdown(df, "era5_err")

        y_col = "stn_" + attr_name

        print(attr_name)

        if "merra_err" in df.columns:
            print("merra", attr_name)
            x_col = "merra_" + attr_name
            coefficients_merra[attr_name] = linear_regression(df, x_col, y_col)
        if "era5_err" in df.columns:
            print("era5", attr_name)
            x_col = "era5_" + attr_name
            coefficients_era5[attr_name] = linear_regression(df, x_col, y_col)

    print(coefficients_era5, coefficients_merra)
    with open("monthly_linear_regression.json", "w", encoding='utf-8') as f:
        json.dump({"merra": coefficients_merra, "era5": coefficients_era5}, f, ensure_ascii=False, indent=4)

    with open("monthly_mean_error.json", "w", encoding='utf-8') as f:
        json.dump({"merra": mean_err_merra, "era5": mean_err_era5}, f, ensure_ascii=False, indent=4)


# save_random_forest_all_attr()
# main()
# merge_files()
time_series_random_forest()
