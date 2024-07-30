import datetime
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import maskoceans
from scipy.interpolate import griddata


def graph_frost_dates_on_map(df, title="Interpolated Frost Dates", scale="low-high"):
    stations_x = df["LongDD"]
    stations_y = df["LatDD"]
    station_values = df["day_of_year"]
    # Create a grid for interpolation
    grid_x, grid_y = np.meshgrid(np.linspace(-102, -94, 80), np.linspace(48, 53, 50))

    # Interpolate station values to the grid
    grid_values = griddata((stations_x, stations_y), station_values, (grid_x, grid_y), method='linear')

    m = Basemap(projection='lcc',
                resolution='f', lat_0=50., lon_0=-98., llcrnrlon=-102, llcrnrlat=48.8, urcrnrlon=-95, urcrnrlat=52.4)
    # draw coastlines, colour oceans, continents and lakes
    m.drawrivers()
    m.drawcountries()
    m.drawstates()
    m.drawcoastlines()

    if scale == "low-high":
        cmap = "coolwarm"
    elif scale == "high-low":
        cmap = "coolwarm_r"

    ct = m.contourf(grid_x, grid_y, grid_values, levels=20, cmap=cmap, latlon=True)
    m.scatter(stations_x, stations_y, c='red', marker='o', label='Stations', latlon=True)
    m.colorbar(ct)

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    plt.legend()
    plt.show()


# graphs the frost date and can either give random colours per station, or
# colour merra blue and station data red. It graphs the temperature to the
# date of the frost.
def graph_frost_dates(df, title="", ra="era5"):
    if ra == "era5":
        is_ra = "is_era5"
        legend = "Era5"
    elif ra == "merra":
        is_ra = "is_merra"
        legend = "Merra"
    elif ra == "nrcan":
        is_ra = "is_nrcan"
        legend = "nrcan"
    else:
        print("did not specify the reanalysis_product, exiting")
        exit(1)

    grouped = df.groupby("StnID")
    fig, ax = plt.subplots()

    fmt = mdates.DateFormatter('%b %d')
    ax.xaxis.set_major_formatter(fmt)

    for name, group in grouped:
        dates = pd.to_datetime(1970 * 1000 + group['day_of_year'], format='%Y%j')

        # ax.scatter(dates, group["air_temp_merged"], alpha=1, c=np.random.rand(3,))
        colour_col = group[is_ra].apply(lambda x: "blue" if x else "red")
        ax.scatter(dates, group["air_temp_merged"], alpha=0.3, c=colour_col)

    plt.xlabel("date")
    plt.ylabel("temperature celsius")
    plt.legend([legend, "station data"])
    plt.title(title)
    leg = ax.get_legend()
    leg.legend_handles[0].set_color('blue')
    leg.legend_handles[1].set_color('red')
    plt.show()
    plt.clf()


def graph_frost_free(df, title="", ra="era5"):
    if ra == "era5":
        is_ra = "is_era5"
        legend = "Era5"
    elif ra == "merra":
        is_ra = "is_merra"
        legend = "Merra"
    elif ra == "nrcan":
        is_ra = "is_nrcan"
        legend = "nrcan"
    else:
        print("did not specify the reanalysis_product, exiting")
        exit(1)

    grouped = df.groupby("StnID")
    fig, ax = plt.subplots()

    for name, group in grouped:
        colour_col = group[is_ra].apply(lambda x: "blue" if x else "red")
        ax.scatter(group["day_of_year"], group["air_temp_merged"], alpha=0.3, c=colour_col)

    plt.xlabel("date")
    plt.ylabel("temperature celsius")
    plt.legend([legend, "station data"])
    plt.title(title)
    leg = ax.get_legend()
    leg.legend_handles[0].set_color('blue')
    leg.legend_handles[1].set_color('red')
    plt.show()
    plt.clf()


def map_year(year):
    if year % 4 == 0:
        return 1
    else:
        return 0


def compensate_for_leap_years(df):
    df = df.reset_index()
    regex = "([0-9]{4})"
    df["year"] = df["season"].str.extract(regex).astype(int)
    df["leap_year_offset"] = df["year"].map(map_year)
    df["day_of_year"] = df["day_of_year"] - df["leap_year_offset"]
    return df


def calculate_day_of_year(df):
    df["day_of_year"] = df["time"].dt.dayofyear
    return df


def calculate_frost_avg(df):
    return df.groupby("StnID").mean()


def calculate_frost_quantile(df, quantile):
    return df.groupby("StnID").quantile(quantile)


def calculate_first_frost(df):
    # change ds to only be fall, calculate first day which goes below 0
    df = df[df["season"].str.match("fall[0-9]{4}")]
    df = df.groupby(["season", "StnID"]).first()
    df = calculate_day_of_year(df)
    return df
    # print(df)


def calculate_last_frost(df):
    # change ds to only be fall, calculate first day which goes below 0
    df = df[df["season"].str.match("spring[0-9]{4}")]
    df = df.groupby(["season", "StnID"]).last()
    df = calculate_day_of_year(df)
    return df
    # print(df)


# separate the year into two halves, January to June, and July to December (inclusive)
def map_seasons(date):
    month = date.month
    year = date.year

    if 1 <= month <= 6:
        return "spring" + str(year)
    elif 7 <= month <= 12:
        return "fall" + str(year)

    print("something went wrong when mapping the seasons, exiting")
    exit(1)


def reformat_frost_dataframe(df):
    df = df.reset_index()

    station_metadata_df = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv",
                                      dtype={"StnID": str})
    df = df.merge(station_metadata_df, how="left", on="StnID")

    # already had a LatDD and LongDD columns
    if "LatDD_x" in df.columns:
        df["LatDD"] = df["LatDD_x"].where(df["LatDD_x"].notna(), df["LatDD_y"])
        df["LongDD"] = df["LongDD_x"].where(df["LongDD_x"].notna(), df["LongDD_y"])

        df = df[df["LatDD"].notna() & df["LongDD"].notna()]

    df["date"] = pd.to_datetime(2023 * 1000 + df['day_of_year'].round(), format='%Y%j')
    return df[["StnID", "StationName", "LatDD", "LongDD", "date", "day_of_year"]]


def merra_vs_station_stats():
    df = pd.read_csv("./data/merged_temp_data.csv",
                     dtype={"StnID": str, "merra_air_temp": float, "is_merra": bool, "air_temp_merged": float},
                     parse_dates=["time"])

    # remove all non-freezing days
    df = df[df["air_temp_merged"] < 0]
    df["season"] = df["time"].map(map_seasons)

    print("calculate first frost")
    first_frost = calculate_first_frost(df)
    first_frost = compensate_for_leap_years(first_frost)
    print("First Frost Merra avg:", first_frost["day_of_year"][first_frost["is_merra"] == True].mean())
    print("First Frost Station avg:", first_frost["day_of_year"][first_frost["is_merra"] != True].mean())

    print("calculate last frost")
    last_frost = calculate_last_frost(df)
    last_frost = compensate_for_leap_years(last_frost)
    print("Last Frost Merra avg:", last_frost["day_of_year"][last_frost["is_merra"] == True].mean())
    print("Last Frost Station avg:", last_frost["day_of_year"][last_frost["is_merra"] != True].mean())

    print("calculate frost free days")
    first_frost_prep = first_frost.rename(columns={"day_of_year": "doy_first_frost"})
    last_frost_prep = last_frost.rename(columns={"day_of_year": "doy_last_frost"})
    frost_free = first_frost_prep.merge(last_frost_prep, how="outer", on=["year", "StnID"])
    frost_free["day_of_year"] = frost_free["doy_first_frost"] - frost_free["doy_last_frost"]
    frost_free["is_merra"] = frost_free["is_merra_x"] | frost_free["is_merra_y"]
    print("Frost Free Days Merra avg:", frost_free["day_of_year"][frost_free["is_merra"] == True].mean())
    print("Last Frost Station avg:", frost_free["day_of_year"][frost_free["is_merra"] != True].mean())


def generate_frost_report(filename="./data/merged_temp_data.csv", ra="era5"):
    lake_man_stns = [552, 515, 569, 556, 539, 574, 540]
    lake_wpg_stns = [565, 568, 564]
    lake_stns = lake_man_stns + lake_wpg_stns
    new_stns = ["566", "567", "568", "569", "570", "571", "572", "573", "574"]
    if ra == "era5":
        t_col = "era5_air_temp"
        is_ra = "is_era5"
    elif ra == "merra":
        t_col = "merra_air_temp"
        is_ra = "is_merra"
    elif ra == "nrcan":
        t_col = "nrcan_mint"
        is_ra = "is_nrcan"
    else:
        print("no reanalysis product chosen, exiting")
        exit(1)

    print("Using data from: ", filename)

    df = pd.read_csv(filename, dtype={"StnID": str, t_col: float, is_ra: bool, "air_temp_merged": float})

    df = df[~df["time"].isna()]
    df["time"] = pd.to_datetime(df["time"], utc=True)

    # remove all non-freezing days
    df = df[df["air_temp_merged"] < 0]
    df["season"] = df["time"].map(map_seasons)

    print("calculate first frost")
    first_frost = calculate_first_frost(df)
    first_frost = compensate_for_leap_years(first_frost)
    # first_frost = first_frost[~first_frost["StnID"].isin(lake_stns)]
    # first_frost = first_frost[~first_frost[is_ra]]
    # first_frost = pd.concat([first_frost[first_frost["StnID"].isin(lake_stns) ^ first_frost[is_ra]],
    #                          first_frost[~first_frost[is_ra]]])
    first_frost = first_frost[~first_frost["StnID"].isin(new_stns)]

    first_frost = first_frost[first_frost["day_of_year"] != 0]
    graph_frost_dates(first_frost, "First Frost With QC (NRCAN supplement)", ra=ra)

    first_frost_avg = calculate_frost_avg(first_frost)
    first_frost_avg = reformat_frost_dataframe(first_frost_avg)
    graph_frost_dates_on_map(first_frost_avg, "Avg First Frost With QC (NRCAN supplement)", "low-high")
    print("First frost average date:", first_frost_avg["date"].mean().strftime("%B %d"))
    first_frost_avg.to_csv("./data/first_frost.csv", index=False)

    print("calculate last frost")
    last_frost = calculate_last_frost(df)
    last_frost = compensate_for_leap_years(last_frost)
    # last_frost = last_frost[~last_frost["StnID"].isin(lake_stns)]
    # last_frost = last_frost[~last_frost[is_ra]]
    # last_frost = pd.concat([last_frost[last_frost["StnID"].isin(lake_stns) ^ last_frost[is_ra]],
    #                         last_frost[~last_frost[is_ra]]])
    last_frost = last_frost[~last_frost["StnID"].isin(new_stns)]

    last_frost = last_frost[last_frost["day_of_year"] != 0]
    last_frost = last_frost[last_frost["day_of_year"] > 92]
    graph_frost_dates(last_frost, "Last Frost With QC (NRCAN supplement)", ra=ra)

    last_frost_avg = calculate_frost_avg(last_frost)
    last_frost_avg = reformat_frost_dataframe(last_frost_avg)
    graph_frost_dates_on_map(last_frost_avg, "Avg Last Frost With QC (NRCAN supplement)", "high-low")
    print("Last frost average date:", last_frost_avg["date"].mean().strftime("%B %d"))
    last_frost_avg.to_csv("./data/last_frost.csv", index=False)

    print("calculate frost free days")
    first_frost_prep = first_frost.rename(columns={"day_of_year": "day_first_frost"})
    last_frost_prep = last_frost.rename(columns={"day_of_year": "day_last_frost"})
    frost_free = first_frost_prep.merge(last_frost_prep, how="outer", on=["year", "StnID"])
    frost_free["day_of_year"] = frost_free["day_first_frost"] - frost_free["day_last_frost"]
    frost_free[is_ra] = frost_free[is_ra + "_x"] | frost_free[is_ra + "_y"]

    frost_free["air_temp_merged"] = (frost_free["air_temp_merged_x"] + frost_free["air_temp_merged_y"]) / 2.0

    graph_frost_free(frost_free, "Frost Free Days With QC (NRCAN supplement)", ra=ra)
    frost_free_avg = calculate_frost_avg(frost_free)
    frost_free_avg = reformat_frost_dataframe(frost_free_avg)
    print("Frost Free days average:", frost_free_avg["day_of_year"].mean())
    graph_frost_dates_on_map(frost_free_avg, "Frost Free Days With QC (NRCAN supplement)", "low-high")
    frost_free_avg.to_csv("./data/frost_free.csv", index=False)


def main():
    generate_frost_report(filename="./data/nrcan_station_temp_data.csv", ra="nrcan")
    # merra_vs_station_stats()


if __name__ == "__main__":
    main()
