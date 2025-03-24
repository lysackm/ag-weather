import xarray as xr
import glob
import pandas as pd
import warnings
from datetime import timedelta

warnings.filterwarnings("error")


def peek_nc(file):
    warnings.filterwarnings('default')
    print("Peeking into the file", file)
    ds = xr.load_dataset(file)
    print(ds, "\n")
    warnings.filterwarnings('error')


# returns a dataframe with the metadata, a data array with the lat and long (in that order)
def load_station_metadata():
    stn_df = pd.read_csv("metadata/station_metadata.csv")
    stn_df = stn_df[["SN", "StnID", "StationName", "stn_lat", "stn_long", "Region", "Elevation"]]
    lat = xr.DataArray(stn_df['stn_lat'], coords={"StnID": stn_df["StnID"]})
    long = xr.DataArray(stn_df['stn_long'], coords={"StnID": stn_df["StnID"]})

    return stn_df, lat, long


# new column called `time_utc` is created
# column with local time is `time`
def localize_time_column(df, time_col="time"):
    df["time_utc"] = df[time_col].dt.tz_localize('utc')
    df["time"] = df["time_utc"].dt.tz_convert('America/Winnipeg')
    return df


# take a dictionary mapping columns and change the names of the keys
# to be the values
def convert_column_names(df, col_dict):
    return df.rename(columns=col_dict)


# better name
def reset_index(df):
    df = df.reset_index()
    if "SN-1" in df.columns:
        df["SN"] = df["SN-1"] + 1
        df = df.drop(columns="SN-1")
    return df


def merge_in_stn_metadata(df, stn_metadata_df):
    merged_df = df.merge(stn_metadata_df, how="left", on="StnID")
    return merged_df


# merge on time and location
def merge_dfs(df_1, df_2, on=["time", "StnID"], how="inner"):
    merged_df = df_1.merge(df_2, how=how, on=on)
    merged_df = merged_df.reset_index()
    return merged_df


def save_data(df, dest_file):
    print("Saving data to", dest_file)
    df.to_csv("./data/" + dest_file, index=False)


def month_and_day_to_doy(row):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month = int(row["NormMM"])
    day = int(row["NormDD"])
    doy = sum(days_in_month[0:month - 1]) + day
    return doy


def apply_function_daily(df_daily, df, src_column, operation, dest_column=""):
    if dest_column == "":
        dest_column = src_column

    df["NormYY"] = df["time"].dt.year
    df["NormMM"] = df["time"].dt.month
    df["NormDD"] = df["time"].dt.day

    groupby_columns = [df["NormYY"], df["NormMM"], df["NormDD"], df["StnID"]]
    if operation == "max":
        df_daily[dest_column] = df[src_column].groupby(by=groupby_columns).max(min_count=1).values
    elif operation == "min":
        df_daily[dest_column] = df[src_column].groupby(by=groupby_columns).min(min_count=1).values
    elif operation == "avg":
        numerator_df = df[src_column].groupby(by=[df["time"].dt.year.rename("NormYY"),
                                              df["time"].dt.month.rename("NormMM"),
                                              df["time"].dt.day.rename("NormDD"),
                                              df["StnID"]]).sum(min_count=1)
        denominator_df = df[src_column].groupby(by=[df["time"].dt.year.rename("NormYY"),
                                                df["time"].dt.month.rename("NormMM"),
                                                df["time"].dt.day.rename("NormDD"),
                                                df["StnID"]]).count()

        df_daily = numerator_df / denominator_df
    elif operation == "sum":
        df_daily[dest_column] = df[src_column].groupby(by=groupby_columns).sum(min_count=1).values

    return df_daily


def hourly_to_daily_df(df, columns, daily_merge_operations):
    operations = ["max", "min", "avg", "sum"]

    # If the daily time starts not at 00:00 then this will not detect it
    is_hourly = not (df["time"].dt.hour == 0).all()
    if is_hourly:
        # climatological day starts at utc=06:00
        df["time_utc_adjusted"] = df["time_utc"] - timedelta(hours=6)
        df["time"] = df["time_utc_adjusted"]
        df_daily = df[columns].groupby(by=[df["time_utc_adjusted"].dt.year.rename("NormYY"),
                                           df["time_utc_adjusted"].dt.month.rename("NormMM"),
                                           df["time_utc_adjusted"].dt.day.rename("NormDD"),
                                           df["StnID"]]).mean()

        df_daily.reset_index()

        for column in columns:
            # Not the most readable code...
            if type(daily_merge_operations[column]) is list:
                for daily_merge_operation in daily_merge_operations[column]:
                    if daily_merge_operation in column:
                        df_daily = apply_function_daily(df_daily, df, column, daily_merge_operation)
                    elif any(substring in column for substring in operations):
                        old_operation = [substring for substring in operations if substring in column][0]
                        dest_column = column.replace(old_operation, "") + daily_merge_operation
                        df_daily = apply_function_daily(df_daily, df, column, daily_merge_operation, dest_column)
                    else:
                        dest_column = column + "_" + daily_merge_operation
                        df_daily = apply_function_daily(df_daily, df, column, daily_merge_operation, dest_column)
            else:
                df_daily = apply_function_daily(df_daily, df, column, daily_merge_operations[column])

        return df_daily
    else:
        df["time"] = df["time_utc"]
        numerator_df = df[columns].groupby(by=[df["time"].dt.year.rename("NormYY"),
                                           df["time"].dt.month.rename("NormMM"),
                                           df["time"].dt.day.rename("NormDD"),
                                           df["StnID"]]).sum(min_count=1)
        denominator_df = df[columns].groupby(by=[df["time"].dt.year.rename("NormYY"),
                                             df["time"].dt.month.rename("NormMM"),
                                             df["time"].dt.day.rename("NormDD"),
                                             df["StnID"]]).count()

        df_daily = numerator_df/denominator_df
        return df_daily


class StandardizeDailyData:
    def __init__(self, source_file, dest_file):
        self.source_file = source_file
        self.dest_file = dest_file

        warnings.filterwarnings('default')
        self.df = pd.read_csv("./data/" + source_file, na_values=[""])
        warnings.filterwarnings('error')

    def time_col_to_datetime(self, time_col, utc_col):
        try:
            self.df["time"] = pd.to_datetime(self.df[time_col])
        except FutureWarning:
            self.df["time"] = pd.to_datetime(self.df[time_col], utc=True)

        if utc_col is not None:
            self.df["time_utc"] = pd.to_datetime(self.df[utc_col], utc=True)
        elif utc_col is None:
            self.df["time_utc"] = self.df["time"].dt.tz_localize('utc')

    def add_stn_id_col(self, stn_col):
        stn_metadata = load_station_metadata()[0]
        if stn_col == "SN" or stn_col == "StnID":
            stn_metadata = stn_metadata[["SN", "StnID"]]
            self.df = self.df.merge(stn_metadata, how="left", on=stn_col)
        else:
            stn_metadata = stn_metadata[[stn_col, "SN", "StnID"]]
            self.df = self.df.merge(stn_metadata, how="left", on=stn_col)

    def create_daily_df(self, daily_merge_operations):
        columns = daily_merge_operations.keys()
        self.df = hourly_to_daily_df(self.df, columns, daily_merge_operations)
        # if NormYY, NormMM, NormDD are in the index, reset the index
        if {"NormYY", "NormMM", "NormDD"} <= set(self.df.index.names):
            self.df = self.df.reset_index()
        time_df = self.df[["NormYY", "NormMM", "NormDD"]].copy()
        time_df = time_df.rename(columns={"NormYY": "year", "NormMM": "month", "NormDD": "day"})
        self.df["DateDT"] = pd.to_datetime(time_df)

    def back_fill_column(self, col_1, col_2):
        self.df[col_1] = self.df[col_1].fillna(self.df[col_2])

    def unit_convert_column(self, col, conversion):
        if type(conversion) is int or type(conversion) is float:
            self.df[col] = self.df[col] + conversion
        else:
            print("unit_convert_column, not coded yet")
            exit(1)

    def rename_columns(self, dict_column_names):
        self.df = self.df.rename(columns=dict_column_names)

    def save_df(self):
        save_data(self.df, "standardized_daily/" + self.dest_file)


class CreateClimateNormal:
    def __init__(self, source_file, dest_file, variables):
        self.source_file = source_file
        self.dest_file = dest_file
        self.df = pd.read_csv("./data" + source_file)
        self.variables = variables

    def create_normal(self, daily_merge_operations):
        self.to_datetime()

        # intersection of the columns, and columns we want to mean
        columns = list(set(self.df.columns) & {"Tmax", "Tmin", "Tavg", "PPT"})

        stn_metadata = load_station_metadata()[0]
        stn_metadata = stn_metadata[["StnID", "StationName", "SN"]]
        self.df = merge_in_stn_metadata(self.df, stn_metadata)

        self.df = hourly_to_daily_df(self.df, columns, daily_merge_operations)
        self.df = self.df[columns].groupby(by=[self.df["NormMM"],
                                               self.df["NormDD"],
                                               self.df["StnID"],
                                               self.df["StationName"],
                                               self.df["SN"]]).mean()
        self.df = self.df.reset_index()

        self.df["NormYY"] = 2020
        self.df["JD"] = self.df.apply(month_and_day_to_doy, axis=1)
        self.df["DateDT"] = pd.to_datetime({
            "year": self.df["NormYY"],
            "month": self.df["NormMM"],
            "day": self.df["NormDD"]})

    def unit_convert_column(self, col, conversion):
        if type(conversion) is int or type(conversion) is float:
            self.df[col] = self.df[col] + conversion
        else:
            print("unit_convert_column, not coded yet")
            exit(1)

    def to_datetime(self):
        self.df["time"] = pd.to_datetime(self.df["time"], utc=True)
        self.df["time"] = self.df["time"].dt.tz_convert('America/Winnipeg')
        self.df["time_utc"] = pd.to_datetime(self.df["time_utc"], utc=True)

    def save_climate_normal(self):
        save_data(self.df, "/climate_normal/" + self.dest_file)


class ProcessRawData:
    def __init__(self, lat, long, lat_name, long_name, base_file, file_regex, dim, column_names=None, dest_file="",
                 save_df=True):
        self.lat = lat
        self.long = long
        self.lat_name = lat_name
        self.long_name = long_name

        self.base_file = base_file
        self.file_regex = file_regex
        self.dim = dim

        self.column_names = column_names
        self.base_columns = [
            "time",
            "time_utc",
            "Tmin",
            "Tmax",
            "Tavg"
            "lon",
            "lat",
            "StnID"
        ]

        self.dest_file = dest_file
        self.save_df = save_df

    def extract_station_locations(self, da):
        indexers = {self.lat_name: self.lat, self.long_name: self.long}
        filtered_data = da.sel(indexers, method="nearest")
        return filtered_data

    def load_nc_data(self):
        warnings.filterwarnings('default')

        complete_regex = self.base_file + self.file_regex
        files = glob.glob(complete_regex)

        data_arrays = []
        for file in files:
            raw_da = xr.load_dataset(file)
            location_filtered_da = self.extract_station_locations(raw_da)
            if "valid_time" in location_filtered_da.variables:
                location_filtered_da = location_filtered_da.rename({"valid_time": "time"})
                location_filtered_da = location_filtered_da.drop_vars(["number", "expver"])
            data_arrays.append(location_filtered_da)

        merged_data_array = xr.concat(data_arrays, self.dim)
        warnings.filterwarnings('error')
        return merged_data_array

    def create_csv_from_netcdf(self):
        df = self.load_nc_data().to_dataframe()
        df = reset_index(df)
        df = localize_time_column(df)
        df = self.rename_columns(df)

        if self.save_df:
            save_data(df, self.dest_file)
        return df

    def rename_columns(self, df):
        # given a dict standardize the names of the columns
        # StnNormID, StnID, Location, NormYY, NormMM, NormDD, DateDT, Tmax, Tmin, Tavg, PPT, CHU, GDD, PDay, NormLocation
        df = df.rename(columns=self.column_names)
        columns = list(set((self.base_columns + list(self.column_names.values()))) & set(df.columns))
        df = df[columns]
        return df


# different functions that are similar to main, but do not want
# to run everytime
def era5_t2m():
    # peek_nc("D:/data/era5/t2m1994.nc/data.nc")
    base_file = "D:/data/era5/"
    file_regex = "t2m[0-9][0-9][0-9][0-9].nc/data.nc"
    dim = "time"
    dest_file = "era5_temperature.csv"
    column_names = {"time": "time",
                    "time_utc": "time_utc",
                    "latitude": "lat",
                    "longitude": "lon",
                    "t2m": "Tavg",
                    "StnID": "StnID"}

    stn_df, lat, long = load_station_metadata()

    era5_processing = ProcessRawData(lat, long, "latitude", "longitude", base_file, file_regex, dim, column_names,
                                     dest_file)
    era5_processing.create_csv_from_netcdf()


def nrcan():
    stn_df, lat, long = load_station_metadata()
    dest_file = "nrcan.csv"
    column_names = {"time": "time",
                    "time_utc": "time_utc",
                    "lon": "lon",
                    "lat": "lat",
                    "mint": "Tmin",
                    "maxt": "Tmax",
                    "pcp": "PPT",
                    "StnID": "StnID"}

    # for nrcan min_t
    base_file = "D:/data/nrcan/"
    file_regex = "mint_dly_[0-9][0-9][0-9][0-9]_deflated.nc"
    dim = "time"
    nr_mint_processing = ProcessRawData(lat, long, "lat", "lon", base_file, file_regex, dim, column_names, dest_file,
                                        save_df=False)
    mint_df = nr_mint_processing.create_csv_from_netcdf()

    # for nrcan min_t
    base_file = "D:/data/nrcan/"
    file_regex = "maxt_dly_[0-9][0-9][0-9][0-9]_deflated.nc"
    dim = "time"
    nr_maxt_processing = ProcessRawData(lat, long, "lat", "lon", base_file, file_regex, dim, column_names, dest_file,
                                        save_df=False)
    maxt_df = nr_maxt_processing.create_csv_from_netcdf()

    # for nrcan pcp
    base_file = "D:/data/nrcan/"
    file_regex = "pcp_dly_[0-9][0-9][0-9][0-9]_deflated.nc"
    dim = "time"
    nr_pcp_processing = ProcessRawData(lat, long, "lat", "lon", base_file, file_regex, dim, column_names, dest_file,
                                       save_df=False)
    pcp_df = nr_pcp_processing.create_csv_from_netcdf()

    on = ["time", "time_utc", "lat", "lon", "StnID"]
    merged_df = merge_dfs(mint_df, maxt_df, on=on)
    merged_df = merged_df.drop(columns=["index"])
    merged_df = merge_dfs(merged_df, pcp_df, on=on)
    merged_df = merged_df.drop(columns=["index"])

    save_data(merged_df, dest_file)


def nrcan_climate_normal():
    create_climate_normal_nrcan = CreateClimateNormal("./nrcan.csv",
                                                      "nrcan.csv",
                                                      ["Tmin", "Tmax", "PPT"])
    daily_merge_operations = {"Tmin": "mean",
                              "Tmax": "sum",
                              "PPT": "mean"}
    create_climate_normal_nrcan.create_normal(daily_merge_operations)
    create_climate_normal_nrcan.save_climate_normal()


def ear5_climate_normal():
    create_climate_normal_era5 = CreateClimateNormal("era5_temperature.csv",
                                                     "era5_temperature.csv",
                                                     ["Tavg"])
    daily_merge_operations = {"Tavg": "mean"}
    create_climate_normal_era5.create_normal(daily_merge_operations)
    create_climate_normal_era5.unit_convert_column("Tavg", -273.15)
    create_climate_normal_era5.save_climate_normal()


# All eccc stations are too large, need to only use stations which
# will be merged with mbag stations (since the 90s)
def station_eccc():
    eccc_mbag_mapping_df = pd.read_csv("./metadata/ECCC_mbag_station_map.csv")[["Climate ID", "StnID", "SN"]]
    climate_ids = list(set(eccc_mbag_mapping_df["Climate ID"].tolist()))

    dfs = []
    for climate_id in climate_ids:
        file = "D:/data/environment_canada/merged_by_station/" + climate_id + ".csv"

        warnings.filterwarnings('default')
        df = pd.read_csv(file)
        warnings.filterwarnings('error')
        dfs.append(df)

    merged_df = pd.concat(dfs)
    del dfs

    merged_df["Climate ID"] = merged_df["Climate ID"].astype(str)
    eccc_mbag_mapping_df["Climate ID"] = eccc_mbag_mapping_df["Climate ID"].astype(str)

    merged_df = merged_df.merge(eccc_mbag_mapping_df, on="Climate ID", how="left")
    merged_df = merged_df.reset_index()
    merged_df.to_csv("./data/eccc.csv", index=False)


# Actually saves it outside the project directory. For grouping the data together
# by station
def eccc():
    eccc_metadata_df = pd.read_csv("./metadata/Manitoba_ECCC_metadata.csv")
    climate_ids = eccc_metadata_df["Climate ID"].tolist()

    for climate_id in climate_ids:
        regex = "D:/data/environment_canada/all_data/*_" + climate_id + "_*.csv"
        files = glob.glob(regex)
        dfs = []
        for file in files:
            df = pd.read_csv(file)
            dfs.append(df)

        merged_df = pd.concat(dfs)
        dest_file = "D:/data/environment_canada/merged_by_station/" + climate_id + ".csv"
        merged_df.to_csv(dest_file, index=False)


def daily_standardize_era5():
    file = "era5_temperature.csv"
    date_col = "time"
    utc_col = "time_utc"
    stn_col = "StnID"
    daily_merge_operations = {
        "Tavg": ["mean", "max", "min"]
    }

    standardize_daily_data = StandardizeDailyData(file, file)
    standardize_daily_data.time_col_to_datetime(date_col, utc_col)
    standardize_daily_data.add_stn_id_col(stn_col)
    standardize_daily_data.create_daily_df(daily_merge_operations)
    standardize_daily_data.unit_convert_column("Tavg", -273.15)
    standardize_daily_data.unit_convert_column("Tmax", -273.15)
    standardize_daily_data.unit_convert_column("Tmin", -273.15)
    standardize_daily_data.save_df()


def daily_standardize_mbag():
    file = "mbag_stations.csv"
    date_col = "TMSTAMP"
    stn_col = "StnID"
    daily_merge_operations = {
        "Tavg": "mean",
        "Tmax": "max",
        "Tmin": "min",
        "PPT": "sum"
    }
    rename_cols = {
        "AvgAir_T": "Tavg",
        "MaxAir_T": "Tmax",
        "MinAir_T": "Tmin",
        "Pluvio_Rain": "PPT"
    }

    standardize_daily_data = StandardizeDailyData(file, file)
    standardize_daily_data.time_col_to_datetime(date_col, None)
    # need custom code to filter out invalid tipping bucket data in the winter
    in_new_year = (standardize_daily_data.df["time"].dt.dayofyear < 75)
    in_end_of_year = (standardize_daily_data.df["time"].dt.dayofyear > 320)
    is_freezing = standardize_daily_data.df["AvgAir_T"] < 3
    mask_df = in_new_year | in_end_of_year | is_freezing

    standardize_daily_data.df["TBRG_Rain"] = standardize_daily_data.df["TBRG_Rain"].mask(mask_df)
    standardize_daily_data.back_fill_column("Pluvio_Rain", "TBRG_Rain")

    standardize_daily_data.add_stn_id_col(stn_col)
    standardize_daily_data.rename_columns(rename_cols)
    standardize_daily_data.create_daily_df(daily_merge_operations)
    standardize_daily_data.save_df()


def daily_standardize_nrcan():
    file = "nrcan.csv"
    date_col = "time"
    utc_date_col = "time_utc"
    stn_col = "StnID"
    daily_merge_operations = {
        "Tmin": "mean",
        "Tmax": "mean",
        "PPT": "sum"
    }

    standardize_daily_data = StandardizeDailyData(file, file)
    standardize_daily_data.time_col_to_datetime(date_col, utc_date_col)
    standardize_daily_data.add_stn_id_col(stn_col)
    standardize_daily_data.create_daily_df(daily_merge_operations)
    standardize_daily_data.save_df()


def daily_standardize_eccc():
    file = "eccc.csv"
    date_col = "Date/Time"
    rename_cols = {
        "Mean Temp (°C)": "Tavg",
        "Max Temp (°C)": "Tmax",
        "Min Temp (°C)": "Tmin",
        "Total Precip (mm)": "PPT"
    }
    daily_merge_operations = {
        "Tmin": "mean",
        "Tmax": "mean",
        "Tavg": "mean",
        "PPT": "sum"
    }

    standardize_daily_data = StandardizeDailyData(file, file)
    standardize_daily_data.time_col_to_datetime(date_col, None)
    standardize_daily_data.rename_columns(rename_cols)
    standardize_daily_data.create_daily_df(daily_merge_operations)
    standardize_daily_data.save_df()


def main():
    # ear5_climate_normal()
    # nrcan()
    # nrcan_climate_normal()
    # era5_t2m()
    eccc()
    station_eccc()

    # daily_standardize_era5()
    daily_standardize_mbag()
    # daily_standardize_nrcan()
    daily_standardize_eccc()


if __name__ == "__main__":
    main()
