import glob

import pandas as pd
import numpy as np


# remove_outliers_province_mean
#
# Function removes outliers by comparing every value to a provincial wide average
# at that specific time (at hourly time resolution).
# Any value that is outside the given threshold is removed and the rows removed.
def remove_outliers_province_mean(df, col_name, threshold):
    df["time"] = pd.to_datetime(df["time"])

    df.set_index(df["time"], inplace=True)
    df["mean_daily"] = df.groupby([df.index.year, df.index.month, df.index.day, df.index.hour])[col_name].transform(
        'mean')

    # diff is a dataframe with the outlier rows removed
    diff = df[abs(df["mean_daily"] - df[col_name]) < threshold]
    diff.to_csv("testing.csv")
    print(diff)

    # deleted is a dataframe with only the removed outlier rows
    # deleted = df[abs(df["mean_daily"] - df[col_name]) > threshold]
    # deleted.to_csv("deleted.csv")


# remove_outliers_closest_neighbor
#
# Function that removes outlier data from the generated csvs (made from
# program in make_combined_csv.py). Outliers are determined relatively
# in regard to the n closest neighbors. Number of neighbors compared is
# dependent on the number of columns in the file Cleaning-Data/cleaning-data/neighboring-stations.csv
# neighboring-stations.csv provides the neighbor StnIds for each station.
# If a stations hourly value difference from the average of the n closest
# neighbors is greater than the threshold then it is removed as an outlier
# Remember to only have the correct number of stations in neighboring-stations.csv
def remove_outliers_closest_neighbor(attr_filename, output_file, col_name, threshold):
    # load whole file
    neighbor_metadata_df = pd.read_csv("../../Cleaning-Data/cleaning-data/neighboring-stations.csv")
    stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
    total_df = pd.read_csv(attr_filename)
    print(attr_filename)
    total_df["time"] = pd.to_datetime(total_df["time"])

    stn_dfs = []

    stations = stn_metadata["StnID"]
    for station in stations:
        # For each attribute each station needs to be checked separately so that we can get the 4 closest stations
        # for that specific station. I don't think this can be optimized drastically, but it probably can be

        neighbors_ids = get_neighbors(station, neighbor_metadata_df)

        # set index to be time and drop duplicate column
        stn_df = total_df[total_df["StnID"] == station].copy()
        stn_df.set_index(stn_df["time"], inplace=True)
        stn_df.drop(columns="time", inplace=True)

        neighbors_df = total_df[total_df["StnID"].isin(neighbors_ids)]
        neighbors_df.set_index(neighbors_df["time"], inplace=True)
        neighbors_df.drop(columns="time", inplace=True)

        # calculate neighbor average for whole dataframe
        neighbors_avg_df = neighbors_df.groupby([neighbors_df.index])[col_name].mean()

        # make joined df on dates so that when comparing the indices are the same
        joined_df = pd.merge(neighbors_avg_df, stn_df[col_name], how="right", right_index=True, left_index=True)

        # print("joined_df", joined_df.index)
        # print("neighbors_avg_df", neighbors_avg_df.index)
        # print("stn_df", stn_df.index)

        # outliers set to NaN
        stn_df.loc[abs(joined_df[col_name + "_x"] - joined_df[col_name + "_y"]) > threshold, col_name] = np.NaN

        # also set other columns to NaN (columns which use the station data which could be an outlier)
        if "merra_err" in stn_df.columns:
            stn_df.loc[abs(joined_df[col_name + "_x"] - joined_df[col_name + "_y"]) > threshold,
                       ["merra_err", "merra_sqr_err"]] = np.NaN
        if "era5_err" in stn_df.columns:
            stn_df.loc[abs(joined_df[col_name + "_x"] - joined_df[col_name + "_y"]) > threshold,
                       ["era5_err", "era5_sqr_err"]] = np.NaN

        # print(stn_df[abs(joined_df[col_name + "_x"] - joined_df[col_name + "_y"]) > threshold]["merra_err"])

        stn_dfs.append(stn_df)

    total_filtered_df = pd.concat(stn_dfs)
    try:
        total_filtered_df.drop(columns="Unnamed: 0", inplace=True)
    except:
        print("Probably no unnamed column")
    total_filtered_df.to_csv(output_file)
    print(output_file)


# given a station with id stn_id, and a loaded df of neighboring-stations.csv then it returns
# the station Ids of the neighbors of stn_id. Returns a list.
def get_neighbors(stn_id, neighbor_df):
    row = neighbor_df[neighbor_df["Station"] == stn_id]
    return row.values.tolist()[0][1:]


# clean_all_csvs_closest_neighbors
#
# using the n closest neighbor method it goes through every attribute and removes
# any outliers that it finds is greater than the defined thresholds in the function.
# Does not do anything for attributes/files that do not have a defined threshold.
def clean_all_csvs_closest_neighbors():
    # Heuristic offset bounds
    #   air temp: +/- 10 degrees
    #   humidity: +/- 20 %
    #   wind speed: +/- 10m/s
    #   air pressure: +/- 15hPa
    air_thresh = 5.0
    ws_thresh = 10.0
    press_thresh = 15.0
    hum_thresh = 20.0
    solar_thresh = 1.0
    soil_thresh = 7.0
    attr_offsets = {"AvgAir_T": air_thresh, "AvgWS": ws_thresh, "Press_hPa": press_thresh, "RH": hum_thresh,
                    "SolarRad": solar_thresh, "Soil_5_20_avg_TempC": soil_thresh,
                    "Soil_20_50_100_avg_TempC": soil_thresh,
                    "Soil_50_100_avg_TempC": soil_thresh, "Soil_TP5_TempC": soil_thresh, "Soil_TP20_TempC": soil_thresh,
                    "Soil_TP50_TempC": soil_thresh}

    files = glob.glob("output/pre_cleaning/*.csv")

    for file in files:
        attr_name = file.replace("_output.csv", "").replace("output/pre_cleaning\\", "")
        output_file = file.replace("pre_cleaning\\", "")
        col_name = "stn_" + attr_name

        if attr_name in attr_offsets.keys():
            threshold = attr_offsets[attr_name]
            # all the work done in this function call. Can comment out for testing purposes
            remove_outliers_closest_neighbor(file, output_file, col_name, threshold)
            # print(file, output_file, col_name, threshold)


clean_all_csvs_closest_neighbors()
