import glob

import pandas as pd
import datetime
import json
import geopy.distance


def load_data(hour="06"):
    df = pd.read_csv("data/wind_data/" + hour + "_wind_data.csv")
    return df


def save_data(df, hour="06"):
    df.to_csv("data/wind_data/" + hour + "_wind_data.csv", index=False)


def calculate_forecasted_date(row):
    return datetime.datetime.fromtimestamp(row["valid_date"] / 1000.0).isoformat()


def remove_t_forecasted_date(row):
    return row["forecasted_date"].replace("T", " ")


def remove_t_date(row):
    return row["date"].replace("T", " ")


def remove_t(df):
    df["forecasted_date"] = df.apply(calculate_forecasted_date, axis=1)
    df["forecasted_date"] = df.apply(remove_t_forecasted_date, axis=1)
    df["date"] = df.apply(remove_t_date, axis=1)
    return df


def process_data(hour="06"):
    df = load_data()
    df["forecasted_date"] = df.apply(calculate_forecasted_date, axis=1)
    save_data(df, hour)


def extract_rm_centroid():
    with open('data/rm_centroids.geojson', 'r') as file:
        json_data = json.load(file)

    features = json_data["features"]

    exported_data = []

    for rm in features:
        exported_data.append({"rm_name": rm["properties"]["MUNI_NAME"], "longitude": rm["geometry"]["coordinates"][0],
                              "latitude": rm["geometry"]["coordinates"][1]})

    df = pd.DataFrame(exported_data)
    df.to_csv("data/rm_centroids.csv", index=False)


def rm_to_station_mapping():
    df_rm = pd.read_csv("data/rm_centroids.csv")
    df_station = pd.read_csv("data/StationList.csv")

    mapping = []

    for index_rm, row_rm in df_rm.iterrows():
        min_distance = 200
        station_name = ""
        station_id = 0

        rm_coords = (row_rm["latitude"], row_rm["longitude"])

        for index_station, row_station in df_station.iterrows():
            station_coords = (row_station["LatDD"], row_station["LongDD"])

            dist = geopy.distance.distance(rm_coords, station_coords)
            # print(dist, rm_coords, station_coords)
            if dist < min_distance:
                min_distance = dist
                station_name = row_station["StationName"]
                station_id = row_station["StnID"]

        mapping.append(
            {"rm_name": row_rm["rm_name"], "station_name": station_name, "stn_id": station_id, "distance": round(min_distance.km, 2)})

    df = pd.DataFrame(mapping)
    df.to_csv("data/rm_station_mapping.csv", index=False)


def merge_rm_with_wind_data(df_wind):
    df_mapping = pd.read_csv("data/rm_station_mapping.csv")

    df_wind = df_wind.merge(df_mapping, how="left", left_on="muni_name", right_on="rm_name")

    print(df_wind.columns)
    return df_wind


def frequent_forecasted_data():
    dataframes = []
    for hour in ["00", "06", "12", "18"]:
        df = load_data(hour)
        df = df[df["offset"] < 6]
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv("frequent_forecasted_data.csv", index=False)


def correct_wind_speed(df):
    df["ws"] = df["ws"] * 0.277778
    df["ws_pbl"] = df["ws_pbl"] * 0.277778

    return df


def filter_for_crb_season(df):
    has_timestamp = False
    if "TMSTAMP" in df.columns:
        df = df.rename(columns={"TMSTAMP": "date"})
        has_timestamp = True

    # crb program operates from August 1st - November 15th
    # XXXX-08-01 to XXXX-10-15, or alternatively 801 to 1015
    df["date"] = pd.to_datetime(df["date"])

    month_day = df["date"].dt.month * 100 + df["date"].dt.day
    df = df[month_day.between(801, 1015)]

    if has_timestamp:
        df = df.rename(columns={"date": "TMSTAMP"})
    return df


def merge_data():
    # running analysis on 12am forecast
    df_wind = pd.read_csv("data/seasonal_wind_data/06_wind_data.csv")
    df_station = pd.read_csv("data/seasonal_station_data/seasonal_station_data.csv")

    df_wind["forecasted_date"] = pd.to_datetime(df_wind["forecasted_date"])
    df_station["TMSTAMP"] = pd.to_datetime(df_station["TMSTAMP"])

    df_merged = df_wind.merge(df_station, how="inner", left_on=["stn_id", "forecasted_date"],
                              right_on=["StnID", "TMSTAMP"])
    df_merged.to_csv("data/merged/merged_wind_data.csv", index=False)


def hour_rounder(t):
    # Rounds to the nearest hour by adding a timedelta hour if minute >= 30
    hours = (t.hour // 6) * 6 + ((t.hour % 6) // 3) * 6

    return t.replace(second=0, microsecond=0, minute=0, hour=0) + datetime.timedelta(hours=hours)


def merge_closest_forecasted_date():
    # ws -> WS_2Min
    # wd -> WD_2Min
    # ws_pbl (ws at planetary boundary layer) -> itself
    # wd_pbl (wind direction at planetary boundary layer) -> itself
    # hgt_pbl (height of planetary boundary layer) -> itself
    # vrate (Ventilation Rate) -> itself

    # cf stands for closest forecast

    df_wind = pd.read_csv("data/merged/merged_wind_data.csv")
    df_wind["forecasted_date"] = pd.to_datetime(df_wind["forecasted_date"])

    df_closest_forecasted = pd.read_csv("data/frequent_forecasted_data.csv")
    df_closest_forecasted["forecasted_date"] = pd.to_datetime(df_closest_forecasted["forecasted_date"])

    df_closest_forecasted[["stn_id", "ws_cf", "wd_cf", "ws_pbl_cf", "wd_pbl_cf", "hgt_pbl_cf", "vrate_cf"]] = \
        df_closest_forecasted[["stn_id", "ws", "wd", "ws_pbl", "wd_pbl", "hgt_pbl", "vrate"]]
    df_closest_forecasted = df_closest_forecasted[
        ["muni_name", "forecasted_date", "ws_cf", "wd_cf", "ws_pbl_cf", "wd_pbl_cf", "hgt_pbl_cf", "vrate_cf"]]

    df_merged = df_wind.merge(df_closest_forecasted, how="left", left_on=["muni_name", "forecasted_date"],
                              right_on=["muni_name", "forecasted_date"])

    df_merged = df_merged.rename(columns={"AvgWS": "avg_ws_stn", "WS_2Min": "2min_ws_stn",
                                          "AvgWD": "avg_wd_stn", "WD_2Min": "2min_wd_stn"})
    df_merged = df_merged[
        ["date", "forecasted_date", "TMSTAMP", "offset", "station_name", "stn_id", "distance", "muni_name",
         "ws",  "avg_ws_stn", "2min_ws_stn", "ws_cf",
         "wd", "avg_wd_stn", "2min_wd_stn", "wd_cf",
         "ws_pbl", "ws_pbl_cf",
         "wd_pbl", "wd_pbl_cf",
         "hgt_pbl", "hgt_pbl_cf",
         "vrate", "vrate_cf"]]

    df_merged.to_csv("data/forecast_match/forecast_match.csv", index=False)


def main():
    # extract_rm_centroid()
    # rm_to_station_mapping()

    # for hour in ["00", "06", "12", "18"]:
    #     df = load_data(hour)
    #     df = remove_t(df)
    #     df = correct_wind_speed(df)
    #     df = merge_rm_with_wind_data(df)
    #     save_data(df, hour)

    # for hour in ["00", "06", "12", "18"]:
    #     df = load_data(hour)
    #     df = filter_for_crb_season(df)
    #     df.to_csv("./data/seasonal_wind_data/" + hour + "_wind_data.csv", index=False)

    # files = glob.glob("./data/station_csv/*.csv")
    # dfs = []
    # for file in files:
    #     df = pd.read_csv(file)
    #     df = filter_for_crb_season(df)
    #     dfs.append(df)
    # df = pd.concat(dfs)
    # df = df[["StnID", "TMSTAMP", "WS_2Min", "WD_2Min", "AvgWS", "AvgWD"]]
    # df.to_csv("./data/seasonal_station_data/seasonal_station_data.csv", index=False)

    # frequent_forecasted_data()

    merge_data()
    merge_closest_forecasted_date()


if __name__ == "__main__":
    main()
