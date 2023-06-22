import pandas as pd
import numpy as np
import glob

from matplotlib import pyplot
from scipy.optimize import curve_fit


# define the true objective function
def objective(x, a, b, c, d, e, f, g):
    return (a * x) + (b * x ** 2) + (c * x ** 3) + (d * x ** 4) + (e * x ** 5) + (f * x ** 6) + g


def polynomial_best_fit():
    x = np.arange(-30, 366 + 30, 1)
    x_plot = np.arange(0, 366, 0.1)
    files = glob.glob("D:/data/processed-data/*.csv")

    for file in files:
        df = pd.read_csv(file)
        df["time"] = pd.to_datetime(df["time"])

        columns = df.columns
        date_index = df.set_index(df["time"])

        if "merra_err" in columns:
            merra_avg_year = date_index.groupby([date_index.index.month, date_index.index.day])[
                "merra_err"].mean()
            last_month = merra_avg_year.iloc[-30:]
            first_month = merra_avg_year.iloc[:30]
            merra_extra_year = pd.concat([last_month, merra_avg_year, first_month])

            popt, _ = curve_fit(objective, x, merra_extra_year)
            a, b, c, d, e, f, g = popt

            y_plot = objective(x_plot, a, b, c, d, e, f, g)
            pyplot.scatter(x, merra_extra_year, color='orange')
            pyplot.plot(x_plot, y_plot, '--', color='red')

        if "era5_err" in columns:
            era5_avg_year = date_index.groupby([date_index.index.month, date_index.index.day])[
                "era5_err"].mean()

            last_month = era5_avg_year.iloc[-30:]
            first_month = era5_avg_year.iloc[:30]
            era5_extra_year = pd.concat([last_month, era5_avg_year, first_month])

            popt, _ = curve_fit(objective, x, era5_extra_year)
            a, b, c, d, e, f, g = popt

            y_plot = objective(x_plot, a, b, c, d, e, f, g)
            pyplot.scatter(x, era5_extra_year, color='lightsteelblue')
            pyplot.plot(x_plot, y_plot, '--', color='blue')

        pyplot.title(file)
        root_path = "D:\\data\\graphs\\interesting\\curve_fitting\\"
        filename = root_path + file.replace("_output.csv", ".png").replace(
                    "D:/data/processed-data\\", "")
        pyplot.savefig(filename)
        pyplot.clf()


polynomial_best_fit()
