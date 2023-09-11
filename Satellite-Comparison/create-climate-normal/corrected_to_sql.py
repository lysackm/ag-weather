import sqlite3
import glob
import pandas as pd


# db schema
# time, lat, lon, AvgAir_T, AvgWS, Pluvio_Rain, Press_hPa, RH, SolarRad,
def intialize_db():
    conn = sqlite3.connect('D:/data/historical_era5/sql')
    c = conn.cursor()

    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS corrected_data
        ([time] DATE,
        [lat] FLOAT,
        [lon] FLOAT,
        [AvgAir_T] FLOAT,
        [AvgWS] FLOAT,
        [Pluvio_Rain] FLOAT,
        [Press_hPa] FLOAT,
        [RH] FLOAT,
        [SolarRad] FLOAT,
        PRIMARY KEY (time, lat, long)
        ''')

    conn.commit


def csv_to_sql():
    attrs = ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH", "SolarRad"]

    files = glob.glob("D:/data/historical_era5/corrected")

    conn = sqlite3.connect('D:/data/historical_era5/sql')
    c = conn.cursor()

    for attr in attrs:
        for file in files:
            if attr in file:
                df = pd.read_csv(file)
                df.to_sql(name='corrected_data', con=conn, if_exists="replace", index_label=["time", "lat", "lon"])
