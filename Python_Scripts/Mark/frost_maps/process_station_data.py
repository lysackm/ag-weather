import pandas as pd
import glob

from pandas import NaT

data_dir = "../../../../data/station-csv/"


def process_station_data():
    # stn_df = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

    station_data_dir = data_dir + "*.csv"
    station_files = glob.glob(station_data_dir)
    print(station_files, station_data_dir)

    temp_dfs = []

    for file in station_files:
        print(file)
        df = pd.read_csv(file)
        df["time"] = df["TMSTAMP"]
        df_temp = df[["time", "StnID", "AvgAir_T"]]
        temp_dfs.append(df_temp)

    df_temp_merged = pd.concat(temp_dfs)
    df_temp_merged["time"] = pd.to_datetime(df_temp_merged["time"])
    df_temp_merged["time"] = df_temp_merged["time"].dt.tz_localize(tz="America/Winnipeg",
                                                                   ambiguous="NaT",
                                                                   nonexistent="shift_forward")
    df_temp_merged = df_temp_merged.where(df_temp_merged.time.dt.year != 2024)
    df_temp_merged.dropna(inplace=True, how="all")

    df_temp_merged.set_index(["time", "StnID"], inplace=True)
    df_temp_merged = df_temp_merged[~df_temp_merged.index.duplicated(keep="last")]
    df_temp_merged["AvgAir_T"].replace("\\N", "", inplace=True)

    df_temp_merged.to_csv("./data/station_temp_data.csv")
    print(df_temp_merged)


if __name__ == "__main__":
    process_station_data()
