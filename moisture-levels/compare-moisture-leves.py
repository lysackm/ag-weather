import glob
import pandas as pd

data_dir = "../../../data/station-csv/"


def remove_thawed_days(df):
    if df.size < 24 * 5 and not df["freezing_days"].all():
        df["freezing_days"] = True
    return df


def main():
    files = glob.glob(data_dir + "*.csv")

    for file in files:
        df = pd.read_csv(file)

        df["thawed_days"] = df["Soil_TP5_TempC"] >= 0

        df['binary_grp'] = (df.thawed_days.diff(1) != False).astype(int).cumsum()

        # df = df.groupby(["binary_grp", "Station"]).apply(remove_thawed_days)
        #
        # df['binary_grp_2'] = (df.freezing_days.diff(1) != False).astype(int).cumsum()
        df = df[df["thawed_days"]]

        groupby = df.groupby(["binary_grp", "Station"])

        for name, group in groupby:
            num_hours = 24 * 5
            if group.size > num_hours:
                print(group.size)
                print(group["Station"].iloc[0])
                print(group["TMSTAMP"].iloc[0])

            # print(name, group)

        # maybe if there are more than 1 group of frozen weather just take the moisture at the start + end?
        # also should it be thawed days instead of frozen days so that the moisture level is reading accurately
        # could do other tests like further in the soil, greater threshold for frozen soils, ect

        exit(1)


main()
