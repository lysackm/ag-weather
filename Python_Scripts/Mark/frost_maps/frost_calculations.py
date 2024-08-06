import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata


class FrostReport:
    def __init__(self, is_ra, t_col, legend):
        self.is_ra = is_ra
        self.t_col = t_col
        self.legend = legend

    def generate_frost_report(self, filename="./data/merged_temp_data.csv"):
        lake_man_stns = [552, 515, 569, 556, 539, 574, 540]
        lake_wpg_stns = [565, 568, 564]
        lake_stns = lake_man_stns + lake_wpg_stns
        new_stns = ["566", "567", "568", "569", "570", "571", "572", "573", "574"]

        print("Using data from: ", filename)

        df = pd.read_csv(filename, dtype={"StnID": str, self.t_col: float, self.is_ra: bool, "min_temp_merged": float})

        df = df[~df["date"].isna()]
        df["date"] = pd.to_datetime(df["date"])

        df["season"] = df["date"].map(map_seasons)
        df = df[~df["StnID"].isin(new_stns)]

        first_frost, first_frost_avg = self.first_frost_report(df)
        last_frost, last_frost_avg = self.last_frost_report(df)
        frost_free = self.frost_free_report(first_frost, last_frost)
        gdd = self.gdd_report(df, False)
        pday = self.pdays_report(df, False)
        chu = self.chu_report(df, False)

        # GDD (5, 10, 15)
        # PDays
        # CHU

    def first_frost_report(self, df, show_scatter=False):
        print("calculate first frost")
        # remove all non-freezing days
        df = df[df["min_temp_merged"] < 0]
        first_frost = calculate_first_frost(df)
        first_frost = compensate_for_leap_years(first_frost)

        first_frost = first_frost[first_frost["day_of_year"] != 0]
        if show_scatter:
            self.graph_frost_dates(first_frost,
                                   first_frost["day_of_year"],
                                   first_frost["min_temp_merged"],
                                   "First Frost With QC (NRCAN supplement)")

        title_base = "First Frost With QC (NRCAN supplement) "
        first_frost_merged = frost_report_calculation(first_frost, title_base)
        first_frost_merged.to_csv("./data/first_frost.csv", index=False)

        return first_frost, first_frost_merged

    def last_frost_report(self, df, show_scatter=False):
        print("calculate last frost")
        # remove all non-freezing days
        df = df[df["min_temp_merged"] < 0]
        last_frost = calculate_last_frost(df)
        last_frost = compensate_for_leap_years(last_frost)

        last_frost = last_frost[last_frost["day_of_year"] != 0]
        last_frost = last_frost[last_frost["day_of_year"] > 92]
        if show_scatter:
            self.graph_frost_dates(last_frost,
                                   last_frost["day_of_year"],
                                   last_frost["min_temp_merged"],
                                   "Last Frost With QC (NRCAN supplement)")

        title_base = "Last Frost With QC (NRCAN supplement) "
        last_frost_merged = frost_report_calculation(last_frost, title_base, scale="high-low", quans=["avg", 0.75, 0.9])
        last_frost_merged.to_csv("./data/last_frost.csv", index=False)

        return last_frost, last_frost_merged

    def frost_free_report(self, first_frost, last_frost, show_scatter=False):
        print("calculate frost free days")
        first_frost_prep = first_frost.rename(columns={"day_of_year": "day_first_frost"})
        last_frost_prep = last_frost.rename(columns={"day_of_year": "day_last_frost"})
        frost_free = first_frost_prep.merge(last_frost_prep, how="outer", on=["year", "StnID"])
        frost_free["frost_free"] = frost_free["day_first_frost"] - frost_free["day_last_frost"]
        frost_free[self.is_ra] = frost_free[self.is_ra + "_x"] | frost_free[self.is_ra + "_y"]

        frost_free["min_temp_merged"] = (frost_free["min_temp_merged_x"] + frost_free["min_temp_merged_y"]) / 2.0

        if show_scatter:
            self.graph_frost_dates(frost_free,
                                   frost_free["frost_free"],
                                   frost_free["min_temp_merged"],
                                   "Frost Free Days With QC (NRCAN supplement)")

        title_base = "Frost Free With QC (NRCAN supplement) "
        frost_free_merged = frost_report_calculation(frost_free, title_base, col="frost_free")
        frost_free_merged.to_csv("./data/frost_free.csv", index=False)
        return frost_free, frost_free_merged

    def gdd_report(self, df, show_scatter=False):
        print("calculate Growing Degree Days (GDD)")
        gdd = calculate_gdd(df)
        gdd = gdd.reset_index()
        gdd["years"] = gdd["date"]
        gdd = gdd.set_index(["StnID", "date"])

        if show_scatter:
            self.graph_frost_dates(gdd, gdd["gdd"], gdd["years"], "GDD With QC (NRCAN supplement)")

        title_base = "GDD With QC (NRCAN supplement) "
        gdd_merged = frost_report_calculation(gdd, title_base, scale="low-high", col="gdd")
        gdd_merged.to_csv("./data/gdd.csv", index=False)
        return gdd, gdd_merged

    def pdays_report(self, df, show_scatter=False):
        print("calculate Potato Growing Days (Pdays)")
        pday = calculate_pdays(df)
        pday = pday.reset_index()
        pday["years"] = pday["date"]
        pday = pday.set_index(["StnID", "date"])

        if show_scatter:
            self.graph_frost_dates(pday, pday["pday"], pday["years"], "Potato Days With QC (NRCAN supplement)")

        title_base = "Pdays With QC (NRCAN supplement) "
        pday_merged = frost_report_calculation(pday, title_base, scale="low-high", col="pday")
        pday_merged.to_csv("./data/pday.csv", index=False)
        return pday, pday_merged

    def chu_report(self, df, show_scatter=False):
        print("calculate Corn Heat Units (CHU)")
        chu = calculate_chu(df)
        chu = chu.reset_index()
        chu["years"] = chu["date"]
        chu = chu.set_index(["StnID", "date"])

        if show_scatter:
            self.graph_frost_dates(chu, chu["chu"], chu["years"], "Corn Heat Units With QC (NRCAN supplement)")

        title_base = "CHU With QC (NRCAN supplement) "
        chu_merged = frost_report_calculation(chu, title_base, scale="low-high", col="chu")
        chu_merged.to_csv("./data/chu.csv", index=False)
        return chu, chu_merged

    def graph_frost_dates(self, df, col_a, col_b, title=""):
        grouped = df.groupby("StnID")
        grouped_a = col_a.groupby("StnID")
        grouped_b = col_b.groupby("StnID")
        fig, ax = plt.subplots()

        for name, group in grouped:
            group_a = grouped_a.get_group(name)
            group_b = grouped_b.get_group(name)
            colour_col = group[self.is_ra].apply(lambda x: "blue" if x else "red")
            ax.scatter(group_a, group_b, alpha=0.3, c=colour_col)

        plt.xlabel("date")
        plt.ylabel("temperature celsius")
        plt.legend([self.legend, "station data"])
        plt.title(title)
        leg = ax.get_legend()
        leg.legend_handles[0].set_color('blue')
        leg.legend_handles[1].set_color('red')
        plt.show()
        plt.clf()


def graph_frost_dates_on_map(df, title="Interpolated Frost Dates", scale="low-high", col="day_of_year"):
    stations_x = df["LongDD"]
    stations_y = df["LatDD"]
    station_values = df[col]
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
    else:
        cmap = "gist_rainbow"

    ct = m.contourf(grid_x, grid_y, grid_values, levels=20, cmap=cmap, latlon=True)
    m.scatter(stations_x, stations_y, c='red', marker='o', label='Stations', latlon=True)
    m.colorbar(ct)

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    plt.legend()
    # plt.show()
    plt.savefig("../../../../frost_maps/graphs/nrcan/" + title.replace(" ", "_") + ".png")
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
    df["day_of_year"] = df["date"].dt.dayofyear
    return df


def calculate_frost_avg(df):
    return df.groupby("StnID").mean(numeric_only=True)


def calculate_frost_quantile(df, quantile):
    return df.groupby("StnID").quantile(quantile, numeric_only=True)


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


def calculate_gdd(df, degree=5):
    # May 1st to October 31st
    df_gdd = df.copy()
    df_gdd = df_gdd[(df_gdd["date"].dt.month >= 5) & (df_gdd["date"].dt.month < 11)]

    df_gdd["gdd"] = ((df_gdd["min_temp_merged"] + df_gdd["max_temp_merged"]) / 2.0) - degree
    df_gdd["gdd"] = df_gdd["gdd"].mask(df_gdd["gdd"] < degree, 0)
    df_gdd = df_gdd.groupby([df_gdd["date"].dt.year, "StnID"]).sum(numeric_only=True)
    return df_gdd


def calculate_pdays(df):
    df = df.copy()
    # June 1st to October 31st
    df = df[(df["date"].dt.month >= 6) & (df["date"].dt.month < 11)]

    df["T1"] = df["min_temp_merged"].apply(p_calc)
    df["T2"] = (((2.0 * df["min_temp_merged"]) + df["max_temp_merged"]) / 3.0).apply(p_calc)
    df["T3"] = ((df["min_temp_merged"] + (2 * df["max_temp_merged"])) / 3.0).apply(p_calc)
    df["T4"] = df["max_temp_merged"].apply(p_calc)

    # print(df["T1"], df["T2"], df["T3"], df["T4"], sep="\n")

    df["pday"] = (1.0 / 24.0) * (5.0 * df["T1"] + 8.0 * df["T2"] + 8.0 * df["T3"] + 3 * df["T4"])
    df = df.groupby([df["date"].dt.year, "StnID"]).sum(numeric_only=True)
    return df


def p_calc(t):
    k = 10

    if t < 7:
        return 0
    elif 7 <= t < 21:
        return k * (1 - (((t - 21) ** 2) / ((21 - 7) ** 2)))
    elif 21 <= t < 30:
        return k * (1 - (((t - 21) ** 2) / ((30 - 21) ** 2)))
    elif t >= 30:
        return 0
    else:
        print("Unexpected temperature value while calculating pdays, exiting. Unexpected value: ", t)
        exit(1)


def calculate_chu(df):
    # May 1st to October 31st
    df = df.copy()
    df = df[(df["date"].dt.month >= 5) & (df["date"].dt.month < 11)]

    df["chu"] = (1.8 * (df["min_temp_merged"] - 4.4) + 3.33 * (df["max_temp_merged"] - 10.0) - 0.084 * (df["max_temp_merged"] - 10) ** 2) / 2.0

    df = df.groupby([df["date"].dt.year, "StnID"]).sum(numeric_only=True)
    return df


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


def reformat_frost_dataframe(df, col="day_of_year"):
    df = df.reset_index()

    station_metadata_df = pd.read_csv("../../../Cleaning-Data/cleaning-data/util/station-metadata.csv",
                                      dtype={"StnID": str})
    df = df.merge(station_metadata_df, how="left", on="StnID")

    # already had a LatDD and LongDD columns
    if "LatDD_x" in df.columns:
        df["LatDD"] = df["LatDD_x"].where(df["LatDD_x"].notna(), df["LatDD_y"])
        df["LongDD"] = df["LongDD_x"].where(df["LongDD_x"].notna(), df["LongDD_y"])

        df = df[df["LatDD"].notna() & df["LongDD"].notna()]

    if col == "day_of_year":
        df["date"] = pd.to_datetime(2023 * 1000 + df[col].round(), format='%Y%j')
        return df[["StnID", "StationName", "LatDD", "LongDD", "date", "day_of_year"]]
    else:
        return df[["StnID", "StationName", "LatDD", "LongDD", col]]


def merra_vs_station_stats():
    df = pd.read_csv("./data/merged_temp_data.csv",
                     dtype={"StnID": str, "merra_air_temp": float, "is_merra": bool, "min_temp_merged": float},
                     parse_dates=["date"])

    # remove all non-freezing days
    df = df[df["min_temp_merged"] < 0]
    df["season"] = df["date"].map(map_seasons)

    print("calculate first frost")
    first_frost = calculate_first_frost(df)
    first_frost = compensate_for_leap_years(first_frost)
    print("First Frost Merra avg:", first_frost["day_of_year"][first_frost["is_merra"] is True].mean())
    print("First Frost Station avg:", first_frost["day_of_year"][first_frost["is_merra"] is not True].mean())

    print("calculate last frost")
    last_frost = calculate_last_frost(df)
    last_frost = compensate_for_leap_years(last_frost)
    print("Last Frost Merra avg:", last_frost["day_of_year"][last_frost["is_merra"] is True].mean())
    print("Last Frost Station avg:", last_frost["day_of_year"][last_frost["is_merra"] is not True].mean())

    print("calculate frost free days")
    first_frost_prep = first_frost.rename(columns={"day_of_year": "doy_first_frost"})
    last_frost_prep = last_frost.rename(columns={"day_of_year": "doy_last_frost"})
    frost_free = first_frost_prep.merge(last_frost_prep, how="outer", on=["year", "StnID"])
    frost_free["day_of_year"] = frost_free["doy_first_frost"] - frost_free["doy_last_frost"]
    frost_free["is_merra"] = frost_free["is_merra_x"] | frost_free["is_merra_y"]
    print("Frost Free Days Merra avg:", frost_free["day_of_year"][frost_free["is_merra"] is True].mean())
    print("Last Frost Station avg:", frost_free["day_of_year"][frost_free["is_merra"] is not True].mean())


def graph_frost_bootstrap(first_frost, quan, title, scale="low-high", col="day_of_year"):
    if quan == "avg":
        first_frost_avg = calculate_frost_avg(first_frost)
    else:
        first_frost_avg = calculate_frost_quantile(first_frost, quan)
    first_frost_avg = reformat_frost_dataframe(first_frost_avg, col)
    graph_frost_dates_on_map(first_frost_avg, title, scale, col)
    return first_frost_avg


def frost_report_calculation(frost_data, title_base, scale="low-high", quans=None, col="day_of_year"):
    if quans is None:
        quans = ["avg", 0.25, 0.10]
    frost_avg = graph_frost_bootstrap(frost_data, quan=quans[0], title=title_base + "Average", scale=scale, col=col)
    frost_avg = frost_avg.rename(columns={col: "avg", "date": "avg_date"})
    frost_25 = graph_frost_bootstrap(frost_data, quan=quans[1], title=title_base + "25%", scale=scale, col=col)
    frost_25 = frost_25.rename(columns={col: "25", "date": "25_date"})
    frost_10 = graph_frost_bootstrap(frost_data, quan=quans[2], title=title_base + "10%", scale=scale, col=col)
    frost_10 = frost_10.rename(columns={col: "10", "date": "10_date"})

    frost_merged = frost_avg.merge(frost_25, how="outer",
                                   on=["StnID", "StationName", "LatDD", "LongDD"])
    frost_merged = frost_merged.merge(frost_10, how="outer",
                                      on=["StnID", "StationName", "LatDD", "LongDD"])
    return frost_merged


def main():
    frost_report = FrostReport("is_nrcan", "min_temp", "NRCAN")
    frost_report.generate_frost_report(filename="./data/nrcan_station_temp_data.csv")
    # merra_vs_station_stats()


if __name__ == "__main__":
    main()
