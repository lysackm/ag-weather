import glob

import pandas as pd
import numpy as np
import plotly.express as px


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


# spacial_correlation
#
# Data format is a dictionary where the keys are the station names
# and the values are the mean for that station. Data is average for every year for
# each station.
# Set show_graph to be true to generate graphs to represent the data on a map of
# Manitoba.
#
def spacial_correlation(df, col, show_graph=False):
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

        stn_data[station] = (stn_lat, stn_long, np.sqrt(stn_df[col].mean()))

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
                                size="value",
                                size_max=25,
                                zoom=8,
                                opacity=0.60)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.show()

    return stn_data


def main():
    files = glob.glob("output/*.csv")

    generic_merra_all = {}
    generic_era5_all = {}
    seasonal_merra_all = {}
    seasonal_era5_all = {}
    spacial_merra_all = {}
    spacial_era5_all = {}

    for file in files:
        df = pd.read_csv(file)
        print(file)

        if "merra_sqr_err" in df.columns:
            generic_merra = generic_performance(df, "merra_sqr_err")
            generic_merra_all[file] = generic_merra
        if "era5_sqr_err" in df.columns:
            generic_era5 = generic_performance(df, "era5_sqr_err")
            generic_era5_all[file] = generic_era5

        # print(file, generic_merra, generic_era5)

        if "merra_sqr_err" in df.columns:
            seasonal_merra = seasonal_breakdown(df, "merra_sqr_err")
            seasonal_merra_all[file] = seasonal_merra
        if "era5_sqr_err" in df.columns:
            seasonal_era5 = seasonal_breakdown(df, "era5_sqr_err")
            seasonal_era5_all[file] = seasonal_era5

        # print(seasonal_merra, seasonal_era5)

        if "merra_sqr_err" in df.columns:
            spacial_merra = spacial_correlation(df, "merra_sqr_err")
            spacial_merra_all[file] = spacial_merra
        if "era5_sqr_err" in df.columns:
            spacial_era5 = spacial_correlation(df, "era5_sqr_err")
            spacial_era5_all[file] = spacial_era5

    print(generic_merra_all, generic_era5_all)
    print(seasonal_merra_all, seasonal_era5_all)
    print(spacial_merra_all, spacial_era5_all)


main()
