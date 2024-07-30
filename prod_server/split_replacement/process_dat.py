import sys
import glob
import time
import json
import tracemalloc
import shutil
import dat_logging
import pandas as pd

from datetime import datetime
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_number
from cProfile import Profile
from pstats import SortKey, Stats

# directory of the .dat files where the incoming data is coming
dat_dir = "D:\\data\\remote_server_mock\\.dats\\"
dest_dir = "D:\\data\\remote_server_mock\\.saved_data\\"
# dat_dir = "C:/Campbellsci/Dats/"
# dest_dir = "C:/WWW/mbagweather.ca/www/Partners/StagingTest/"


# get_date_since
# Take a string which is a dat and return a datetime object which represents
# the date which the date which to fetch data since
#
# get_date_since can either be a day, day and month, or full date
# If there is missing data then the current date is used to fill the date
def get_date_since_to_date(get_date_since):
    date_pieces = get_date_since.split("/")

    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    if len(date_pieces) == 3:
        year = date_pieces[0]
        month = date_pieces[1]
        day = date_pieces[2]
    elif len(date_pieces) == 2:
        month = date_pieces[0]
        day = date_pieces[1]
    elif len(date_pieces) == 1:
        day = date_pieces[0]

    date_str = str(year) + str(month) + str(day)

    try:
        date_since = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        dat_logging.log_non_fatal_error("Invalid get_data_since date, reading " + date_str + ". Using current date.")
        date_str = str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day)
        date_since = datetime.strptime(date_str, "%Y%m%d")

    return date_since


# given a df and a dictionary of column to threshold mappings, apply the threshold to
# each column. If value is lower than the lower_threshold, then the substitution replaces
# the value
def apply_lower_thresholds(df, lower_thresholds, substitution=""):
    for column, lower_threshold in lower_thresholds.items():
        try:
            df[column] = df[column].mask(df[column] < lower_threshold, other=substitution)
        except KeyError as e:
            dat_logging.log_warning("Key was not found in the dataframe and a lower threshold of "
                                    "lower_threshold was not applied to column " + column + ". KeyError: " + str(e))
        except TypeError as e:
            is_num_col = df[column].apply(is_number)
            df.loc[is_num_col, column] = df.loc[is_num_col, column].mask(df.loc[is_num_col, column] < lower_threshold,
                                                                         other=substitution)
            # Commented out logging upper/lower threshold removed data can trigger the warning
            # dat_logging.log_warning("Comparison with the type lower_threshold is incompatible. Applying "
            #                         "threshold to all numerical values. Column: " + column + " TypeError:  " + str(e))
    return df


# given a df and a dictionary of column to threshold mappings, apply the threshold to
# each column. If value is higher than the upper_threshold, then the substitution replaces
# the value
def apply_upper_thresholds(df, upper_thresholds, substitution=""):
    for column, upper_threshold in upper_thresholds.items():
        try:
            df[column] = df[column].mask(df[column] > upper_threshold, other=substitution)
        except KeyError as e:
            dat_logging.log_warning("Key column was not found in the dataframe and a lower threshold of lower_threshold"
                                    " was not applied to column " + column + ". KeyError: " + str(e))
        except TypeError as e:
            is_num_col = df[column].apply(is_number)
            df.loc[is_num_col, column] = df.loc[is_num_col, column].mask(df.loc[is_num_col, column] > upper_threshold,
                                                                         other=substitution)
            # Commented out logging upper/lower threshold removed data can trigger the warning
            # dat_logging.log_warning("Comparison with the type upper threshold is incompatible. Applying "
            #                         "threshold to all numerical values. Column: " + column + " TypeError: " + str(e))
    return df


# apply some transformation to the given df, based on a dictionary of column to transformation
# mappings. If the transformation is a string then all values are replaced with the string, if it
# is an int or float, then the transformation is multiplied to the column
def apply_transformations(df, transformations):
    for column, transformation in transformations.items():
        try:
            if type(transformation) is str:
                df[column] = transformation
            elif type(transformation) is int or type(transformation) is float:
                if is_numeric_dtype(df[column]):
                    df[column] = df[column] * transformation
                else:
                    dat_logging.log_warning("Found non numerical values when trying to apply a numerical transformation"
                                            "in column " + column + " applying transformation to all numerical data.")
                    is_num_col = df[column].apply(is_number)
                    df.loc[is_num_col, column] = df.loc[is_num_col, column] * transformation
        except KeyError as e:
            dat_logging.log_non_fatal_error("Trying to apply transformation " + str(transformation) +
                                            " when column " + column + " doesnt exist. KeyError: " + str(e))
    return df


# In the df add quotes to the values of the columns listed in quoted_columns
def apply_quotes(df, quoted_columns):
    for column in quoted_columns:
        df[column] = '"' + df[column] + '"'
    return df


# Format the column to the specified format in df_metadata
def format_time_column(df, timestamp, df_metadata, column, format_key):
    try:
        if format_key in df_metadata:
            df.loc[:, column] = timestamp.dt.strftime(df_metadata[format_key])
        else:
            if column == "TIME":
                df.loc[:, "TIME"] = timestamp.dt.time
            elif column == "DATE":
                df.loc[:, column] = timestamp.dt.date
    except ValueError as e:
        dat_logging.log_non_fatal_error("For file " + df_metadata["destination_file"] + " an improper date format was "
                                        "given, ValueError: " + str(e))


# Formats all date columns in df based on df_metadata, as well as handling getting the
# get_data_since property
def date_processing(df, df_metadata=None):
    if df_metadata is None:
        df_metadata = {}

    timestamp = pd.to_datetime(df["TMSTAMP"])

    format_time_column(df, timestamp, df_metadata, "DATE", "date_format")
    format_time_column(df, timestamp, df_metadata, "TIME", "time_format")
    format_time_column(df, timestamp, df_metadata, "TMSTAMP", "timestamp_format")

    if "get_data_since" in df_metadata:
        start_date = get_date_since_to_date(df_metadata["get_data_since"])
        df = df[timestamp > start_date]

    return df


# apply thresholds and transformations to df
def df_data_operations(df, df_metadata):
    if "lower_thresholds" in df_metadata:
        lower_threshold = df_metadata["lower_thresholds"]
        df = apply_lower_thresholds(df, lower_threshold)
    if "upper_thresholds" in df_metadata:
        upper_threshold = df_metadata["upper_thresholds"]
        df = apply_upper_thresholds(df, upper_threshold)
    if "transformations" in df_metadata:
        transformations = df_metadata["transformations"]
        df = apply_transformations(df, transformations)
    # pandas automatically adds triple quotes, undesired effect
    # if "quoted_columns" in df_metadata:
    #     quoted_columns = df_metadata["quoted_columns"]
    #     df = apply_quotes(df, quoted_columns)
    return df


# directly copy file from src_file to dest_file
def copy_file_directly(base_directory, src_file, dest_file):
    dest_file = dest_dir + base_directory + "/" + dest_file
    shutil.copy(src_file, dest_file)
    print("Copying directly:", base_directory)


# Move a single file to the partner which contains data from a single dat file. The
# metadata for how this should be processed is kept in version
def copy_individual_stn_data(partner_data, dat_file_full, df_stn, version):
    dat_file = dat_file_full.split("\\")[-1]

    if version in partner_data["copy_individual_stn_data"]:
        mapped_dat_files = partner_data["copy_individual_stn_data"][version][".dat_to_partner_file_mapping"]
        version_data = partner_data["copy_individual_stn_data"][version]

        if dat_file in mapped_dat_files:
            if "direct_copy" not in version_data or not version_data["direct_copy"]:
                if df_stn is None:
                    df_stn = load_dat(dat_file_full)
                df_processed = df_stn.copy()
                df_processed = df_data_operations(df_processed, version_data)
                df_processed = date_processing(df_processed, version_data)
                df_processed = column_formatting(df_processed, version_data)
                df_processed = process_column_mapping(df_processed, version_data, dat_file)
                save_df(df_processed, version_data, partner_data["base_directory"], mapped_dat_files[dat_file])
            else:
                copy_file_directly(partner_data["base_directory"], dat_file_full, mapped_dat_files[dat_file])

    return df_stn


# concat a station df to a larger df
def station_to_concat_file(df_concat, df_stn):
    return pd.concat([df_concat, df_stn])


# returns an inverted dictionary
# ie. if d = {a: b} returns {b: a}
def invert_dict(d):
    return {v: k for k, v in d.items()}


# apply special formatting to the columns to truncate decimals or add trailing zeros
def column_formatting(df, metadata):
    if "column_format" in metadata:
        for column, formatting in metadata["column_format"].items():
            try:
                df[column] = df[column].apply(formatting.format)
            except ValueError as e:
                dat_logging.log_non_fatal_error("Error in the value of the string format ValueError: " + str(e))
            except IndexError as e:
                dat_logging.log_non_fatal_error("Column does not exist when trying to apply string formatting: " +
                                                str(e))
    return df


# process the concatenated data to be as specified for an individual partner
def process_concat_data(df, metadata):
    if "previous_rows" in metadata:
        previous_rows = metadata["previous_rows"]
    else:
        previous_rows = "all"

    stations = metadata["stations"]

    df = df[df["StnID"].isin(stations)]
    df = df_data_operations(df.copy(), metadata)
    df = date_processing(df.copy(), metadata)
    if "StationName" in df.columns:
        df = df.sort_values(["StationName", "TMSTAMP"])
    else:
        df = df.sort_values["TMSTAMP"]

    if previous_rows != "all" and type(previous_rows) is int:
        df = df.groupby("StnID").tail(previous_rows)

    df = column_formatting(df, metadata)
    df = process_column_mapping(df, metadata)

    return df


# Add a custom header to a partners file
def add_header(metadata, partner, dest_file):
    # just copy header file to destination location?
    src_file = "./partner_headers/" + partner + "/" + metadata["header"]
    try:
        shutil.copy(src_file, dest_file)
    except FileNotFoundError as e:
        dat_logging.log_non_fatal_error("No header file found, default header used FileNotFoundError: " + str(e))
        return False
    return True


# save a df to the destination_file
def save_df(df, metadata, base_directory, destination_file):
    destination_file = dest_dir + base_directory + "/" + destination_file
    delimiter = ","
    header = True
    mode = "w"

    if "csv_deliminator" in metadata:
        delimiter = metadata["csv_deliminator"]

    if "header" in metadata:
        if type(metadata["header"]) is bool and not metadata["header"]:
            header = False
        elif type(metadata["header"]) is str:
            if add_header(metadata, base_directory, destination_file):
                header = False
                mode = "a"
            else:
                header = True

    try:
        df.to_csv(destination_file, index=False, sep=delimiter, header=header, mode=mode)
        print("Saving df to ", destination_file)
    except OSError as e:
        dat_logging.log_fatal_error("OSError when saving to file " + destination_file + " OSError: " + str(e))


# go through metadata related to concatenated data
def iterate_concat_data(df_concat, version_metadata, base_directory):
    if type(version_metadata) is list:
        for request in version_metadata:
            df = process_concat_data(df_concat.copy(), request)
            save_df(df, request, base_directory, request["destination_file"])
    elif type(version_metadata) is dict:
        df = process_concat_data(df_concat.copy(), version_metadata)
        save_df(df, version_metadata, base_directory, version_metadata["destination_file"])
    else:
        dat_logging.log_non_fatal_error("Unknown data when parsing the version meta data for " +
                                        base_directory + ". Skipping copying this data")


# take the concatenated data and process it based on partner specification
def copy_concat_stn_data(df_concat_15, df_concat_60, df_concat_24, partner_json):
    for partner in partner_json:
        base_dir = None
        try:
            if "copy_concatenated_stn_data" in partner_json[partner]:
                base_dir = partner_json[partner]["base_directory"]
                concat_data = partner_json[partner]["copy_concatenated_stn_data"]

                if "15" in concat_data:
                    iterate_concat_data(df_concat_15, concat_data["15"], base_dir)
                if "60" in concat_data:
                    iterate_concat_data(df_concat_60, concat_data["60"], base_dir)
                if "24" in concat_data:
                    iterate_concat_data(df_concat_24, concat_data["24"], base_dir)
        except Exception as e:
            dat_logging.log_fatal_error("Unknown error caught when processing concatenated dat file for  " + base_dir +
                                        " Exception: " + str(e))


# load a dat file, only read 2nd of 2 headers
def load_dat(filename):
    return pd.read_csv(filename, header=1)


# merge metadata into station data
def post_processing_concat_file(df, station_metadata):
    df = df.merge(station_metadata, how="left", on=["StnID"])
    return df


# rename columns in df
def process_column_mapping(df, metadata, dat_file=None):
    column_mapping = None
    if "column_mapping" in metadata and metadata["column_mapping"]:
        try:
            if "column_mapping_exceptions" in metadata and dat_file in metadata["column_mapping_exceptions"]:
                column_mapping = metadata["column_mapping_exceptions"][dat_file]
                df = df[list(column_mapping.keys())]
                df = df.rename(columns=column_mapping)
            else:
                column_mapping = metadata["column_mapping"]
                df = df[list(column_mapping.keys())]
                df = df.rename(columns=column_mapping)
        except KeyError as e:
            if column_mapping is None:
                dat_logging.log_non_fatal_error("Error when mapping columns KeyError " + str(e))
            else:
                columns = []
                for column, column_mapped in column_mapping.items():
                    if column in df.columns:
                        df = df.rename(columns={column: column_mapped})
                        columns.append(column_mapped)
                    else:
                        dat_logging.log_non_fatal_error("Column " + column + " does not exist in the .dat file's "
                                                        "columns or metadata columns. Mapping to partners column "
                                                        + column_mapped + " was not completed, and will not be included"
                                                        " in the final file.")
                df = df[columns]
    else:
        dat_logging.log_warning("No column mapping provided for destination file " + dest_dir)

    return df


def process_all_dats():
    dat_logging.log_info("Starting .dat file transfer to partner")
    partner_json_file = open("./partner_data.json")
    partner_json = json.load(partner_json_file)
    dat_files = glob.glob(dat_dir + "*.dat")
    station_metadata = pd.read_csv("station_metadata.csv")

    df_concat_15 = pd.DataFrame()
    df_concat_24 = pd.DataFrame()
    df_concat_60 = pd.DataFrame()

    # iterate through .dat files
    for dat_file in dat_files:
        try:
            df_stn = None
            dat_file_complete = dat_file
            print(dat_file_complete)

            # from the .dat file name find the matching station id
            # isolate the name of the station
            station_name = dat_file.split("\\")[-1][:-6]
            time_version = dat_file.split("\\")[-1][-6:-4]

            # ignoring files that are not in the format name24.dat, name60.dat, or name15.dat
            if time_version not in ["24", "60", "15"]:
                continue

            # find the station id from the name
            stn_id = station_metadata[station_metadata["DatFilename"] == station_name]["StnID"].values

            if len(stn_id) <= 0:
                stn_id = -1
            else:
                assert (len(stn_id) == 1)
                stn_id = stn_id[0]

            # iterate through the partner data and see if the current file is used anywhere
            for partner in partner_json:
                # check if we need to copy the files over to a specific partner
                if "copy_individual_stn_data" in partner_json[partner]:
                    df_stn = copy_individual_stn_data(partner_json[partner], dat_file_complete, df_stn, time_version)

            # all data gets added to the contacted file, given that we have a valid stnID
            if stn_id != -1:
                if df_stn is None:
                    df_stn = load_dat(dat_file_complete)

                if time_version == "15":
                    df_concat_15 = station_to_concat_file(df_concat_15, df_stn)
                elif time_version == "60":
                    df_concat_60 = station_to_concat_file(df_concat_60, df_stn)
                elif time_version == "24":
                    df_concat_24 = station_to_concat_file(df_concat_24, df_stn)

        except Exception as e:
            dat_logging.log_fatal_error("Unknown error caught when processing dat file " + dat_file + " Exception: "
                                        + str(e))
            continue

    # merge in canadian metadata
    df_concat_15 = post_processing_concat_file(df_concat_15, station_metadata)
    df_concat_60 = post_processing_concat_file(df_concat_60, station_metadata)
    df_concat_24 = post_processing_concat_file(df_concat_24, station_metadata)

    # check if partners need the concatenated file, move over data if necessary
    copy_concat_stn_data(df_concat_15, df_concat_60, df_concat_24, partner_json)
    dat_logging.log_info("Finished .dat file transfer to partner")


def main():
    start_time = time.time()
    tracemalloc.start()
    dat_logging.initialize_logger()
    with Profile() as profile:
        process_all_dats()
        (
            Stats(profile)
            .strip_dirs()
            .sort_stats("cumtime")
            .print_stats()
        )
    print("Successfully completed running program in", time.time() - start_time, "seconds, memory usage:",
          tracemalloc.get_traced_memory()[1] / (sys.getsizeof([]) * 1000000.0), "MB")
    tracemalloc.stop()


if __name__ == "__main__":
    main()
