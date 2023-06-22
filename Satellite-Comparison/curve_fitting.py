import pandas as pd
import numpy as np
import glob

from matplotlib import pyplot
from scipy.optimize import curve_fit


# define the true objective function
def objective(x, a, b, c, d, e, f, g):
    return (a * x) + (b * x ** 2) + (c * x ** 3) + (d * x ** 4) + (e * x ** 5) + f * np.sin(g + x)


def polynomial_best_fit():
    # use this line for monthly averages
    # x = np.arange(-30, 8839 + 30, 1)
    x_plot = np.arange(0, 8839, 0.1)
    files = glob.glob("D:/data/processed-data/*.csv")

    for file in files:
        df = pd.read_csv(file)
        df["time"] = pd.to_datetime(df["time"])

        columns = df.columns
        date_index = df.set_index(df["time"])

        if "merra_err" in columns:
            merra_avg_year = date_index.groupby([date_index.index.month, date_index.index.day, date_index.index.hour])[
                "merra_err"].mean()
            last_month = merra_avg_year.iloc[-300:]
            first_month = merra_avg_year.iloc[:300]
            merra_extra_year = pd.concat([last_month, merra_avg_year, first_month])

            # only needed for hourly with NaN values
            x = np.arange(0, len(merra_extra_year), 1)

            popt, _ = curve_fit(objective, x, merra_extra_year)
            a, b, c, d, e, f, g = popt
            print(popt)

            y_plot = objective(x_plot, a, b, c, d, e, f, g)
            pyplot.scatter(x, merra_extra_year, color='orange')
            pyplot.plot(x_plot, y_plot, '--', color='red')

        if "era5_err" in columns:
            era5_avg_year = date_index.groupby([date_index.index.month, date_index.index.day, date_index.index.hour])[
                "era5_err"].mean()

            last_month = era5_avg_year.iloc[-300:]
            first_month = era5_avg_year.iloc[:300]
            era5_extra_year = pd.concat([last_month, era5_avg_year, first_month])
            era5_extra_year.dropna(inplace=True)

            # only needed for hourly with NaN values
            x = np.arange(0, len(era5_extra_year), 1)

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
