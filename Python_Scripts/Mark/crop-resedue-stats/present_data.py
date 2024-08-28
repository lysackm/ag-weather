import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr


def calculate_error_wd(row):
    error = row['wd'] - row['2min_wd_stn']
    error = (error + 180) % 360 - 180
    return error


def calculate_error_wd_pbl(row):
    error = row['wd_pbl'] - row['wd_pbl_cf']
    error = (error + 180) % 360 - 180
    return error


def calculate_statistics():
    df = pd.read_csv("data/forecast_match/forecast_match.csv")
    df = df.dropna(how="any")

    # df = df[df["ws"] > 5]
    df = df[df["avg_ws_stn"] > 2]

    df["ws_err"] = df["ws"] - df["avg_ws_stn"]
    df["wd_err"] = df.apply(calculate_error_wd, axis=1)
    df["ws_cf_err"] = df["ws"] - df["ws_cf"]
    df["ws_pbl_err"] = df["ws_pbl"] - df["ws_pbl_cf"]
    df["wd_pbl_err"] = df.apply(calculate_error_wd_pbl, axis=1)
    df["hgt_pbl_err"] = df["hgt_pbl"] - df["hgt_pbl_cf"]
    df["vrate_err"] = df["vrate"] - df["vrate_cf"]

    print("station wind speed (AvgWS): ", df["ws_err"].mean())
    corr, _ = pearsonr(df["ws"], df["avg_ws_stn"])
    print('Pearsons correlation: %.3f' % corr)

    print("NAM wind speed comparison: ", df["ws_cf_err"].mean())
    corr, _ = pearsonr(df["ws"], df["ws_cf"])
    print('Pearsons correlation: %.3f' % corr)

    print("station wind direction (AvgWD): ", df["wd_err"].mean())

    print("NAM wind speed mixing layer: ", df["ws_pbl_err"].mean())
    print("NAM wind direction mixing layer: ", df["wd_pbl_err"].mean())
    print("mixing layer height: ", df["hgt_pbl_err"].mean())
    print("volume rate: ", df["vrate_err"].mean(), "\n\n")


def graph_mbe_statistics():
    ws = []
    wd = []
    ws_cf = []
    ws_pbl_cf = []
    wd_pbl_cf = []
    hgt_pbl_cf = []
    vrate_cf = []

    df_forecast = pd.read_csv("data/forecast_match/forecast_match.csv")
    df_forecast = df_forecast.dropna(how="any")

    for max_offset in range(0, 52, 6):
        df = df_forecast[df_forecast["offset"].between(max_offset, max_offset + 6, inclusive="both")]

        ws.append((df["ws"] - df["avg_ws_stn"]).mean())
        wd.append(df.apply(calculate_error_wd, axis=1).mean())
        ws_cf.append((df["ws"] - df["ws_cf"]).mean())
        ws_pbl_cf.append((df["ws_pbl"] - df["ws_pbl_cf"]).mean())
        wd_pbl_cf.append(df.apply(calculate_error_wd_pbl, axis=1).mean())
        hgt_pbl_cf.append((df["hgt_pbl"] - df["hgt_pbl_cf"]).mean())
        vrate_cf.append((df["vrate"] - df["vrate_cf"]).mean())

    x = list(range(0, 52, 6))

    y = [ws, wd, ws_cf, ws_pbl_cf, wd_pbl_cf, hgt_pbl_cf, vrate_cf]
    y_names = ["Wind Speed (m/s) NAM - Station MBE",
               "Wind Direction (º) NAM - Station MBE",
               "Wind Speed (m/s) NAM - NAM MBE",
               "Wind Speed Mixing Layer (m/s) NAM - NAM MBE",
               "Wind Direction Mixing Layer (º) NAM - NAM MBE",
               "Mixing Layer Height (m) NAM - NAM MBE",
               "Volume Rate (m^2/s) NAM - NAM MBE"]
    file_names = ["ws_stn",
                  "wd_stn",
                  "ws_nam",
                  "ws_pbl_nam",
                  "wd_pbl_nam",
                  "hgt_pbl_nam",
                  "vrate_nam"]

    for y_axis, y_name, filename in zip(y, y_names, file_names):
        plt.plot(x, y_axis)
        plt.title(y_name)
        plt.xlabel("Time of Day (CST)")
        plt.xticks(x, list(map(lambda i: (i + 1) % 24, x)))
        plt.savefig("graphs/mbe/" + filename + "_mbe.png")
        # plt.show()
        plt.clf()


def graph_rmse_statistics():
    ws = []
    wd = []
    ws_cf = []
    ws_pbl_cf = []
    wd_pbl_cf = []
    hgt_pbl_cf = []
    vrate_cf = []

    df_forecast = pd.read_csv("data/forecast_match/forecast_match.csv")
    df_forecast = df_forecast.dropna(how="any")

    for max_offset in range(0, 52, 6):
        df = df_forecast[df_forecast["offset"].between(max_offset, max_offset + 5, inclusive="both")]

        ws.append(np.sqrt(((df["ws"] - df["avg_ws_stn"]) ** 2).mean()))
        wd.append(np.sqrt((df.apply(calculate_error_wd, axis=1) ** 2).mean()))
        ws_cf.append(np.sqrt(((df["ws"] - df["ws_cf"]) ** 2).mean()))
        ws_pbl_cf.append(np.sqrt(((df["ws_pbl"] - df["ws_pbl_cf"]) ** 2).mean()))
        wd_pbl_cf.append(np.sqrt((df.apply(calculate_error_wd_pbl, axis=1) ** 2).mean()))
        hgt_pbl_cf.append(np.sqrt(((df["hgt_pbl"] - df["hgt_pbl_cf"]) ** 2).mean()))
        vrate_cf.append(np.sqrt(((df["vrate"] - df["vrate_cf"]) ** 2).mean()))

    x = list(range(0, 52, 6))

    y = [ws, wd, ws_cf, ws_pbl_cf, wd_pbl_cf, hgt_pbl_cf, vrate_cf]
    y_names = ["Wind Speed (m/s) NAM - Station RMSE",
               "Wind Direction (º) NAM - Station RMSE",
               "Wind Speed (m/s) NAM - NAM RMSE",
               "Wind Speed Mixing Layer (m/s) NAM - NAM RMSE",
               "Wind Direction Mixing Layer (º) NAM - NAM RMSE",
               "Mixing Layer Height (m) NAM - NAM RMSE",
               "Volume Rate (m^2/s) NAM - NAM RMSE"]
    file_names = ["ws_stn",
                  "wd_stn",
                  "ws_nam",
                  "ws_pbl_nam",
                  "wd_pbl_nam",
                  "hgt_pbl_nam",
                  "vrate_nam"]

    for y_axis, y_name, filename in zip(y, y_names, file_names):
        print(y_axis, y_name)
        plt.plot(x, y_axis)
        plt.title(y_name)
        plt.xlabel("Time of Day (CST)")
        plt.xticks(x, list(map(lambda i: (i + 1) % 24, x)))
        # plt.show()
        plt.savefig("graphs/rmse/" + filename + "_rmse.png")
        plt.clf()


def graph_variable_statistics():
    ws = []
    ws_cf = []
    ws_pbl_cf = []
    hgt_pbl_cf = []
    vrate_cf = []

    df_forecast = pd.read_csv("data/forecast_match/forecast_match.csv")
    df_forecast = df_forecast.dropna(how="any")

    for max_offset in range(0, 52, 6):
        df = df_forecast[df_forecast["offset"].between(max_offset, max_offset + 5, inclusive="both")]

        # ws.append(((df["ws"] - df["avg_ws_stn"])/df["ws"]).mean())
        # ws_cf.append(((df["ws"] - df["ws_cf"])/df["ws"]).mean())
        # ws_pbl_cf.append(((df["ws_pbl"] - df["ws_pbl_cf"])/df["ws_pbl"]).mean())
        # hgt_pbl_cf.append(((df["hgt_pbl"] - df["hgt_pbl_cf"])/df["hgt_pbl"]).mean())
        # vrate_cf.append(((df["vrate"] - df["vrate_cf"])/df["vrate"]).mean())

        ws.append(df["avg_ws_stn"].mean())
        ws_cf.append(df["ws_cf"].mean())
        ws_pbl_cf.append(df["ws_pbl_cf"].mean())
        hgt_pbl_cf.append(df["hgt_pbl"].mean())
        vrate_cf.append(df["vrate"].mean())

    x = list(range(0, 52, 6))

    y = [ws, ws_cf, ws_pbl_cf, hgt_pbl_cf, vrate_cf]
    y_names = ["Station Average Wind Speed (m/s)",
               "NAM Average Wind Speed (m/s)",
               "NAM Average Wind Speed Mixing Layer (m/s)",
               "NAM Average Mixing Layer Height (m)",
               "NAM Average Volume Rate (m^2/s)"]
    file_names = [
        "stn_ws",
        "nam_ws",
        "nam_pbl_ws",
        "nam_pbl_hgt",
        "nam_vrate"]

    for y_axis, y_name, filename in zip(y, y_names, file_names):
        plt.plot(y, y_axis)
        plt.title(y_name)
        plt.xlabel("Time of Day (CST)")
        plt.xticks(x, list(map(lambda i: (i + 1) % 24, x)))
        # plt.show()
        plt.savefig("graphs/variable/" + filename + "_relative_error.png")
        plt.clf()


def scatter_plot():
    df_forecast = pd.read_csv("data/forecast_match/forecast_match.csv")
    df_forecast = df_forecast.dropna(how="any")

    titles = ["Wind Speed (m/s) NAM - Station Comparison",
              "Wind Direction (º) NAM - Station Comparison",
              "Wind Speed (m/s) NAM - NAM Comparison",
              "Wind Speed Mixing Layer (m/s) NAM - NAM Comparison",
              "Wind Direction Mixing Layer (º) NAM - NAM Comparison",
              "Mixing Layer Height (m) NAM - NAM Comparison",
              "Volume Rate (m^2/s) NAM - NAM Comparison"]

    predicted_names = ["ws", "wd", "ws", "ws_pbl", "wd_pbl", "hgt_pbl", "vrate"]
    measured_names = ["avg_ws_stn", "avg_wd_stn", "ws_cf", "ws_pbl_cf", "wd_pbl_cf", "hgt_pbl_cf", "vrate_cf"]

    for title, predicted, measured in zip(titles, predicted_names, measured_names):
        plt.title(title)
        df_sample = df_forecast.sample(50000)
        plt.scatter(df_sample[predicted], df_sample[measured], alpha=1.0 / 255.0)
        plt.xlabel("Forecasted Data")
        plt.ylabel("'Measured' Data")
        # plt.show()
        plt.savefig("graphs/scatter/" + predicted + measured + ".png")
        plt.clf()


# graph_mbe_statistics()
graph_rmse_statistics()
# scatter_plot()
# calculate_statistics()
# graph_variable_statistics()
