# This file is used to find the relative difference between different weather stations on any particular day.
# If a weather station is too different from its neighbors then it's considered to be faulty, and that value is
# set to None. To be used after the base and bounds checks of the other qa check is done
import time
import pandas
import pandas as pd


# Not generalized, only for 1 variable
# sloppy
def replace_outliers_refactor(df, date_col, attribute, threshold):
    neighboring_stations_df = pd.read_csv("neighboring-stations.csv")

    df = df[df[attribute].notna()]

    df = df.merge(neighboring_stations_df, how="left", left_on=["StnID"], right_on=["Station"])

    for i in range(3):
        i = str(i)
        df_copy = df[["StnID", attribute, date_col]]
        df_copy.rename(columns={attribute: attribute + i}, inplace=True)
        df = df.merge(df[["StnID", attribute, date_col]],
                      how="left",
                      left_on=["Neighbor" + i, date_col],
                      right_on=["StnID", date_col])
        df.rename(columns={"StnID_x": "StnID", attribute + "_x": attribute, attribute + "_y": attribute + i}, inplace=True)
        # df[["StnID", attribute, attribute + i]] = df["StnID_x", attribute + "_x", attribute + "_y"]

    df["mean"] = (df[attribute + "0"] + df[attribute + "1"] + df[attribute + "2"])/3.0
    df[attribute] = df[attribute].mask(abs(df[attribute] - df["mean"]) > threshold)
    df = df.drop(columns=['Neighbor0', 'Neighbor1', 'Neighbor2', 'StnID_y', 'StnID_y', "mean",
                          attribute + "0", attribute + "1", attribute + "2", "Station"])

    # print(df[df[attribute + "_filtered"].isna()][[attribute, "mean"]])

    return df


# dependents are values that are derived or only have meaning with the attribute
def replace_outliers(df, date_col, attributes, attr_offsets, dependents):
    count = 0
    neighbor_frame = pandas.read_csv("neighboring-stations.csv")
    dates = df[date_col].unique()

    # iterate through every similar datetime
    for datetime in dates:
        start_time = time.time()
        # filter by datetime
        date_block = df[df[date_col] == datetime]

        for index, station in date_block.iterrows():
            # find neighbor stations
            neighbor_ids = get_neighbors(station["StnID"], neighbor_frame)
            neighbor_data = date_block[date_block["StnID"].isin(neighbor_ids)]

            # average neighbor attribute values
            attributes_avg = neighbor_data[attributes].mean()

            for attribute in attributes:
                # compare to neighbor avg, remove outlier values
                if station[attribute] > attributes_avg[attribute] + attr_offsets[attribute]:
                    print(f"Station {station['StnID']} ({station['Station']}) reading for attribute {attribute} "
                          f"(avg: {attributes_avg[attribute]}) was past the offset. Its reading was {station[attribute]}")

                    date_block.loc[index, attribute] = None
                    for attr_dep in dependents[attribute]:
                        date_block.loc[index, attr_dep] = None
                    count += 1

                elif station[attribute] < attributes_avg[attribute] - attr_offsets[attribute]:
                    print(f"Station {station['StnID']} ({station['Station']}) reading for attribute {attribute} "
                          f"(avg: {attributes_avg[attribute]}) was past the offset. Its reading was {station[attribute]}")

                    date_block.loc[index, attribute] = None
                    for attr_dep in dependents:
                        date_block.loc[index, attr_dep] = None
                    count += 1
        print("time total: ", time.time() - start_time)
        df[df[date_col] == datetime] = date_block

    print("count: ", count, len(df.index) * len(attributes))
    return df


def get_neighbors(stn_id, neighbor_frame):
    row = neighbor_frame[neighbor_frame["Station"] == stn_id]
    return row.values.tolist()[0][1:]


# used to do quality assurance on data from the 24-hour set. Returns a dataframe with outliers set to None
# takes ~9-10 minutes to run on all the data
def qa_relative_24(df_24):
    date_col = "Date"

    attributes = ["AvgAir_T", "MaxAir_T", "MinAir_T", "AvgRH", "MaxRH", "MinRH", "MaxWS", "AvgWS", "Press_hPa"]
    # Heuristic offset bounds
    #   air temp: +/- 10 degrees
    #   humidity: +/- (10, 15, 20) %
    #   wind speed: +/- 10m/s
    #   pressure: +/- 10 hPa
    humidity_offset = 20
    attr_offsets = {"AvgAir_T": 10, "MaxAir_T": 10, "MinAir_T": 10, "AvgRH": humidity_offset, "MaxRH": humidity_offset,
                    "MinRH": humidity_offset, "MaxWS": 10, "AvgWS": 10, "Press_hPa": 10}
    # "TotRS_MJ": 10

    dependents = {"AvgAir_T": ["EvapTot24"],
                  "MaxAir_T": ["HmMaxAir_T"],
                  "MinAir_T": ["HmMinAir_T"],
                  "AvgRH": ["EvapTot24"],
                  "MaxRH": ["HmMaxRH"],
                  "MinRH": ["HmMinRH"],
                  "MaxWS": ["HmMaxWS"],
                  "AvgWS": ["EvapTot24"]}

    # "TotRS_MJ": ["AvgRS_kw", "MaxRS_kw", "HmMaxRS", "EvapTot24"]

    file = open("start.csv", "w")
    df_24.to_csv(file)
    file.close()

    df_24 = replace_outliers(df_24, date_col, attributes, attr_offsets, dependents)

    file = open("end.csv", "w")
    df_24.to_csv(file)
    file.close()
    return df_24


def qa_relative_60(df_60):
    date_col = "Datetime"

    attributes = ["AvgAir_T", "MaxAir_T", "MinAir_T", "Air_10", "RH", "AvgRH", "MaxWS", "MaxWS_10", "Max5WD_10",
                  "AvgWS", "WS_2Min", "Press_hPa"]

    # Heuristic offset bounds
    #   air temp: +/- 10 degrees
    #   humidity: +/- 20 %
    #   wind speed: +/- 10m/s
    #   air pressure: +/- 15hPa
    humidity_offset = 20
    attr_offsets = {"AvgAir_T": 10, "MaxAir_T": 10, "MinAir_T": 10, "Air_10": 10, "RH": humidity_offset,
                    "AvgRH": humidity_offset, "MaxWS": 10, "MaxWS_10": 10, "Max5WD_10": 10, "AvgWS": 10,
                    "WS_2Min": 10, "Press_hPa": 10}

    dependents = {"MaxWS": ["HmMaxWS", "MaxWD"],
                  "MaxWS_10": ["MaxWD_10"],
                  "WS_2Min": ["WD_2Min"]}

    return replace_outliers(df_60, date_col, attributes, attr_offsets, dependents)


def qa_relative_15(df_15):
    date_col = "Datetime"

    attributes = ["Air_T", "RH", "AvgWS", "MaxWS", "Press_hPa"]

    # Heuristic offset bounds
    #   air temp: +/- 10 degrees
    #   humidity: +/- 20 %
    #   wind speed: +/- 10m/s
    #   air pressure: +/- 15hPa
    attr_offsets = {"Air_T": 10, "RH": 20, "AvgWS": 10, "MaxWS": 10, "Press_hPa": 15}

    dependents = {}

    return replace_outliers(df_15, date_col, attributes, attr_offsets, dependents)


def qa_consecutive_24(df_24):
    start_time = time.time()
    # find every group all the data points into groups where it is consecutively below 0, group of size 1 if it is
    # above zero
    # if TotRS_MJ is below 5 for more than 5 days we want to remove the data
    for index, group in df_24[df_24["TotRS_MJ"] < 5].groupby((df_24['TotRS_MJ'] >= 5).cumsum()):
        if len(group.index) > 5:
            df_24.iloc[group.index] = None

    print(time.time() - start_time)

    file = open("EvapTot24.csv", "w")
    df_24["TotRS_MJ"].to_csv(file)
    file.close()
    return df_24


# define the attrs, offsets, and whatnot
# made, so I didnt have to edit the other functions, while this is
# not meant to be permanently stored.
def general_qa():
    df_path = "../../Python_Scripts/Mark/frost_maps/data/station_temp_data.csv"
    df = pd.read_csv(df_path)
    date_col = "time"
    attributes = ["AvgAir_T"]
    attr_offsets = {"AvgAir_T": 10}
    dependents = []

    df = replace_outliers(df, date_col, attributes, attr_offsets, dependents)
    print(df, df.shape, sep="\n")
    df.to_csv(df_path)


def main():
    df_path = "../../Python_Scripts/Mark/frost_maps/data/station_temp_data.csv"
    df = pd.read_csv(df_path)
    date_col = "time"
    attribute = "AvgAir_T"
    threshold = 10
    df = replace_outliers_refactor(df, date_col, attribute, threshold)
    df.to_csv("../../Python_Scripts/Mark/frost_maps/data/station_temp_data_2.csv", index=False)

    # dff = pandas.read_csv("mock-station-data.csv")
    #
    # print("Starting qa_relative_24")
    #
    # qa_relative_24(dff)
    # # qa_consecutive_24(dff)


if __name__ == "__main__":
    main()
    print("End of program (yay)")
