import pandas as pd
import numpy as np
import torch
from torch import nn
import torch.optim as optim
from sklearn.model_selection import train_test_split


def time_series_data():
    df = pd.read_csv("random_forest_data.csv")


# raw data to stored np array
def process_data(attr_stn_col, attr_model_col, model):
    df = pd.read_csv("random_forest_data.csv")

    df["time"] = pd.to_datetime(df["time"])

    model_df = df[["Station", model + "_lat", model + "_lon", "elevation", model + "_AvgAir_T", model + "_AvgWS",
                   model + "_Pluvio_Rain", model + "_Press_hPa", model + "_RH", model + "_SolarRad", attr_stn_col]]
    model_df = model_df.assign(month=df["time"].dt.month)
    model_df = model_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the merra location
    model_df = model_df.assign(dist=((df["stn_long"] - df[model + "_lon"]) ** 2 +
                                     (df["stn_lat"] - df[model + "_lat"]) ** 2) ** 1 / 2)

    model_df[attr_stn_col] = model_df[attr_stn_col] - model_df[attr_model_col]

    model_df = model_df.dropna()

    for column in model_df.columns:
        if column != attr_stn_col and column != "Station":
            model_df[column] = normalize_column(model_df[column])

    return model_df


def normalize_column(x):
    col_max = x.max()
    col_min = x.min()

    x = (x - col_min) / (col_max - col_min) * 2 - 1
    return x


# returns a tensor
def load_data(attr, is_time_faded=False):
    model = "merra"
    attr_stn_col = "stn_" + attr
    attr_model_col = model + "_" + attr
    model_df = process_data(attr_stn_col, attr_model_col, model)

    if is_time_faded:
        model_df = time_fading(model_df)
        model_df = model_df.dropna()

        x_df = model_df.loc[:, model_df.columns != "Station"]
        x_df = x_df.loc[:, x_df.columns != attr_stn_col]
        x_arr = x_df.to_numpy()
        y_arr = model_df[attr_stn_col].to_numpy()

    else:
        x_arr = model_df.loc[:, model_df.columns != "Station"].to_numpy()
        y_arr = model_df[attr_stn_col].to_numpy()

    x_train, x_test, y_train, y_test = train_test_split(x_arr, y_arr, train_size=0.75)

    # tensors objects for pytorch
    x_train = torch.tensor(x_train, dtype=torch.float32)
    x_test = torch.tensor(x_test, dtype=torch.float32)

    y_train = torch.tensor(y_train, dtype=torch.float32).reshape(-1, 1)
    y_test = torch.tensor(y_test, dtype=torch.float32).reshape(-1, 1)

    return x_train, x_test, y_train, y_test


def time_fading(df):
    num_previous = 3
    model = "merra"
    df_past = df[[model + "_AvgAir_T", model + "_AvgWS", model + "_Pluvio_Rain",
                  model + "_Press_hPa", model + "_RH", model + "_SolarRad"]]

    for i in range(num_previous):
        str_num = str(i) + model
        new_col_names = [str_num + "_AvgAir_T", str_num + "_AvgWS", str_num + "_Pluvio_Rain",
                         str_num + "_Press_hPa", str_num + "_RH", str_num + "_SolarRad"]

        df[new_col_names] = (df_past
                             .groupby(df["Station"], group_keys=False)
                             .apply(lambda s: s.bfill().shift(-1)))
        df_past = df[new_col_names]

    return df


def train_neural_network(model, x_train, x_test, y_train, y_test):
    n_epochs = 100
    batch_size = 10

    history = []

    loss_fn = nn.MSELoss()  # mean squared error loss function
    optimizer = optim.Adam(model.parameters(), weight_decay=0.01, lr=1e-5)

    for epoch in range(n_epochs):
        for i in range(0, len(x_train), batch_size):
            x_batch = x_train[i:i + batch_size]
            y_pred = model(x_batch)
            ybatch = y_train[i:i + batch_size]
            loss = loss_fn(y_pred, ybatch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        y_pred = model(x_test)
        mse = float(loss_fn(y_pred, y_test))
        history.append(mse)
        print(f'Finished epoch {epoch}, latest loss {loss}, test data mse {mse}')
    print(history)


def run_neural_network():
    # attrs = ["stn_AvgAir_T", "stn_AvgWS", "stn_Pluvio_Rain", "stn_Press_hPa", "stn_RH", "stn_SolarRad"]
    attr = "AvgAir_T"

    model = torch.nn.Sequential(
        nn.LazyLinear(128),
        nn.ReLU(),
        nn.LazyLinear(64),
        nn.ReLU(),
        nn.LazyLinear(32),
        nn.ReLU(),
        nn.LazyLinear(1),
    )

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Using {device} device")
    print(model)

    x_train, x_test, y_train, y_test = load_data(attr, True)
    print("loaded data")

    train_neural_network(model, x_train, x_test, y_train, y_test)


run_neural_network()
