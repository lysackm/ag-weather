import pandas as pd
import numpy as np

# load file once, generate all stats for that file


# generic_performance
#
# Find the root-mean-square of the entire attribute, over all stations
# over all time
# returns a single number
def generic_performance(df, col):
    return np.sqrt(df[col].mean())


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
    df.set_index(df["time"], inplace=True)
    all_years = df.groupby(pd.Grouper(freq='3M', origin='start'))[col].mean()

    seasons = [[], [], [], []]
    counter = 0
    for avg in all_years:
        seasons[counter].append(avg)
        counter = (counter + 1) % 3

    for i in range(4):
        seasons[i] = np.mean(seasons[i])

    print(seasons)
    return seasons


# spacial_correlation
#
# Data format is a dictionary where the keys are the station names
# and the values are the mean for that station
def spacial_correlation(df, col):
    stn_metadata = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")
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
            print(stn_df)

        stn_data["station"] = np.sqrt(stn_df[col].mean)


def main():
    df = pd.read_csv("some_file.csv")

    generic_merra = generic_performance(df, "merra_sqr_err")
    generic_era5 = generic_performance(df, "era5_sqr_err")

    seasonal_merra = seasonal_breakdown(df, "merra_sqr_err")
    seasonal_era5 = seasonal_breakdown(df, "era5_sqr_err")
