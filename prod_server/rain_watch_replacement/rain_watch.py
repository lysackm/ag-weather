import datetime
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


# replace the rain_watch RTMC page, would have to be run off a bat file
# which would be triggered by windows task scheduler. Probably want to
# take the data from one of the parner pages, as to not touch the dat
# files and further slow down RTMC. Save the image in the same directory
# as the old rain watch image, with the same name and there shouldnt be
# a problem. (hopefully)
# MBAg is likely the partner with the highest likelihood of having all
# the required data.

# open file (pandas?, or just grab the last month of daily data?)
# get most recent hour row for each station
# get last month of 24 hour data

# make a df with x_coord, y_coord, hour_precip, 24hr_precip, month_precip, TMSTAMP, Station name?
# probably best if I just add the time stamp to the top of the screen, only report station which have reported data
# in the last hour
# station name is cluttered and sometimes misleading
# do what NDAWN does and add a gradient but make no claims about the accuracy of the gradiant
# make it higher resolution?

# geopandas is unlikely the correct package to use for this project

def make_precip_df():
    dir_60 = "./data/mawp60raw.txt"

    header_60 = ["TMSTAMP", "RECNBR", "StnID", "BatMin", "Air_T", "AvgAir_T", "MaxAir_T", "MinAir_T", "RH", "AvgRH",
                 "Pluvio_Rain", "Pluvio_Rain24RT", "WS_10Min", "WD_10Min", "AvgWS", "AvgWD", "AvgSD", "MaxWS_10",
                 "MaxWD_10", "MaxWS", "HmMaxWS", "MaxWD", "Max5WS_10", "Max5WD_10", "WS_2Min", "WD_2Min", "Soil_T05",
                 "AvgRS_kw", "TotRS_MJ", "TBRG_Rain", "TBRG_Rain24RT", "Soil_TP5_TempC", "Soil_TP5_VMC",
                 "Soil_TP20_TempC", "Soil_TP20_VMC", "Soil_TP50_TempC", "Soil_TP50_VMC", "Soil_TP100_TempC",
                 "Soil_TP100_VMC", "Evap60", "SolarRad", "Press_hPa"]

    df_raw = pd.read_csv(dir_60, header=0, names=header_60, skipfooter=1, engine="python")
    df_raw = df_raw[["TMSTAMP", "StnID", "Pluvio_Rain", "Pluvio_Rain24RT"]]
    df_raw["TMSTAMP"] = pd.to_datetime(df_raw["TMSTAMP"])

    df_60 = df_raw.iloc[df_raw.groupby("StnID")["TMSTAMP"].idxmax()]

    # get start of the month
    month_start_date = pd.offsets.MonthBegin().rollback(datetime.datetime.now())
    month_start_date = month_start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    df_month = df_raw[df_raw["TMSTAMP"] > month_start_date]
    df_month = df_month.groupby("StnID")["Pluvio_Rain"].sum()
    df_month = df_month.rename("month_total")

    df = df_60.merge(df_month, how="outer", on="StnID")

    station_metadata = pd.read_csv("./data/station_metadata.csv")

    station_metadata = station_metadata[["StnID", "LatDD", "LongDD"]]
    df = df.merge(station_metadata, how="left", on="StnID")

    return df


def make_gdf(df):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LongDD, df.LatDD), crs="EPSG:4326")
    return gdf


def graph_rain_stations(gdf):
    rm_map = gpd.read_file("./shape_files/Official_RM_Boundaries_2015/MB_RM_Boundaries.shp")
    rm_map.plot()
    ax = rm_map.plot(color="white", edgecolor="black")
    gdf.plot(ax=ax, color="red")
    plt.show()


def main():
    df = make_precip_df()
    gdf = make_gdf(df)
    graph_rain_stations(gdf)


if __name__ == "__main__":
    main()
