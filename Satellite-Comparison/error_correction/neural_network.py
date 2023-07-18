import pandas as pd
import numpy as np
import torch


# raw data to stored np array
def process_data(attr_stn_col, model):
    df = pd.read_csv("random_forest_data.csv")
    model_df = df[[model + "_lat", model + "_lon", "elevation", model + "_AvgAir_T", model + "_AvgWS",
                   model + "_Pluvio_Rain", model + "_Press_hPa", model + "_RH", model + "_SolarRad", attr_stn_col]]
    model_df = model_df.assign(month=df["time"].dt.month)
    model_df = model_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the merra location
    model_df = model_df.assign(dist=((df["stn_long"] - df[model + "_lon"]) ** 2 +
                                     (df["stn_lat"] - df[model + "_lat"]) ** 2) ** 1 / 2)

    model_df = model_df.dropna()

    return model_df


# returns a tensor
def load_data(attr_stn_col):
    model = "merra"
    model_df = process_data(attr_stn_col, model)

    x_arr = model_df.loc[:, model_df.columns != attr_stn_col].to_numpy()
    y_arr = model_df[attr_stn_col].to_numpy()

    # tensors objects for pytorch
    x = torch.tensor(x_arr, dtype=torch.float32)
    y = torch.tensor(y_arr, dtype=torch.float32).reshape(-1, 1)
