# program to read in the merra data csv's and then apply an operation to the column that holds the data.
# Mostly to convert units to be the same as station data units.

import glob
import os

import pandas as pd

attributes = ["total-precipitation", "ground-wetness-root", "ground-wetness-top", "avg-prof-soil-moisture",
             "Incident-shortwave-land", "2-meter-specific-humidity"]


def isolate_station_names(filepath, directory):
    station_names = filepath[len(directory) + 1:-4]
    station_names = station_names.replace(" ", "_")
    station_names = station_names.replace("_hourly", "")
    station_names = station_names.replace(".", "")
    return station_names


def main(attribute):
    directory = 'D:\merradownload\\' + attribute
    output_dir = '.\output\\' + attribute + '.csv'
    is_first = True

    if os.path.exists(output_dir):
        os.remove(output_dir)

    for filename in glob.iglob(f'{directory}/*.csv'):
        df = pd.read_csv(filename)
        df[attribute] = df[attribute] + 273.15

        # make new column called StnNames
        stn_names = isolate_station_names(filename, directory)
        df["StnNames"] = stn_names

        # replace 0 column with correct time indicator
        df["time"] = range(0, len(df["time"]))
        df["time"] = df["time"] % 24

        if is_first:
            df.to_csv(output_dir, mode='a', header=not os.path.exists(output_dir))
            is_first = False
        else:
            df.to_csv(output_dir, mode="a", header=False)


for attribute in attributes:
    main(attribute)
