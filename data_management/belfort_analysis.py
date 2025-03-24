from compare_data_series import graph_compared_values
from sklearn.linear_model import LinearRegression
from scipy.stats import ttest_ind, linregress
import pandas as pd

def main():
    df_eccc = pd.read_csv("./data/belfort_shield/carman-eccc.csv")
    df_eccc = df_eccc[["Date/Time (LST)", "Precip. Amount (mm)"]]
    df_eccc = df_eccc.rename(columns={"Date/Time (LST)": "TMSTAMP", "Precip. Amount (mm)": "ECCC_Pluvio"})
    df_eccc["TMSTAMP"] = pd.to_datetime(df_eccc["TMSTAMP"])

    df = pd.read_csv("./data/belfort_shield/belfort_1_60.dat")
    df["TMSTAMP"] = pd.to_datetime(df["TMSTAMP"])

    df = df.merge(df_eccc, how="inner", on=["TMSTAMP"])

    # df = df[(df["Standard_Rain"] != 0) | (df["Belfort_Rain"] != 0) | (df["ECCC_Pluvio"] != 0)]
    # df = df[(df["Belfort_Rain"] != 0)]
    # print(df.corr())

    graph_compared_values(df["Standard_Rain"], df["ECCC_Pluvio"], df["TMSTAMP"], "MAWP Belfort", "ECCC")
    graph_compared_values(df["Standard_Rain"], df["Belfort_Rain"], df["TMSTAMP"], "Standard", "Belfort")
    graph_compared_values(df["Belfort_Rain"], df["ECCC_Pluvio"], df["TMSTAMP"], "MAWP Standard", "ECCC")

    # df = df[["Standard_Rain", "Belfort_Rain", "AvgWS"]]
    df = df[(df["Standard_Rain"] != 0)]
    # print(df["Standard_Rain"])
    # df["error"] = df["Standard_Rain"] - df["Belfort_Rain"]
    # df["percent_error"] = df["error"] / df["Standard_Rain"]
    # graph_corr_matrix(df)

    # uncomment for slopes
    slope, intercept, r, p, std_err = linregress(df["Standard_Rain"], df["Belfort_Rain"])

    print(slope, intercept, r, p, std_err)

    df["synergy"] = df["Standard_Rain"] * df["AvgWS"]
    reg = LinearRegression().fit(df[["Standard_Rain", "synergy"]], df["Belfort_Rain"])
    print(reg.coef_, reg.intercept_)

    df["corrected"] = df["Standard_Rain"] * 0.9958 + 0.0398 * df["synergy"] + 0.01524
    graph_compared_values(df["Belfort_Rain"], df["corrected"], df["TMSTAMP"], "Standard", "Equation 1")

    df["corrected_2"] = df["Standard_Rain"] * 1.1258 + 0.02349
    graph_compared_values(df["Belfort_Rain"], df["corrected_2"], df["TMSTAMP"], "Standard", "Equation 2")

    graph_compared_values(df["corrected"], df["corrected_2"], df["TMSTAMP"], "corrected 1", "corrected 2")

if __name__ == "__main__":
    main()
