import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math


def linear_comparison(i, j, col1, col2, ax, title):
    ax[i, j].scatter(col1, col2, s=0.1)
    ax[i, j].axline((0, 0), slope=1)
    ax[i, j].axline((0, 2), slope=1)
    ax[i, j].axline((0, -2), slope=1)
    ax[i, j].set_title(title)
    ax[i, j].set_ylabel("degree celsius")
    ax[i, j].set_xlabel("degree celsius")


def yearly_scatter(i, j, date_col, col1, col2, ax, title):
    ax[i, j].scatter(date_col, col1, c="Blue", label="Old Normal", s=0.1)
    ax[i, j].scatter(date_col, col2, c="Orange", label="New Normal", s=0.1)
    ax[i, j].legend()
    ax[i, j].set_title(title)
    ax[i, j].set_xticks(["2000-01-01", "2000-03-01", "2000-05-01", "2000-07-01", "2000-09-01", "2000-11-01"])


def normal_scatter(merged_normal):
    fig, ax = plt.subplots(2, 2)
    linear_comparison(0, 0, merged_normal["Tmax_x"], merged_normal["Tmax_y"], ax, "Comparing max temp between two normals")
    linear_comparison(0, 1, merged_normal["Tmin_x"], merged_normal["Tmin_y"], ax, "Comparing min temp between two normals")
    linear_comparison(1, 0, merged_normal["Tavg_x"], merged_normal["Tavg_y"], ax, "Comparing avg temp between two normals")
    plt.show()
    plt.clf()

    fig, ax = plt.subplots(2, 2)
    yearly_scatter(0, 0, merged_normal["DateDT"], merged_normal["Tmax_x"], merged_normal["Tmax_y"], ax, "Max temp yearly comparison")
    yearly_scatter(1, 0, merged_normal["DateDT"], merged_normal["Tmin_x"], merged_normal["Tmin_y"], ax, "Min temp yearly comparison")
    yearly_scatter(0, 1, merged_normal["DateDT"], merged_normal["Tavg_x"], merged_normal["Tavg_y"], ax, "Avg temp yearly comparison")
    plt.show()
    plt.clf()


def compare_normals():
    normal_df = pd.read_csv("../../../data/2000-normal.csv")
    corrected_df = pd.read_csv("../../../data/climate_normals/climate_normal_avg/2020_2.csv")

    print(normal_df["Location"].unique())

    # normal_df = normal_df[normal_df["Location"] == "RUSSELL"]
    # corrected_df = corrected_df[corrected_df["Location"] == "RUSSELL"]

    merged_df = normal_df.merge(corrected_df, how="inner", on=["Location", "NormMM", "NormDD"])
    merged_df["DateDT"] = merged_df["DateDT_x"]
    print(merged_df[["Tmax_x", "Tmax_y"]])

    print("Tmax", round(math.sqrt(mean_squared_error(merged_df["Tmax_x"], merged_df["Tmax_y"])), 2))
    print("Tmin", round(math.sqrt(mean_squared_error(merged_df["Tmin_x"], merged_df["Tmin_y"])), 2))
    print("Tavg", round(math.sqrt(mean_squared_error(merged_df["Tavg_x"], merged_df["Tavg_y"])), 2))
    print("PPT", round(math.sqrt(mean_squared_error(merged_df["PPT_x"], merged_df["PPT_y"])), 2))
    print("CHU", round(math.sqrt(mean_squared_error(merged_df["CHU_x"], merged_df["CHU_y"])), 2))
    print("GDD", round(math.sqrt(mean_squared_error(merged_df["GDD_x"], merged_df["GDD_y"])), 2))
    
    print("mean error \n \n")

    print("Tmax", round((merged_df["Tmax_x"] - merged_df["Tmax_y"]).mean(), 2))
    print("Tmin", round((merged_df["Tmin_x"] - merged_df["Tmin_y"]).mean(), 2))
    print("Tavg", round((merged_df["Tavg_x"] - merged_df["Tavg_y"]).mean(), 2))
    print("PPT", round((merged_df["PPT_x"] - merged_df["PPT_y"]).mean(), 2))
    print("CHU", round((merged_df["CHU_x"] - merged_df["CHU_y"]).mean(), 2))
    print("GDD", round((merged_df["GDD_x"] - merged_df["GDD_y"]).mean(), 2))

    # random forest corrected model preforming poorly, make sure equations are working correctly
    # maybe try using non modified era5 data instead.

    normal_scatter(merged_df)


def compare_rain_normals():
    normal = pd.read_csv("../../../data/2000-normal.csv")
    era5 = pd.read_csv("../../../data/climate_normal_avg/2000_era5.csv")

    regression = linear_model.LinearRegression()

    merged_df = era5.merge(normal, how="inner", on=["Location", "DateDT"])

    # merged_df = merged_df[np.logical_and(merged_df["PPT_x"] > 1, merged_df["PPT_y"] > 1)]

    # merged_df["PPT_x"] = merged_df["PPT_x"] * 0.295 + 1.385

    x = merged_df["PPT_x"].values
    y = merged_df["PPT_y"].values

    x = x.reshape(len(x), 1)
    y = y.reshape(len(y), 1)

    regression.fit(x, y)

    slope = regression.coef_[0][0]
    intercept = regression.intercept_[0]
    print(slope, intercept)

    plt.scatter(x, y, c="black", alpha=0.05, edgecolors='none')
    plt.plot([0, 8], [0, 8], c="blue")
    plt.plot([0, 8], [intercept, 8 * slope + intercept], c="red")

    ax = plt.gca()
    ax.set_xlim([0, 8])
    ax.set_ylim([0, 8])

    plt.show()

    print("PPT", round((merged_df["PPT_x"] - merged_df["PPT_y"]).mean(), 5))

    print(merged_df["PPT_x"].sum(), merged_df["PPT_y"].sum())

    df = merged_df[["Location", "DateDT", "PPT_x", "PPT_y"]]
    # df.to_csv("corrected_normal.csv")


def graph_normals():
    normal = pd.read_csv("../../../data/2000-normal.csv")
    era5 = pd.read_csv("../../../data/climate_normal_avg/2000_era5.csv")

    normal = normal[normal["PPT"] < 1]

    merged_df = era5.merge(normal, how="inner", on=["Location", "DateDT"])
    merged_df = merged_df[np.logical_and(merged_df["PPT_x"] > 1, merged_df["PPT_y"] > 1)]

    merged_df["PPT_x"] = merged_df["PPT_x"]

    x = merged_df["PPT_x"].values
    y = merged_df["PPT_y"].values

    x = x.reshape(len(x), 1)
    y = y.reshape(len(y), 1)

    plt.scatter(x, y, c="black")
    plt.show()


compare_normals()
# compare_rain_normals()
# graph_normals()
