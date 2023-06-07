import glob

import pandas as pd
import matplotlib.pyplot as plt


dates = pd.date_range(start="2018-01-01", periods=60, freq="M")

files = glob.glob("sqr-err/*.csv")

for file in files:
    x = []
    df = pd.read_csv(file)

    for station in df.columns:
        if station != "Unnamed: 0":
            plt.plot(dates, df[station], label=station)

    # for day in df.index:
    #     x.append(df.loc[day].mean(axis=0))
    #
    # x = x[:-1]

    # plt.plot(dates, x)

    plt.title(file.replace("./sqr-err\\", "").replace("_output.csv", ""))
    plt.xlabel("time")
    plt.ylabel("mean error")
    filename = "D:\\data\\graphs\\" + file.replace("_output.csv", ".png").replace("./sqr-err", "")
    print(filename)
    plt.savefig(filename)
    plt.clf()
