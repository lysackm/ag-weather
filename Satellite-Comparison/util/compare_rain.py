import pandas as pd
import numpy as np

data_dir = "../../../../data/"


# returns file name for station data for our station data
def get_stn_filename(year):
    return "station-csv/MBAg-60min-" + str(year) + ".csv"


# load station data from the csv and return it as a dataframe
def load_stn_data(year):
    # station data is per year

    stn_file = get_stn_filename(year)
    stn_df = pd.read_csv(data_dir + stn_file, na_values="\\N")
    stn_df = stn_df.rename(columns={"TMSTAMP": "time"})
    stn_df["time"] = pd.to_datetime(stn_df["time"])
    return stn_df


def main():
    output_df = pd.DataFrame()

    # print the both rain columns when the absolute difference is greater than 10mm
    for year in range(2018, 2023):
        stn_df = load_stn_data(year)
        stn_df["diff"] = abs(stn_df["Pluvio_Rain"] - stn_df["TBRG_Rain"])
        stn_df["time"] = pd.to_datetime(stn_df["time"])
        print(stn_df["time"].dt.month)
        stn_df = stn_df[~((stn_df["time"].dt.month <= 3) & (stn_df["time"].dt.month >= 11) & (stn_df["Pluvio_Rain"] == 0)) &
                        stn_df["diff"] > 10 | stn_df["diff"] > 20]

        output_df = pd.concat([output_df, stn_df[["time", "Pluvio_Rain", "TBRG_Rain", "Station", "StnID"]]])

    output_df.to_csv("rain_comparison.csv", index=False)


def rain_stats():
    df = pd.read_csv("../make_combined_csv/output/temp-backup/Pluvio_Rain_output.csv")
    print("Station rain below 0.1: ", df[df["stn_Pluvio_Rain"] < 0.1]["stn_Pluvio_Rain"].size / df["stn_Pluvio_Rain"].size)
    print("era5-Land rain below 0.1: ", df[df["era5_Pluvio_Rain"] < 0.1]["stn_Pluvio_Rain"].size / df["stn_Pluvio_Rain"].size)
    print("Merra rain below 0.1: ", df[df["merra_Pluvio_Rain"] < 0.1]["stn_Pluvio_Rain"].size / df["stn_Pluvio_Rain"].size)


def rain_filtered():
    df = pd.read_csv("../make_combined_csv/output/temp-backup/Pluvio_Rain_output.csv")
    df = df[df["stn_Pluvio_Rain"] < 0.1]

    print(df[""])

rain_stats()
