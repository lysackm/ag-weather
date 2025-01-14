import pandas as pd


# p is a function defined in the p-days calculation
def p(t):
    k = 1

    if t < 7:
        return t * 0
    elif 7 <= t < 21:
        return k * (1 - ((t - 21) ** 2 / (21 - 7) ** 2))
    elif 21 <= t < 30:
        return k * (1 - ((t - 21) ** 2 / (30 - 21) ** 2))
    elif 30 <= t:
        return t * 0

    print("fatal error, outside of defined behaviour in p(t)", t)
    exit(1)


# https://www.gov.mb.ca/agriculture/weather/agricultural-climate-of-mb.html
def calculate_p_day(t_min, t_max):
    t1 = p(t_min)
    t2 = p(((2 * t_min) + t_max)/3)
    t3 = p((t_min + (2 * t_max))/3)
    t4 = p(t_max)

    return (1/24) * (5 * t1 + 8 * t2 + 8 * t3 + 3 * t4)


# https://www.gov.mb.ca/agriculture/weather/agricultural-climate-of-mb.html
def calculate_chu(t_min, t_max):
    chu = (1.8 * (t_min - 4.4) + 3.33 * (t_max - 10) - 0.084 * (t_max - 10) ** 2) / 2.0
    return chu.clip(0)


# https://www.gov.mb.ca/agriculture/weather/agricultural-climate-of-mb.html
def calculate_gdd(t_min, t_max):
    conditional = (t_min + t_max)/2 - 5

    if conditional > 0:
        return conditional
    elif conditional <= 0:
        return 0


def filter_dates(df):
    df = df[(df["NormYY"] >= 1991) & (df["NormYY"] <= 2020)]
    return df


def filter_stations(df):
    stn_ids = pd.read_csv("./metadata/station_metadata.csv")["StnID"].to_list()
    df = df[df["StnID"].isin(stn_ids)]
    return df


def merge_columns(df):
    df["Tmin_source"] = "mbag"
    df["Tmin"] = df["mbag_Tmin"]
    df["Tmin_source"] = df["Tmin_source"].mask(df["Tmin"].isna(), "eccc")
    df["Tmin"] = df["Tmin"].fillna(df["eccc_Tmin"])
    df["Tmin_source"] = df["Tmin_source"].mask(df["Tmin"].isna(), "nrcan")
    df["Tmin"] = df["Tmin"].fillna(df["nrcan_Tmin"])
    df["Tmin_source"] = df["Tmin_source"].mask(df["Tmin"].isna(), "invalid")

    df["Tmax_source"] = "mbag"
    df["Tmax"] = df["mbag_Tmax"]
    df["Tmax_source"] = df["Tmax_source"].mask(df["Tmax"].isna(), "eccc")
    df["Tmax"] = df["Tmax"].fillna(df["eccc_Tmax"])
    df["Tmax_source"] = df["Tmax_source"].mask(df["Tmax"].isna(), "nrcan")
    df["Tmax"] = df["Tmax"].fillna(df["nrcan_Tmax"])
    df["Tmax_source"] = df["Tmax_source"].mask(df["Tmax"].isna(), "invalid")

    df["Tavg_source"] = "mbag"
    df["Tavg"] = df["mbag_Tavg"]
    df["Tavg_source"] = df["Tavg_source"].mask(df["Tavg"].isna(), "eccc")
    df["Tavg"] = df["Tavg"].fillna(df["eccc_Tavg"])
    df["Tavg_source"] = df["Tavg_source"].mask(df["Tavg"].isna(), "era5")
    df["Tavg"] = df["Tavg"].fillna(df["era5_Tavg"])
    df["Tavg_source"] = df["Tavg_source"].mask(df["Tavg"].isna(), "invalid")

    df["PPT_source"] = "mbag"
    df["PPT"] = df["mbag_PPT"]
    df["PPT_source"] = df["PPT_source"].mask(df["PPT"].isna(), "eccc")
    df["PPT"] = df["PPT"].fillna(df["eccc_PPT"])
    df["PPT_source"] = df["PPT_source"].mask(df["PPT"].isna(), "nrcan")
    df["PPT"] = df["PPT"].fillna(df["nrcan_PPT"])
    df["PPT_source"] = df["PPT_source"].mask(df["PPT"].isna(), "invalid")

    df = df[["StnID", "NormYY", "NormMM", "NormDD", "DateDT",
             "Tavg", "Tavg_source", "Tmin", "Tmin_source", "Tmax", "Tmax_source", "PPT", "PPT_source"]]

    return df


def combine_daily_data():
    # contains PPT, Tmin, Tmax
    df_nrcan = pd.read_csv("./data/standardized_daily/nrcan.csv")
    df_nrcan = df_nrcan.rename(columns={"PPT": "nrcan_PPT",
                                        "Tmin": "nrcan_Tmin",
                                        "Tmax": "nrcan_Tmax"})
    df_nrcan = df_nrcan.set_index(["StnID", "NormYY", "NormMM", "NormDD", "DateDT"])

    df_era5 = pd.read_csv("./data/standardized_daily/era5_temperature.csv")
    df_era5 = df_era5.rename(columns={"Tavg": "era5_Tavg",
                                      "Tmin": "era5_Tmin",
                                      "Tmax": "era5_Tmax"})
    df_era5 = df_era5.set_index(["StnID", "NormYY", "NormMM", "NormDD", "DateDT"])

    # contains PPT, Tmin, Tmax
    df_eccc = pd.read_csv("./data/standardized_daily/eccc.csv")
    df_eccc = df_eccc.rename(columns={"PPT": "eccc_PPT",
                                      "Tmin": "eccc_Tmin",
                                      "Tmax": "eccc_Tmax",
                                      "Tavg": "eccc_Tavg"})
    df_eccc = df_eccc.set_index(["StnID", "NormYY", "NormMM", "NormDD", "DateDT"])

    # contains Tmin, Tmax, PPT
    df_mbag = pd.read_csv("./data/standardized_daily/mbag_stations.csv")
    df_mbag = df_mbag.rename(columns={"PPT": "mbag_PPT",
                                      "Tmin": "mbag_Tmin",
                                      "Tmax": "mbag_Tmax",
                                      "Tavg": "mbag_Tavg"})
    df_mbag = df_mbag.set_index(["StnID", "NormYY", "NormMM", "NormDD", "DateDT"])

    df_joined = df_nrcan.join([df_era5, df_eccc, df_mbag],
                              how="outer")
    df_joined = df_joined.reset_index()
    return df_joined


def create_composite_daily_data():
    df = combine_daily_data()
    df = merge_columns(df)
    df = filter_stations(df)
    df = filter_dates(df)
    df.to_csv("./data/merged_dataset_2024_normal.csv", index=False)
    return df


def create_composite_climate_normal():
    df = create_composite_daily_data()

    # drop source columns and DateDT, NormYY (NormYY is set as 2020, DateDT will be constructed) and SN
    df = df.drop(columns=["Tavg_source", "Tmin_source", "Tmax_source", "PPT_source", "DateDT", "NormYY"])

    # group by NormMM, NormDD, StnID, SN
    df = df.groupby(["NormMM", "NormDD", "StnID"]).mean()
    df = df.reset_index()

    # drop feb 29th (leap year day)
    df = df[(df["NormMM"] != 2) | (df["NormDD"] != 29)]

    # NormYY is the year which the end of the climate normal span (inclusive)
    df["NormYY"] = 2020
    date_df = df[["NormYY", "NormMM", "NormDD"]].rename(columns={"NormYY": "year", "NormMM": "month", "NormDD": "day"})
    df["DateDT"] = pd.to_datetime(date_df[["year", "month", "day"]])

    # Arbitrary non leap year
    date_df["year"] = 2001
    df["non_leap_year_date"] = pd.to_datetime(date_df[["year", "month", "day"]])
    df["JD"] = df["non_leap_year_date"].dt.dayofyear
    df.drop(columns=["non_leap_year_date"])

    df["CHU"] = df[["Tmin", "Tmax"]].apply(lambda row: calculate_chu(row["Tmin"], row["Tmax"]), axis=1)
    df["GDD"] = df[["Tmin", "Tmax"]].apply(lambda row: calculate_gdd(row["Tmin"], row["Tmax"]), axis=1)
    df["PDay"] = df[["Tmin", "Tmax"]].apply(lambda row: calculate_p_day(row["Tmin"], row["Tmax"]), axis=1)

    # merge in station metadata
    normal_station_metadata_df = pd.read_csv("./metadata/merged_climate_normal_stns.csv")
    normal_station_metadata_df = normal_station_metadata_df[["StnID", "StationName", "lat", "long", "NormLocation"]]
    df = df.merge(normal_station_metadata_df, on=["StnID"], how="left")

    df = df.round(2)
    df = df.rename(columns={"StationName": "Location"})
    df = df[["StnID", "Location", "NormYY", "NormMM", "NormDD", "DateDT", "JD", "Tmax", "Tmin", "Tavg", "PPT",
             "CHU", "GDD", "PDay", "NormLocation"]]

    df.to_csv("./data/climate_normal/2020_MBAg_normal.csv", index=False)


def main():
    create_composite_climate_normal()


if __name__ == "__main__":
    main()
