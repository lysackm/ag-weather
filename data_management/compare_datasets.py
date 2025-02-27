import matplotlib.pyplot as plt
import pandas as pd
import math
from scipy.stats import ttest_ind
from sklearn.metrics import root_mean_squared_error


def t_test(series_1, series_2):
    res = ttest_ind(series_1, series_2)

    p = res.pvalue
    t = res.statistic

    print("T-test statistic: ", t)
    print("P value", p)
    return p, t


# series 1 is presumed to be the true value
# series 2 is presumed to be the predicted value
def rmse(series_1, series_2):
    rmse = root_mean_squared_error(series_1, series_2)

    print("RMSE: ", rmse)
    return rmse


#
def graph_compared_values(series_1, series_2, x_axis, label_1="Series 1", label_2="Series 2"):
    ax1 = plt.subplot(221)
    ax1.plot(x_axis, series_1, color="Blue", label=label_1)
    ax1.plot(x_axis, series_2, color="Red", label=label_2)
    ax1.legend()

    ax2 = plt.subplot(222)
    ax2.plot(x_axis, series_1.cumsum(), color="Blue", label=label_1)
    ax2.plot(x_axis, series_2.cumsum(), color="Red", label=label_2)
    ax2.set_title("Cumulative Sum")
    ax2.legend()

    ax3 = plt.subplot(223)
    ax3.plot(x_axis, series_1 - series_2)
    ax3.set_title("Difference between series")

    ax4 = plt.subplot(224)
    ax4.scatter(series_1, series_2)
    ax4.set_ylabel(label_1)
    ax4.set_xlabel(label_2)
    ax4.set_title("Plotting against each other")

    plt.show()


# labels are packed into a tuple
def compare_stn_variable(df_1, df_2, col_1, time_col_1, col_2, time_col_2, stn_id=None, labels=None):
    if stn_id is not None:
        df_1 = df_1[df_1["StnID"] == stn_id]
    df_1 = df_1[[col_1, time_col_1]].dropna()
    df_1[[col_1 + "_1", time_col_1]] = df_1[[col_1, time_col_1]]

    if stn_id is not None:
        df_2 = df_2[df_2["StnID"] == stn_id]
    df_2 = df_2[[col_2, time_col_2]].dropna()
    df_2[[col_2 + "_2", time_col_2]] = df_2[[col_2, time_col_2]]

    # merge on overlapping dates
    df_merged = df_1.merge(df_2, left_on=[time_col_1], right_on=[time_col_2], how="inner")

    series_1 = df_merged[col_1 + "_1"]
    series_2 = df_merged[col_2 + "_2"]
    time_index = df_merged[time_col_1]

    t_test(series_1, series_2)
    rmse(series_1, series_2)

    if labels is not None:
        graph_compared_values(series_1, series_2, time_index, labels[0], labels[1])
    else:
        graph_compared_values(series_1, series_2, time_index)


def main():
    df_1 = pd.read_csv("D:/data/misc/st_labre/saintlabre24.txt")
    df_2 = pd.read_csv("D:/data/misc/st_labre/5022575.csv")

    col_1 = "Pluvio_Rain"
    time_col_1 = "TMSTAMP"

    col_2 = "Total Precip (mm)"
    time_col_2 = "Date/Time"

    df_1[time_col_1] = pd.to_datetime(df_1[time_col_1])
    df_2[time_col_2] = pd.to_datetime(df_2[time_col_2])

    compare_stn_variable(df_1, df_2, col_1, time_col_1, col_2, time_col_2, labels=("MAWP", "ECCC"))


if __name__ == "__main__":
    main()
