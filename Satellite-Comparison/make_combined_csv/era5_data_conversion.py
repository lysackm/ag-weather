from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

from make_combined_csv import *
import metpy as mp
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

data_dir = '../../../../data/'


def train_random_forest(attr_stn_col, era5_stn_col):
    n_estimators = 100
    max_features = 0.5
    min_samples_leaf = 1

    df = pd.read_csv("..\error_correction\\random_forest_data.csv")
    # convert time to datetime to apply operations
    df["time"] = pd.to_datetime(df["time"])

    era5_df = df[["era5_lat", "era5_long", "elevation", "era5_AvgAir_T", "era5_AvgWS", "era5_Pluvio_Rain",
                  "era5_Press_hPa", "era5_RH", "era5_SolarRad", attr_stn_col]]
    era5_df = era5_df.assign(month=df["time"].dt.month)
    era5_df = era5_df.assign(hour=df["time"].dt.hour)

    era5_df = era5_df.dropna(how="any")

    x_arr = era5_df[
        ["era5_lat", "era5_long", "elevation", "era5_AvgAir_T", "era5_AvgWS", "era5_Pluvio_Rain", "era5_Press_hPa",
         "era5_RH", "era5_SolarRad", "month", "hour"]].to_numpy()
    y_arr = (era5_df[attr_stn_col] - era5_df[era5_stn_col]).to_numpy()

    model = RandomForestRegressor(n_estimators=n_estimators, max_features=max_features,
                                  min_samples_leaf=min_samples_leaf, n_jobs=-1)
    model.fit(x_arr, y_arr)

    predicted_test = model.predict(x_arr)
    rmse = np.sqrt(mean_squared_error(y_arr, predicted_test))

    print(f'Root mean squared error: {rmse:.3}')

    return model


# Utility function to modify the elevation file given as geopotential
# by era5. Not ran everytime main runs
def extract_elevation():
    # ds = xr.open_dataset('../create-climate-normal/geopotential.nc')
    #
    # ds = ds.map(mp.calc.geopotential_to_height)
    #
    # ds.to_netcdf('../create-climate-normal/elevation.nc')

    da = xr.open_dataarray('../create-climate-normal/elevation.nc')
    da = da.squeeze(drop=True)
    # used to shift over to -180 to 180 instead of 0 to 360
    # da['longitude'] = da['longitude'] - 360
    print(da)

    print(da.loc[52.3:49.0, -102:-95])
    # (52.34, -102.03), (49, -95)

    da.loc[52.3:49.0, -102:-95].plot()
    plt.show()


def merge_ds_attr_files():
    print('Merge_attr_files')

    attr_names = ['t2m', 'rad', 'totprec', 'v10m', 'u10m', 'sp', '2mdt']
    base_dir = data_dir + '/historical_era5/'

    for year in range(2016, 2018):
        data_sets = []

        for attr_name in attr_names:
            filename = base_dir + 'attribute/' + attr_name + str(year) + '.nc/data.nc'
            data_sets.append(xr.open_dataset(filename))

        ds_merge = xr.merge(data_sets)
        print(ds_merge)
        ds_merge.to_netcdf(base_dir + 'yearly/' + str(year) + '.nc')
        print('merged file ' + str(year))


def calculate_era5_sp(p, t2m, elevation):
    numerator = 0.0065 * elevation.copy()
    denominator = t2m + 0.0065 * elevation.copy() + 273.15

    # equation source https://keisan.casio.com/exec/system/1224575267
    sp = p * (1 - numerator.div(denominator)) ** -5.257

    return sp


def calculate_era5_rh(temp, dew_point):
    numerator = math.e ** ((17.625 * dew_point).div(243.04 + dew_point))
    denominator = math.e ** ((17.625 * temp).div(243.04 + temp))

    col = numerator.div(denominator) * 100
    return col


def calculate_era5_ws(v, u):
    v = (v ** 2 + u ** 2) ** (1 / 2)
    return v


# Assumed it is an attribute from the era5_attr list
def get_era_filename(year):
    return data_dir + '/historical_era5/yearly/' + str(year) + '.nc'


# load era5 data from the file and return a xarray data array
def load_era5_data(year):
    era5_file = get_era_filename(year)
    # data array since 1 attribute per file
    era5_da = xr.open_dataset(era5_file)
    era5_df = era5_da.to_dataframe()
    era5_df = era5_df.reset_index()

    era5_df['longitude'] = era5_df['longitude'].round(1)
    era5_df['latitude'] = era5_df['latitude'].round(1)
    era5_df['lat'] = era5_df['latitude']
    era5_df['long'] = era5_df['longitude']
    era5_df = era5_df.assign(month=era5_df["time"].dt.month)
    era5_df = era5_df.assign(hour=era5_df["time"].dt.hour)

    elevation_df = xr.open_dataset('../create-climate-normal/elevation.nc').to_dataframe()
    elevation_df = elevation_df.reset_index()
    elevation_df = elevation_df.rename(columns={'z': 'elevation'})
    elevation_df['longitude'] = elevation_df['longitude'].round(1)
    elevation_df['latitude'] = elevation_df['latitude'].round(1)

    era5_df = era5_df.merge(elevation_df, how='inner', on=['latitude', 'longitude'])
    era5_df.set_index(['time', 'latitude', 'longitude'], inplace=True)
    print('final', era5_df, era5_df.columns)

    for attr in era5_df.columns:
        if attr not in ['u10', 'v10', 'elevation']:
            era5_df[attr] = era5_df[attr].apply(conversions.get(attr, lambda x: x))

    print("null rows 1", era5_df[era5_df.isnull().any(axis=1)][['sp', 'elevation', 't2m']])
    print("row one", era5_df[era5_df.isnull().any(axis=1)].iloc[0])

    era5_df["ws"] = calculate_era5_ws(era5_df['v10'], era5_df['u10'])
    era5_df['rh'] = calculate_era5_rh(era5_df['t2m'], era5_df['d2m'])
    era5_df['sp'] = calculate_era5_sp(era5_df['sp'], era5_df['t2m'], era5_df['elevation'])

    print("columns", era5_df.columns)

    print("null rows 2", era5_df[era5_df.isnull().any(axis=1)][['sp', 'elevation', 't2m']])
    era5_df = era5_df.dropna()

    return era5_df[['lat', 'long', 'elevation', 't2m', 'ws', 'tp', 'sp', 'rh', 'ssrd', 'month', 'hour']]


def apply_model(df, model, attr_col):
    # double check this
    df[attr_col + '_corr'] = df[attr_col] + model.predict(df)


def main():
    attrs = ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH", "SolarRad"]
    historical_attrs = ["t2m", "ws", "tp", "sp", "rh", "sr"]

    for attr, era5_attr in zip(attrs, historical_attrs):
        attr_stn_col = "stn_" + attr
        attr_model_col = "era5_" + attr
        model = train_random_forest(attr_stn_col, attr_model_col)

        for year in range(1990, 1992):
            print("Year completed:", year)
            era5_df = load_era5_data(year)
            apply_model(era5_df, model, era5_attr)

            corrected_col = era5_df[era5_attr + '_corr']
            print("Finished applying model: ", corrected_col)
            corrected_col.to_csv("climate_normal_data/" + str(year) + "_" + attr + "csv")


merge_ds_attr_files()
# extract_elevation()
# main()
