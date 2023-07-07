import json

import pandas as pd
import glob
from sklearn import datasets, linear_model
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# train_random_forest
#
# Train and save a random forest based off of the following attributes:
# Latitude, Longitude (model), Month, Distance from observed, attribute value
# Elevation, Hour. Uses Scikit learn.


def train_random_forest(df, attr_col):
    attr_stn_col = "stn_" + attr_col
    merra_stn_col = "merra_" + attr_col
    era5_stn_col = "era5_" + attr_col

    # will have to derive hour, month, and distance from observed
    merra_cols = ["time", "merra_lon", "merra_lat", attr_stn_col, merra_stn_col, "elevation"]
    era5_cols = ["time", "era5_lon", "era5_lat", attr_stn_col, era5_stn_col, "elevation"]


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


main()
