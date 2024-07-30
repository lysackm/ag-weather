import pandas as pd


def merge_merra_station_data():
    df_merra = pd.read_csv("./data/merra_temp_data.csv", parse_dates=["time"])
    # df_merra["time"] = pd.to_datetime(df_merra["time"])
    df_merra = df_merra[["time", "StnID", "merra_air_temp"]]
    df_station = pd.read_csv("./data/station_temp_data.csv", parse_dates=["time"])
    # df_station["time"] = pd.to_datetime(df_station["time"])

    # print(df_station[df_station["time"].isna()])
    # print(df_merra[df_merra["time"].isna()])

    print("merra", df_merra.dtypes, sep="\n")
    print("station", df_station.dtypes, sep="\n")

    df_merged = df_merra.merge(df_station, how="left", on=["time", "StnID"])

    df_merged["is_merra"] = pd.isna(df_merged["AvgAir_T"])

    return df_merged


def merge_station_ec_data():
    df_station = pd.read_csv("./data/station_temp_data.csv", parse_dates=["time"])
    df_ec = pd.read_csv("./data/environment_canada_temp_data.csv", parse_dates=["time"], dtype={"StnID": str})
    df_station_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

    df_ec = df_ec[df_ec["StnID"] != "5032951"]

    df_station = df_station.merge(df_station_metadata, how="left", on="StnID")
    df_station = df_station[["time", "StnID", "StationName", "LatDD", "LongDD", "AvgAir_T"]]

    df_merged = pd.concat([df_station, df_ec], ignore_index=True)
    df_merged["is_merra"] = False
    df_merged["air_temp_merged"] = df_merged["AvgAir_T"]

    print(df_station, df_ec, df_merged, sep="\n")
    df_merged.to_csv("./data/ec_station_temp_data.csv", index=False)


def merge_era5_station_data():
    df_era5 = pd.read_csv("./data/era5_temp_data.csv", parse_dates=["time"])
    # df_era5["time"] = pd.to_datetime(df_era5["time"])
    df_era5 = df_era5[["time", "StnID", "era5_air_temp"]]
    df_station = pd.read_csv("./data/station_temp_data.csv", parse_dates=["time"])
    # df_station["time"] = pd.to_datetime(df_station["time"])

    # print(df_station[df_station["time"].isna()])
    # print(df_era5[df_era5["time"].isna()])

    print("era5", df_era5.dtypes, sep="\n")
    print("station", df_station.dtypes, sep="\n")

    df_merged = df_era5.merge(df_station, how="left", on=["time", "StnID"])

    df_merged["is_era5"] = pd.isna(df_merged["AvgAir_T"])

    return df_merged


def merge_nrcan_station_data():
    # mint for the whole year, since we only care if there was a frost on a day
    # converts hourly data to daily minimum data
    df_station_metadata = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

    df_nrcan = pd.read_csv("./data/nrcan_temp_data.csv")
    df_nrcan = df_nrcan[["time", "StnID", "nrcan_mint"]]

    df_station = pd.read_csv("./data/station_temp_data.csv")
    df_station["time_utc"] = pd.to_datetime(df_station["time"], utc="true")
    df_station = df_station.groupby([df_station["time_utc"].dt.date,
                                     df_station["StnID"]]).min()
    df_station = df_station.drop(columns=["time_utc"])
    df_station = df_station.reset_index()
    df_station["StnID"] = df_station["StnID"].astype(int)

    df_merged = df_nrcan.merge(df_station, how="outer", on=["time", "StnID"])

    stations = list(set(df_station_metadata["StnID"].unique()) & set(df_station["StnID"].unique()))
    df_merged = df_merged[df_merged["StnID"].isin(stations)]

    df_merged["is_nrcan"] = pd.isna(df_merged["AvgAir_T"])
    df_merged["air_temp_merged"] = df_merged["nrcan_mint"].where(df_merged["is_nrcan"], df_merged["AvgAir_T"])

    df_merged = df_merged.drop(columns=["time_utc"])
    df_merged = df_merged[df_merged["air_temp_merged"].notna()]
    df_merged.to_csv("./data/nrcan_station_temp_data.csv", index=False)


def main():
    # df_merged = merge_era5_station_data()

    # df_merged["air_temp_merged"] = df_merged["era5_air_temp"].where(df_merged["is_era5"], df_merged["AvgAir_T"])
    # df_merged = df_merged.fillna(np.nan)

    # df_merged.to_csv("./data/era5_station_temp_data.csv", index=False)

    # merge_station_ec_data()

    merge_nrcan_station_data()


if __name__ == "__main__":
    main()
