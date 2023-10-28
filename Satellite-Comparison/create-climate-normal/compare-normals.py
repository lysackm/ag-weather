import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math


def compare_normals():
    normal_df = pd.read_csv("../../../data/2000-normal.csv")
    corrected_df = pd.read_csv("../../../data/climate_normal_avg/2000_era5.csv")

    print(normal_df["Location"].unique())

    normal_df = normal_df[normal_df["Location"] == "RUSSELL"]
    corrected_df = corrected_df[corrected_df["Location"] == "RUSSELL"]

    print(normal_df)

    merged_df = normal_df.merge(corrected_df, how="inner", on=["Location", "DateDT"])

    print("Tmax", round(math.sqrt(mean_squared_error(merged_df["Tmax_x"], merged_df["Tmax_y"])), 2))
    print("Tmin", round(math.sqrt(mean_squared_error(merged_df["Tmin_x"], merged_df["Tmin_y"])), 2))
    print("Tavg", round(math.sqrt(mean_squared_error(merged_df["Tavg_x"], merged_df["Tavg_y"])), 2))
    print("PPT", round(math.sqrt(mean_squared_error(merged_df["PPT_x"], merged_df["PPT_y"])), 2))
    print("CHU", round(math.sqrt(mean_squared_error(merged_df["CHU_x"], merged_df["CHU_y"])), 2))
    print("GDD", round(math.sqrt(mean_squared_error(merged_df["GDD_x"], merged_df["GDD_y"])), 2))
    
    print("mean error \n \n")

    print("Tmax", round((merged_df["Tmax_x"] - merged_df["Tmax_y"]).mean(), 2))
    print("Tmin", round((merged_df["Tmin_x"] - merged_df["Tmin_y"]).mean(), 2))
    print("Tavg", round((merged_df["Tavg_x"] - merged_df["Tavg_y"]).mean(), 2))
    print("PPT", round((merged_df["PPT_x"] - merged_df["PPT_y"]).mean(), 2))
    print("CHU", round((merged_df["CHU_x"] - merged_df["CHU_y"]).mean(), 2))
    print("GDD", round((merged_df["GDD_x"] - merged_df["GDD_y"]).mean(), 2))

    # random forest corrected model preforming poorly, make sure equations are working correctly
    # maybe try using non modified era5 data instead.


compare_normals()
