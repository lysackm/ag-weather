import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def linear_comparison(i, j, col1, col2, ax, title, is_precip=False):
    ax[i, j].scatter(col1, col2, s=0.1)
    if not is_precip:
        ax[i, j].axline((0, 0), slope=1)
        ax[i, j].axline((0, 2), slope=1)
        ax[i, j].axline((0, -2), slope=1)
    else:
        ax[i, j].axline((0, 0), slope=1)
        ax[i, j].axline((0, 1), slope=1)
        ax[i, j].axline((1, 0), slope=1)
        ax[i, j].set_xlim(left=0)
        ax[i, j].set_ylim(bottom=0)
    ax[i, j].set_title(title)
    if not is_precip:
        ax[i, j].set_ylabel("degree celsius")
        ax[i, j].set_xlabel("degree celsius")


def yearly_scatter(i, j, date_col, col1, col2, ax, title, label_1="Old Data", label_2="Introduced Data"):
    ax[i, j].scatter(date_col, col1, c="Blue", label=label_1, s=0.1)
    ax[i, j].scatter(date_col, col2, c="Orange", label=label_2, s=0.1)
    ax[i, j].legend(loc="upper left")
    ax[i, j].set_title(title)
    ax[i, j].set_xticks(["2000-01-01", "2000-03-01", "2000-05-01", "2000-07-01", "2000-09-01", "2000-11-01"])


def display_linear_comparison(df, columns_to_compare):
    num_cols = math.ceil(len(columns_to_compare) / 2.0)
    if num_cols < 2:
        num_cols = 2
    fig, ax = plt.subplots(2, num_cols)

    i = 0
    j = 0
    for counter in range(1, len(columns_to_compare) + 1):
        col_name = columns_to_compare[counter - 1]
        is_precip = col_name == "PPT"
        linear_comparison(i, j, df[col_name + "_x"], df[col_name + "_y"], ax, "Comparing " + col_name,
                          is_precip=is_precip)

        i = (i + 1) % 2
        if counter % 2 == 0 and counter != 0:
            j += 1

    plt.show()


def display_yearly_scatter(df, columns_to_compare, label_1="Old Data", label_2="Introduced Data"):
    num_cols = math.ceil(len(columns_to_compare) / 2.0)
    if num_cols < 2:
        num_cols = 2
    fig, ax = plt.subplots(2, num_cols)

    i = 0
    j = 0
    for counter in range(1, len(columns_to_compare) + 1):
        col_name = columns_to_compare[counter - 1]
        yearly_scatter(i, j, df["DateDT_x"], df[col_name + "_x"], df[col_name + "_y"], ax, "Comparing " + col_name, label_1, label_2)

        i = (i + 1) % 2
        if counter % 2 == 0 and counter != 0:
            j += 1

    plt.show()


def get_cmap(n, name='hsv'):
    return plt.get_cmap(name, n)


# useful for when looking at precipitation
def compare_monthly_totals(df, col):
    cmap = get_cmap(df["StnID"].nunique())
    df_copy = df.copy()
    df_copy = df_copy.drop(columns=["DateDT_x", "DateDT_y"])
    df_copy = df_copy[[col + "_x", col + "_y"]].groupby(by=[df_copy["NormMM"], df_copy["NormDD"], df_copy["StnID"]]).mean()
    df_copy = df_copy.reset_index()
    df_copy = df_copy.groupby(by=[df_copy["NormMM"],
                                  df_copy["StnID"]]).sum()
    x_ticks = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, ax = plt.subplots(2)
    i = 0
    monthly_stats = []
    for label, stn_df in df_copy.groupby("StnID"):
        if list(stn_df.shape)[0] == 12:
            colour = cmap(i)
            i += 1
            # graph the two columns next to each other
            ax[0].plot(range(12), stn_df[col + "_x"], c=colour, ls="-")
            ax[0].plot(range(12), stn_df[col + "_y"], c=colour, ls=":")

            # graph the bias
            ax[1].plot(range(12), stn_df[col + "_x"] - stn_df[col + "_y"], c=colour)
            monthly_stats.append(stn_df[col + "_x"] - stn_df[col + "_y"])

    ax[0].set_xticks(range(len(x_ticks)))
    ax[1].set_xticks(range(len(x_ticks)))
    ax[0].set_xticklabels(x_ticks)
    ax[1].set_xticklabels(x_ticks)

    print("Monthly total statistics:")
    print("Month: Mean error, Standard deviation")
    monthly_mean_stats = np.mean(monthly_stats, axis=0)
    monthly_std_dev_stats = np.std(monthly_stats, axis=0)
    for month, mean, std_dev in zip(x_ticks, monthly_mean_stats.tolist(), monthly_std_dev_stats.tolist()):
        print(month + ":" + str(round(mean, 2)) + "," + str(round(std_dev, 2)))

    ax[1].plot(range(12), monthly_mean_stats, c="black", linewidth=5)
    plt.show()


def show_singular_station(df, column, stn_id, show_plot=False):
    source_colour_map = {"eccc": "red", "nrcan": "green", "era5": "blue", "mbag": "black"}

    df = df[df["StnID"] == stn_id]
    source_column_name = column + "_source"
    df["colour"] = df[source_column_name].apply(lambda x: source_colour_map[x])

    plt.scatter(df["DateDT"], df[column], color=df["colour"], s=0.3)
    plt.savefig("D:/data/graphs/climate_normal_stn_graphs/" + column + "_" + str(stn_id) + ".png")
    if show_plot:
        plt.show()
    plt.clf()


def show_all_stations_individually(column):
    df = pd.read_csv("D:/PycharmProjects/data_management/data/merged_dataset_2024_normal.csv")
    df["DateDT"] = pd.to_datetime(df["DateDT"])

    plt.figure(figsize=(8, 6), dpi=260)

    station_df = pd.read_csv("./metadata/station_metadata.csv")
    stn_ids = station_df["StnID"].tolist()

    for stn_id in stn_ids:
        show_singular_station(df.copy(), column, stn_id)


def save_normal_summary(df_file=""):
    if df_file == "":
        df = pd.read_csv("./data/climate_normal/2020_MBAg_normal.csv")
    else:
        df = pd.read_csv(df_file)
    df = df.drop(columns=["DateDT", "NormLocation", "NormYY", "NormMM", "NormDD", "JD"])
    df_summary = df.groupby(by=[df["StnID"], df["Location"]]).sum()
    rounded_cols = ["Tmax", "Tmin", "Tavg", "PPT", "CHU", "GDD", "PDay"]
    df_summary[rounded_cols] = df_summary[rounded_cols].round(2)
    df_summary.to_csv("./data/climate_normal/summaries/2020_MBAg_normal_summary.csv")


def run_normal_graph_suite(df_1, df_2, columns_to_compare):
    df = df_1.merge(df_2, how="inner", on=["StnID", "NormMM", "NormDD"])
    print(df)
    display_yearly_scatter(df, columns_to_compare)
    display_linear_comparison(df, columns_to_compare)
    if "PPT" in columns_to_compare:
        compare_monthly_totals(df, "PPT")


def normal_comparison():
    df_1 = pd.read_csv("./data/climate_normal/historical_2000_normal.csv")
    df_2 = pd.read_csv("./data/climate_normal/nrcan_temperature.csv")
    df_3 = pd.read_csv("./data/climate_normal/era5_temperature.csv")
    df_4 = pd.read_csv("./data/climate_normal/2020_MBAg_normal.csv")
    df_5 = pd.read_csv("./data/climate_normal/2020_MBAg_normal_non_climatological_days.csv")

    columns = ["Tmax", "Tmin", "PPT"]
    # run_normal_graph_suite(df_1, df_2, columns)
    # run_normal_graph_suite(df_1, df_3, ["Tavg"])
    run_normal_graph_suite(df_1, df_4, columns + ["Tavg"])


def daily_comparison():
    df_1 = pd.read_csv("./data/standardized_daily/mbag_stations.csv")
    df_2 = pd.read_csv("./data/standardized_daily/nrcan.csv")
    # df_2 = pd.read_csv("./data/standardized_daily/era5_temperature.csv")

    # group by day, compare values in column list
    df = df_1.merge(df_2, how="inner", on=["StnID", "NormYY", "NormMM", "NormDD"])
    columns = ["Tmax", "Tmin", "PPT"]
    display_linear_comparison(df, columns)
    display_yearly_scatter(df, columns, "Mbag", "NRCan")
    # DBO_DT_stns
    if "PPT" in columns:
        compare_monthly_totals(df, "PPT")


def main():
    # normal_comparison()
    # daily_comparison()
    # save_normal_summary()

    show_all_stations_individually("PPT")


if __name__ == "__main__":
    main()
