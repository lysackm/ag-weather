import pandas as pd
import glob

from pandas import NaT

data_dir = "../../../../data/environment_canada/1993-2023/"


def process_environment_canada_data():
    station_data_dir = data_dir + "*.csv"
    station_files = glob.glob(station_data_dir)
    print(station_files, station_data_dir)

    temp_dfs = []

    for file in station_files:
        print(file)
        df = pd.read_csv(file, encoding='unicode_escape')
        df["time"] = df["Date/Time (LST)"]
        df_temp = df[["time", "Station Name", "Climate ID", "Longitude (x)", "Latitude (y)", "Temp (°C)"]]
        df_temp = df_temp.rename(columns={"Station Name": "StationName",
                                          "Climate ID": "StnID",
                                          "Longitude (x)": "LongDD",
                                          "Latitude (y)": "LatDD",
                                          "Temp (°C)": "AvgAir_T"})
        temp_dfs.append(df_temp)

    df_temp_merged = pd.concat(temp_dfs)
    df_temp_merged["time"] = pd.to_datetime(df_temp_merged["time"])
    df_temp_merged["time"] = df_temp_merged["time"].dt.tz_localize(tz="America/Winnipeg",
                                                                   ambiguous="NaT",
                                                                   nonexistent="shift_forward")

    df_temp_merged = df_temp_merged.where((df_temp_merged.time.dt.year < 2024) & (df_temp_merged.time.dt.year > 1993))
    df_temp_merged = df_temp_merged.where((df_temp_merged.LatDD > 49.0) & (df_temp_merged.LatDD < 52.5))
    df_temp_merged.dropna(inplace=True, how="all")
    df_temp_merged = df_temp_merged[~df_temp_merged["AvgAir_T"].isna()]

    df_temp_merged.set_index(["time", "StnID"], inplace=True)
    df_temp_merged = df_temp_merged[~df_temp_merged.index.duplicated(keep="last")]

    df_temp_merged.to_csv("./data/environment_canada_temp_data.csv")
    print(df_temp_merged)


if __name__ == "__main__":
    process_environment_canada_data()
