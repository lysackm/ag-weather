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


output_df = pd.DataFrame()

# print the both rain columns when the absolute difference is greater than 10mm
for year in range(2018, 2022):
    stn_df = load_stn_data(year)
    stn_df["diff"] = abs(stn_df["Pluvio_Rain"] - stn_df["TBRG_Rain"])
    stn_df = stn_df[stn_df["diff"] > 10]
    print(stn_df[["time", "Pluvio_Rain", "TBRG_Rain"]])
    print(len(stn_df))

    output_df = pd.concat([output_df, stn_df[["time", "Pluvio_Rain", "TBRG_Rain"]]])

output_df.to_csv("rain_comparison.csv", index=False)
