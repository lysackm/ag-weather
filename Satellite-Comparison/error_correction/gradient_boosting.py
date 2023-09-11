import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import RandomizedSearchCV


# raw data to stored np array
def process_data(attr_stn_col, attr_model_col, model):
    df = pd.read_csv("random_forest_data.csv")

    df["time"] = pd.to_datetime(df["time"])

    model_df = df[[model + "_lat", model + "_long", "elevation", model + "_AvgAir_T", model + "_AvgWS",
                   model + "_Pluvio_Rain", model + "_Press_hPa", model + "_RH", model + "_SolarRad", attr_stn_col, "Station"]]
    model_df = model_df.assign(month=df["time"].dt.month)
    model_df = model_df.assign(hour=df["time"].dt.hour)
    # calculate the difference between the station location and the merra location
    model_df = model_df.assign(dist=((df["stn_long"] - df[model + "_long"]) ** 2 +
                                     (df["stn_lat"] - df[model + "_lat"]) ** 2) ** 1 / 2)

    model_df[attr_stn_col] = model_df[attr_stn_col] - model_df[attr_model_col]

    model_df = model_df.dropna()

    return model_df


def time_fading(df):
    num_previous = 24
    model = "era5"
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


def load_data(attr, is_time_faded=False):
    model = "era5"
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
        x_df = model_df.loc[:, model_df.columns != "Station"]
        x_arr = x_df.loc[:, x_df.columns != attr_stn_col].to_numpy()
        y_arr = model_df[attr_stn_col].to_numpy()

    x_train, x_test, y_train, y_test = train_test_split(
        x_arr, y_arr, test_size=0.2)

    return x_train, x_test, y_train, y_test


def tune_parameters():
    attr = "AvgAir_T"
    params = {
        "loss": ["squared_error", "absolute_error"],
        "learning_rate": [None, 0.1, 0.01, 0.001],
        "max_leaf_nodes": [None, 50, 500, 1000],
        "min_samples_leaf": [30, 50, 100],
        "l2_regularization": [0.1, 0.01, 0]
    }

    gradient_model = HistGradientBoostingRegressor(max_iter=500)

    model = RandomizedSearchCV(gradient_model, params)

    x_train, x_test, y_train, y_test = load_data(attr, True)

    search = model.fit(x_train, y_train)

    print(search.best_params_)
    print(search.cv_results_)


def train_gradient_boosting_regression(model=None, attr="AvgAir_T"):
    x_train, x_test, y_train, y_test = load_data(attr, True)

    if model is None:
        model = HistGradientBoostingRegressor(
            loss='squared_error',
            learning_rate=0.1,
            max_leaf_nodes=500,
            max_iter=3500,
            min_samples_leaf=10,
            l2_regularization=0)

    model = model.fit(x_train, y_train)

    score = model.score(x_test, y_test)

    print("score:", score)

    predicted_test = model.predict(x_test)
    rmse = np.sqrt(mean_squared_error(y_test, predicted_test))
    test_score = r2_score(y_test, predicted_test)
    spearman = spearmanr(y_test, predicted_test)
    pearson = pearsonr(y_test, predicted_test)

    print("Comprehensive Statistics")
    print(f'Root mean squared error: {rmse:.4}')
    print(f'Test data R-2 score: {test_score:.4}')
    print(f'Spearman: {spearman[0]:.4} Pearson: {pearson[0]:.4}')


for attr in ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH", "SolarRad"]:
    train_gradient_boosting_regression(attr=attr)
