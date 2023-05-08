# This file is used to find the relative difference between different weather stations on any particular day.
# If a weather station is too different from its neighbors then it's considered to be faulty, and that value is
# set to None. To be used after the base and bounds checks of the other qa check is done
import time
import pandas


def get_neighbors(stn_id, neighbor_frame):
    row = neighbor_frame[neighbor_frame["Station"] == stn_id]
    return row.values.tolist()[0][1:]


# used to do quality assurance on data from the 24-hour set. Returns a dataframe with outliers set to None
# takes ~9-10 minutes to run on all the data
def qa_relative_24(df_24):
    date_col = "Date"

    attributes = ["AvgAir_T", "MaxAir_T", "MinAir_T", "AvgRH", "MaxRH", "MinRH", "MaxWS", "AvgWS"]
    # attributes = ["AvgRH", "MaxRH", "MinRH"]
    # Heuristic offset bounds
    #   air temp: +/- 10 degrees
    #   humidity: +/- (10, 15, 20) %
    #   wind speed: +/- 10m/s
    humidity_offset = 20
    attr_offsets = {"AvgAir_T": 10, "MaxAir_T": 10, "MinAir_T": 10, "AvgRH": humidity_offset, "MaxRH": humidity_offset,
                    "MinRH": humidity_offset, "MaxWS": 10, "AvgWS": 10, "TotRS_MJ": 10}

    dependents = {"AvgAir_T": ["EvapTot24"],
                  "MaxAir_T": ["HmMaxAir_T"],
                  "MinAir_T": ["HmMinAir_T"],
                  "AvgRH": ["EvapTot24"],
                  "MaxRH": ["HmMaxRH"],
                  "MinRH": ["HmMinRH"],
                  "MaxWS": ["HmMaxWS"],
                  "AvgWS": ["EvapTot24"],
                  "TotRS_MJ": ["AvgRS_kw", "MaxRS_kw", "HmMaxRS", "EvapTot24"]}

    count = 0

    # for customized offsets have a dictionary with all the attribute types, then you can get corresponding offset
    # for the 2nd version of the code this has 0 cost problems
    neighbor_frame = pandas.read_csv("neighboring-stations.csv")

    dates = df_24[date_col].unique()
    file = open("start.csv", "w")
    df_24.to_csv(file)
    file.close()

    for date in dates:
        start_time = time.time()
        # filter by datetime
        date_block = df_24[df_24[date_col] == date]

        for index, station in date_block.iterrows():
            neighbor_ids = get_neighbors(station["StnID"], neighbor_frame)
            neighbor_data = date_block[date_block["StnID"].isin(neighbor_ids)]

            # t=0.11 sec per day
            attributes_avg = neighbor_data[attributes].mean()

            for attribute in attributes:
                # Remove outlier values
                if station[attribute] > attributes_avg[attribute] + attr_offsets[attribute]:
                    print(f"Station {station['StnID']} ({station['Station']}) reading for attribute {attribute} "
                          f"(avg: {attributes_avg[attribute]}) was past the offset. Its reading was {station[attribute]}")
                    print("Setting value to NULL")
                    date_block.loc[index, attribute] = None
                    for attr_dep in dependents:
                        date_block.loc[index, attr_dep] = None
                    print(neighbor_data[attribute])
                    print(neighbor_data["Station"])
                    count += 1

                elif station[attribute] < attributes_avg[attribute] - attr_offsets[attribute]:
                    print(f"Station {station['StnID']} ({station['Station']}) reading for attribute {attribute} "
                          f"(avg: {attributes_avg[attribute]}) was past the offset. Its reading was {station[attribute]}")
                    print("Setting value to NULL")
                    date_block.loc[index, attribute] = None
                    print(neighbor_data[attribute])
                    print(neighbor_data["Station"])
                    date_block.loc[index, attribute] = None
                    for attr_dep in dependents:
                        date_block.loc[index, attr_dep] = None
                    count += 1
        print("time total: ", time.time() - start_time)
        df_24[df_24[date_col] == date] = date_block

    file = open("end.csv", "w")
    df_24.to_csv(file)
    file.close()
    print("count: ", count, len(df_24.index) * len(attributes))
    return df_24


def qa_consecutive_24(df_24):
    # need to group by station id first
    for index, group in df_24[df_24["EvapTot24"] < 5].groupby((df_24['EvapTot24'] >= 5).cumsum()):
        if len(group.index) > 5:
            print(group)
            df_24.iloc[group.index] = None

    return df_24


df = pandas.read_csv("mock-station-data.csv")

print("Starting qa_relative_24")

# qa_relative_24(df)
qa_consecutive_24(df)

print("End of program (yay)")
