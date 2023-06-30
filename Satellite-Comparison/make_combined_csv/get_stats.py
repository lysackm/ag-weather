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


# monthly_breakdown
#
# Break down data for each month. Then find the root-mean-square error
# for each of the months over all the years.
def monthly_breakdown(df, col):
    df["time"] = pd.to_datetime(df["time"])
    df.set_index(df["time"], inplace=True)
    all_years = np.sqrt(df.groupby([df.index.month])[col].mean())

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
                                opacity=0.60,
                                title=title)

        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 80, "l": 0, "b": 0})
        fig.write_html(output_file)

    return stn_data


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
        print(month)


def get_column_name(file, prefix=""):
    return prefix + file.replace("output\\", "").replace("_output.csv", "")


def correlation_coefficient(df, col1, col2):
    two_column_df = df[[col1, col2]]
    correlation = two_column_df.corr(method="pearson")
    print("\n\n", col1, col2, "\n")
    print(correlation)
    print("\n\n")
    return correlation


def main():
    files = glob.glob("output/*.csv")
    root_path = "D:\\data\\graphs\\interesting\\manitoba_map\\"

    generic_merra_all = {}
    generic_era5_all = {}
    monthly_merra_all = {}
    monthly_era5_all = {}
    spacial_merra_all = {}
    spacial_era5_all = {}

    for file in files:
        df = pd.read_csv(file)
        print(file)

        stn_col = get_column_name(file, "stn_")
        merra_col = get_column_name(file, "merra_")
        era5_col = get_column_name(file, "era5_")

        if "merra_sqr_err" in df.columns:
            generic_merra = generic_performance(df, "merra_sqr_err")
            generic_merra_all[file] = generic_merra
        if "era5_sqr_err" in df.columns:
            generic_era5 = generic_performance(df, "era5_sqr_err")
            generic_era5_all[file] = generic_era5

        # print(file, generic_merra, generic_era5)

        if "merra_sqr_err" in df.columns:
            monthly_merra = monthly_breakdown(df, "merra_sqr_err")
            monthly_merra_all[file] = monthly_merra
        if "era5_sqr_err" in df.columns:
            monthly_era5 = monthly_breakdown(df, "era5_sqr_err")
            monthly_era5_all[file] = monthly_era5

        # print(seasonal_merra, seasonal_era5)

        if "merra_sqr_err" in df.columns:
            output_file = root_path + file.replace("_output.csv", ".html").replace("output\\", "merra_")
            title = "merra " + file.replace("_output.csv", "").replace("output\\", "")

            spacial_merra = spacial_correlation(df, "merra_err", False, output_file, title)
            spacial_merra_all[file] = spacial_merra
        if "era5_sqr_err" in df.columns:
            output_file = root_path + file.replace("_output.csv", ".html").replace("output\\", "era5_")
            title = "era5 " + file.replace("_output.csv", "").replace("output\\", "")

            spacial_era5 = spacial_correlation(df, "era5_err", False, output_file, title)
            spacial_era5_all[file] = spacial_era5

        if merra_col in df.columns:
            correlation_coefficient(df, stn_col, merra_col)
        if era5_col in df.columns:
            correlation_coefficient(df, stn_col, era5_col)

    print(generic_merra_all, generic_era5_all)
    print(monthly_merra_all, monthly_era5_all)

    print("merra")
    format_seasonal_stats(monthly_merra_all)
    print("\nEra5")
    format_seasonal_stats(monthly_era5_all)


main()
