import datetime
import multiprocessing
import os
import re
import sys
import glob
import time
import json
import traceback
import tracemalloc
import shutil
import jsonschema.exceptions
import pandas as pd

from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_number
from dat_logging import Logger
from json_data_validator import JSONDataValidator

# directory of the .dat files where the incoming data is coming
# local testing
# dat_dir = "D:\\data\\remote_server_mock\\.dats\\"
# dest_dir = "D:\\data\\remote_server_mock\\.saved_data\\"
# prod file directories
dat_dir = "C:/Campbellsci/Dats/"
dest_dir = "C:/WWW/mbagweather.ca/www/Partners/"

logger = Logger()


# given a df and a dictionary of column to threshold mappings, apply the threshold to
# each column. If value is lower than the lower_threshold, then the substitution replaces
# the value
def apply_lower_thresholds(df, lower_thresholds, metadata_id, substitution="NaN"):
    if type(lower_thresholds) is not dict:
        logger.log_non_fatal_error("ID: " + metadata_id + " lower_thresholds was not a dictionary as expected. No "
                                   "lower thresholds are applied to the dataframe.")
        return df

    for column, lower_threshold in lower_thresholds.items():
        try:
            df[column] = df[column].mask(df[column] < lower_threshold, other=substitution)
        except KeyError as e:
            logger.log_warning("ID: " + metadata_id + " Key was not found in the dataframe and a lower threshold of "
                               "lower_threshold was not applied to column " + column + ". KeyError: " + str(e))
        except TypeError:
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
def apply_upper_thresholds(df, upper_thresholds, metadata_id, substitution="NaN"):
    if type(upper_thresholds) is not dict:
        logger.log_non_fatal_error("ID: " + metadata_id + " upper_thresholds was not a dictionary as expected. No "
                                   "upper thresholds are applied to the dataframe.")
        return df

    for column, upper_threshold in upper_thresholds.items():
        try:
            df[column] = df[column].mask(df[column] > upper_threshold, other=substitution)
        except KeyError as e:
            logger.log_warning("ID: " + metadata_id + " Key column was not found in the dataframe and a lower threshold"
                               " of lower_threshold was not applied to column " + column + ". KeyError: " + str(e))
        except TypeError:
            is_num_col = df[column].apply(is_number)
            df.loc[is_num_col, column] = df.loc[is_num_col, column].mask(df.loc[is_num_col, column] > upper_threshold,
                                                                         other=substitution)
            # Commented out logging upper/lower threshold removed data can trigger the warning
            # dat_logging.log_warning("ID: " + metadata_id + "Comparison with the type upper threshold is incompatible."
            #                         "Applying "
            #                         "threshold to all numerical values. Column: " + column + " TypeError: " + str(e))
    return df


def parse_transformation_string(df, column, transformation_string, metadata_id):
    # $ is an escape character
    if len(transformation_string) > 0 and transformation_string[0] == '$':
        transformation = transformation_string[1:].split("$")
        try:
            if transformation[0].upper() == "UPPERCASE":
                df[column] = df[column].str.upper()
        except KeyError as e:
            err_msg = metadata_id
            err_msg += " Column " + str(column) + " does not exist in data when applying transformation "
            err_msg += transformation_string + ". Transformation not applied."
            logger.log_non_fatal_error(err_msg)
    else:
        df[column] = transformation_string

    return df


# apply some transformation to the given df, based on a dictionary of column to transformation
# mappings. If the transformation is a string then all values are replaced with the string, if it
# is an int or float, then the transformation is multiplied to the column
def apply_transformations(df, transformations, metadata_id):
    for column, transformation in transformations.items():
        try:
            if type(transformation) is str:
                df = parse_transformation_string(df, column, transformation, metadata_id)
            elif type(transformation) is int or type(transformation) is float:
                if is_numeric_dtype(df[column]):
                    df[column] = df[column] * transformation
                else:
                    logger.log_warning("ID: " + metadata_id + " Found non numerical values when trying to apply a "
                                       "numerical transformation in column " + column + " applying transformation to"
                                       " all numerical data.")
                    is_num_col = df[column].apply(is_number)
                    df.loc[is_num_col, column] = df.loc[is_num_col, column] * transformation
            else:
                err_msg = metadata_id
                err_msg += " Unknown transformation done on column " + column
                logger.log_warning(err_msg)
        except KeyError as e:
            logger.log_non_fatal_error("ID: " + metadata_id + " Trying to apply transformation " + str(transformation) +
                                       " when column " + column + " doesnt exist. KeyError: " + str(e))
    return df


# In the df add quotes to the values of the columns listed in quoted_columns
def apply_quotes(df, quoted_columns):
    for column in quoted_columns:
        df[column] = '\"' + df[column] + '\"'
    return df


# Format the column to the specified format in df_metadata
def format_time_column(df, timestamp, df_metadata_dict, column, format_key, offset_key):
    try:
        if offset_key in df_metadata_dict:
            unit = df_metadata_dict[offset_key]["unit"]
            value = df_metadata_dict[offset_key]["value"]
            timedelta = pd.Timedelta(value=value, unit=unit)
            timestamp = timestamp + timedelta
    except ValueError as e:
        err_msg = "ID: " + df_metadata_dict["id"]
        err_msg += " There was an error in the time offset on column " + column
        err_msg += ". Transformation not applied, continuing."
        err_msg += " ValueError: " + str(e)
        logger.log_non_fatal_error(err_msg)

    try:
        if format_key in df_metadata_dict:
            df.loc[:, column] = timestamp.dt.strftime(df_metadata_dict[format_key])
        else:
            if column == "TIME":
                df.loc[:, "TIME"] = timestamp.dt.time
            elif column == "DATE":
                df.loc[:, column] = timestamp.dt.date
    except ValueError as e:
        logger.log_non_fatal_error("ID: " + df_metadata_dict["id"] + " An improper date format was given, "
                                   "ValueError: " + str(e))


# Formats all date columns in df based on df_metadata
def date_processing(df, df_metadata=None):
    if df_metadata is None:
        df_metadata = {}

    timestamp = pd.to_datetime(df["TMSTAMP"])

    format_time_column(df, timestamp, df_metadata, "DATE", "date_format", "date_offset")
    format_time_column(df, timestamp, df_metadata, "TIME", "time_format", "time_offset")
    format_time_column(df, timestamp, df_metadata, "TMSTAMP", "timestamp_format", "timestamp_offset")

    return df


# apply thresholds and transformations to df
def df_data_operations(df, df_metadata):
    if "lower_thresholds" in df_metadata:
        lower_threshold = df_metadata["lower_thresholds"]
        if "substitution_value" in df_metadata:
            df = apply_lower_thresholds(df, lower_threshold, df_metadata["id"], substitution=df_metadata["substitution_value"])
        else:
            df = apply_lower_thresholds(df, lower_threshold, df_metadata["id"])
    if "upper_thresholds" in df_metadata:
        upper_threshold = df_metadata["upper_thresholds"]
        if "substitution_value" in df_metadata:
            df = apply_upper_thresholds(df, upper_threshold, df_metadata["id"], substitution=df_metadata["substitution_value"])
        else:
            df = apply_upper_thresholds(df, upper_threshold, df_metadata["id"])
    if "transformations" in df_metadata:
        transformations = df_metadata["transformations"]
        df = apply_transformations(df, transformations, df_metadata["id"])
    # pandas automatically adds triple quotes, undesired effect
    if "quoted_columns" in df_metadata:
        quoted_columns = df_metadata["quoted_columns"]
        df = apply_quotes(df, quoted_columns)
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

        if check_run_time_regex(version_data) and dat_file in mapped_dat_files:
            if "direct_copy" not in version_data or not version_data["direct_copy"]:
                if df_stn is None:
                    df_stn = load_dat(dat_file_full)
                df_processed = df_stn.copy()

                if "previous_rows" in version_data:
                    previous_rows = version_data["previous_rows"]
                else:
                    previous_rows = "all"

                if "StationName" in df_processed.columns:
                    df_processed = df_processed.sort_values(["StationName", "TMSTAMP"])
                else:
                    df_processed = df_processed.sort_values(["TMSTAMP"])

                df_processed = non_sparce_time_processing(df_processed, version_data)
                df_processed = date_processing(df_processed, version_data)
                df_processed = df_data_operations(df_processed, version_data)

                if previous_rows != "all" and type(previous_rows) is int:
                    df_processed = df_processed.groupby("StnID").tail(previous_rows)

                df_processed = column_formatting(df_processed, version_data)
                df_processed = process_column_mapping(df_processed, version_data, dat_file)

                destination_file = dest_dir + partner_data["base_directory"] + "/" + mapped_dat_files[dat_file]
                df_processed = merge_retention_data(df_processed, version_data, destination_file)
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


# a more precise but slow way to format a column
def process_row(value, format_str):
    if isinstance(value, float):
        if pd.isna(value):
            return ""
        value = format_str.format(value)
        return value
    else:
        return ""


# apply special formatting to the columns to truncate decimals or add trailing zeros
def column_formatting(df, metadata):
    if "column_format" in metadata:
        for column, formatting in metadata["column_format"].items():
            try:
                df[column] = df[column].apply(lambda row: process_row(row, formatting))
            except ValueError as e:
                logger.log_warning("ID: " + metadata["id"] + " Error in the value of the string format ValueError: "
                                   + str(e))
                df[column] = df[column].astype(float)
                df[column] = df[column].apply(lambda row: process_row(row, formatting))
            except IndexError as e:
                logger.log_non_fatal_error("ID: " + metadata["id"] + " Column does not exist when trying to apply"
                                                                     " string formatting: " + str(e))
            except KeyError as e:
                logger.log_non_fatal_error("ID: " + metadata["id"] + " Column does not exist when trying to apply"
                                                                     " string formatting: " + str(e))
    return df


# process the concatenated data to be as specified for an individual partner
def process_concat_data(df, metadata, base_directory, destination_file):
    if "previous_rows" in metadata:
        previous_rows = metadata["previous_rows"]
    else:
        previous_rows = "all"

    stations = metadata["stations"]

    df = df[df["StnID"].isin(stations)]

    if "StationName" in df.columns:
        df = df.sort_values(["StationName", "TMSTAMP"])
    else:
        df = df.sort_values(["TMSTAMP"])

    # TODO check if all of these .copy()s are necessary
    df = non_sparce_time_processing(df.copy(), metadata)
    df = date_processing(df.copy(), metadata)
    df = df_data_operations(df.copy(), metadata)

    if previous_rows != "all" and type(previous_rows) is int:
        df = df.groupby("StnID").tail(previous_rows)

    df = column_formatting(df, metadata)
    df = process_column_mapping(df, metadata)

    destination_file = dest_dir + base_directory + "/" + destination_file
    df = merge_retention_data(df, metadata, destination_file)

    return df


# Add a custom header to a partners file
def add_header(metadata, partner, dest_file):
    src_file = "./partner_headers/" + partner + "/" + metadata["header"]
    try:
        shutil.copy(src_file, dest_file)
    except FileNotFoundError as e:
        logger.log_non_fatal_error("ID: " + metadata["id"] + " No header file found, default header used"
                                   " FileNotFoundError: " + str(e))
        return False
    return True


# Future work: Could add options to control how NaN values are deliverd to partners
def get_partner_index_cols_names(metadata):
    if "column_mapping" in metadata:
        col_map = metadata["column_mapping"]
        return [col_map["TMSTAMP"], col_map["StnID"]]
    else:
        return ["TMSTAMP", "StnID"]


def read_partner_data(metadata, dest_file):
    sep = ","
    skip_rows = []
    columns = list(metadata["column_mapping"].values())

    if "csv_deliminator" in metadata:
        sep = metadata["csv_deliminator"]
    if "skip_rows" in metadata:
        skip_rows = metadata["skip_rows"]

    df = pd.read_csv(dest_file,
                     sep=sep,
                     skiprows=skip_rows,
                     header=None,
                     names=columns,
                     na_values=["", "nan"],
                     encoding='unicode_escape')

    partner_metadata = metadata
    if "column_format" in partner_metadata:
        for column in metadata["column_mapping"]:
            if column in partner_metadata["column_format"]:
                partner_col = partner_metadata["column_mapping"][column]
                previous_col_format = partner_metadata["column_format"][column]
                del partner_metadata["column_format"][column]
                partner_metadata["column_format"][partner_col] = previous_col_format

    df = column_formatting(df, partner_metadata)
    return df


def merge_retention_data(dats_df, metadata, dest_file):
    if "retain_data" in metadata and metadata["retain_data"]:
        if os.path.isfile(dest_file):
            partner_df = read_partner_data(metadata, dest_file)
            concatenated_df = pd.concat([partner_df, dats_df])
            index_cols = get_partner_index_cols_names(metadata)
            concatenated_df = concatenated_df.drop_duplicates(keep="last", subset=index_cols)

            if "TMSTAMP" in index_cols:
                concatenated_df["date_col"] = pd.to_datetime(concatenated_df["TMSTAMP"])
                index_cols.remove("TMSTAMP")
                index_cols.append("date_col")
                sorted_df = concatenated_df.sort_values(index_cols, ascending=True)
                sorted_df = sorted_df.drop(columns="date_col")
            else:
                sorted_df = concatenated_df.sort_values(index_cols, ascending=True)
            return sorted_df
        else:
            logger.log_warning("ID: " + metadata["id"] + " Could not find partner file " + dest_file +
                               ", starting a new file with the current dat.")
            return dats_df
    else:
        return dats_df


# save a df to the destination_file
def save_df(df, metadata, base_directory, destination_file_suffix):
    destination_file = dest_dir + base_directory + "/" + destination_file_suffix
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
        # ඞ is arbitrarily chosen as the quote char. A character which should not be used should be used in the partner
        # file
        df.to_csv(destination_file, index=False, sep=delimiter, header=header, mode=mode, quotechar="ඞ",
                  doublequote=False)
        print("Saving df to ", destination_file)
    except OSError as e:
        logger.log_fatal_error("ID: " + metadata["id"] + " OSError when saving to file " + destination_file +
                               " OSError: " + str(e))


def get_concat_data_destination_file(metadata):
    # For whatever reason they have both, destination_file takes precedent
    if "destination_file" in metadata:
        return metadata["destination_file"]
    elif "new_file_daily" in metadata and metadata["new_file_daily"]:
        curr_date = datetime.datetime.now()
        yesterday_date = curr_date - datetime.timedelta(days=1)
        destination_file = str(yesterday_date.date()) + ".txt"
        return destination_file
    else:
        raise KeyError("Did not find destination_file or new_file_daily in the partner file")


# go through metadata related to concatenated data
def iterate_concat_data(df_concat, version_metadata, base_directory):
    if type(version_metadata) is list:
        for request in version_metadata:
            if check_run_time_regex(request):
                destination_file = get_concat_data_destination_file(request)
                logger.log_info("Saving file " + destination_file + " to partner " + base_directory)
                df = process_concat_data(df_concat.copy(), request, base_directory, destination_file)
                save_df(df, request, base_directory, destination_file)
    elif type(version_metadata) is dict:
        if check_run_time_regex(version_metadata):
            destination_file = get_concat_data_destination_file(version_metadata)
            logger.log_info("Saving file " + destination_file + " to partner " + base_directory)
            df = process_concat_data(df_concat.copy(), version_metadata, base_directory, destination_file)
            save_df(df, version_metadata, base_directory, destination_file)
    else:
        logger.log_non_fatal_error("Unknown data when parsing the version meta data "
                                   "for " + base_directory + ". Skipping copying this data")


# take the concatenated data and process it based on partner specification
def copy_concat_stn_data(df_concat_15, df_concat_60, df_concat_24, partners_json):
    # Prod has 4 virtual threads, but since there is a large amount of IO operations which would
    # be halting, 6 workers may still be beneficial
    num_processes = 4
    tasks = []
    with multiprocessing.Pool(num_processes) as pool:
        for partner_json in partners_json:
            if "copy_concatenated_stn_data" in partner_json:
                base_dir = partner_json["base_directory"]
                concat_data = partner_json["copy_concatenated_stn_data"]

                if "15" in concat_data:
                    tasks.append((iterate_concat_data, (df_concat_15, concat_data["15"], base_dir)))
                if "60" in concat_data:
                    tasks.append((iterate_concat_data, (df_concat_60, concat_data["60"], base_dir)))
                if "24" in concat_data:
                    tasks.append((iterate_concat_data, (df_concat_24, concat_data["24"], base_dir)))

        results = [pool.apply_async(pool_calculation, task) for task in tasks]
        for result in results:
            try:
                result.get(timeout=180)
            except multiprocessing.TimeoutError as e:
                logger.log_non_fatal_error("Timed out when waiting for multi-threading to wait for a response "
                                           "TimeoutError: " + str(e))
            except Exception as e:
                stack_trace = ''.join(traceback.TracebackException.from_exception(e).format())
                logger.log_non_fatal_error("Unknown multithreading error occurred attempting to continue. "
                                           "Error message: " + str(e) + "\n" + stack_trace)


# load a dat file, only read 2nd of 2 headers
def load_dat(filename):
    return pd.read_csv(filename, header=1)


# merge metadata into station data
def post_processing_concat_file(df, station_metadata):
    df = df.merge(station_metadata, how="left", on=["StnID"])
    return df


# based on partner data, check if the current date matches the run_time_regex
def check_run_time_regex(version_metadata):
    current_date = str(datetime.datetime.now())
    if "run_time_regex" in version_metadata:
        run_time_regex = version_metadata["run_time_regex"]
        return bool(re.search(run_time_regex, current_date))
    else:
        return True


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
                logger.log_non_fatal_error("ID: " + metadata["id"] + " Error when mapping columns KeyError " + str(e))
            else:
                columns = []
                for column, column_mapped in column_mapping.items():
                    if column in df.columns:
                        df = df.rename(columns={column: column_mapped})
                        columns.append(column_mapped)
                    else:
                        logger.log_non_fatal_error("ID: " + metadata["id"] + " Column " + column + " does not exist in "
                                                   "the .dat file's columns or metadata columns. Mapping to partners "
                                                   "column " + column_mapped + " was not completed, and will not "
                                                   "be included in the final file.")
                df = df[columns]
    else:
        logger.log_warning("ID: " + metadata["id"] + " No column mapping provided for destination file " + dest_dir)

    return df


def non_sparce_time_processing(df, metadata):
    if "non_sparce_time" in metadata and metadata["non_sparce_time"] is True:
        # get current date, rounded to the hour
        current_time = datetime.datetime.now()
        current_time = current_time.replace(minute=0, second=0, microsecond=0)

        # get unique station IDs from df
        df_stn_data = df[["StnID", "StationName", "LatDD", "LongDD", "URL"]]
        df_stn_data = df_stn_data.drop_duplicates()

        df_recorded = df.drop(columns=["StationName", "LatDD", "LongDD", "URL"])

        # get station metadata and merge in the time to create a non-sparce indexed dataframe with no data
        df_stn_data["TMSTAMP"] = str(current_time)

        # merge in the data
        df_merged = df_stn_data.merge(df_recorded, how="left", on=["TMSTAMP", "StnID"])
        df_merged = df_merged.fillna("")

        return df_merged
    else:
        return df


def return_single_valid_dat(stn_id, df_stn, dat_file_complete, time_version):
    # all data gets added to the contacted file, given that we have a valid stnID
    if stn_id != -1:
        if df_stn is None:
            df_stn = load_dat(dat_file_complete)

        return df_stn, time_version


# Given a single dat_file read it and then apply appropriate processing,
# then copying the single file to partners if the partner json says that
# it is required
# returning None indicates that the loop should continue, otherwise returns
# a tuple of the df (dat file -> df) and the time version (15, 60, 24)
def process_single_dat(partners_json, station_metadata, dat_file):
    df_stn = None
    dat_file_complete = dat_file

    # from the .dat file name find the matching station id
    # isolate the name of the station
    station_name = dat_file.split("\\")[-1][:-6]
    time_version = dat_file.split("\\")[-1][-6:-4]

    # ignoring files that are not in the format name24.dat, name60.dat, or name15.dat
    if time_version not in ["24", "60", "15"]:
        return None

    # find the station id from the name
    station_metadata["DatFilename"] = station_metadata["DatFilename"].str.lower()
    stn_id = station_metadata[station_metadata["DatFilename"] == station_name.lower()]["StnID"].values

    if len(stn_id) <= 0:
        stn_id = -1
    else:
        assert (len(stn_id) == 1)
        stn_id = stn_id[0]

    try:

        # iterate through the partner data and see if the current file is used anywhere
        for partner_json in partners_json:
            # check if we need to copy the files over to a specific partner
            if "copy_individual_stn_data" in partner_json:
                df_stn = copy_individual_stn_data(partner_json, dat_file_complete, df_stn, time_version)

        return return_single_valid_dat(stn_id, df_stn, dat_file_complete, time_version)

    except Exception as e:
        stack_trace = ''.join(traceback.TracebackException.from_exception(e).format())
        logger.log_fatal_error("Unknown error caught when processing dat file " + dat_file + " Exception: "
                               + str(e).replace("\n", "") + stack_trace)

        # Want to still return a value for the concatenated processing
        return return_single_valid_dat(stn_id, df_stn, dat_file_complete, time_version)


# simple bootstrap which can be used by pool workers
def pool_calculation(func, args):
    return func(*args)


def validate_partner_data():
    for partner_file in glob.glob("./partner_data/*.json"):
        try:
            partner_validator = JSONDataValidator(partner_file, "./partner_data/schemas/sub_schemas/*.json", "./partner_data/schemas/partner_file_specs_schema.json")
            partner_validator.validate_data()
        except jsonschema.exceptions.ValidationError as e:
            error_message = "JSON validator failed when validating the " + partner_file
            error_message += " partner json file. Continuing with operation, although errors may occur. "
            error_message += " Error Message: " + e.message
            logger.log_non_fatal_error(error_message)
        except json.decoder.JSONDecodeError as e:
            error_message = "There is a JSON encoding error with loading the schema. JSON validation for "
            error_message += partner_file + " skipped. "
            error_message += "Error: " + str(e)
            logger.log_non_fatal_error(error_message)
            continue


def process_all_dats():
    list_concat_15 = []
    list_concat_60 = []
    list_concat_24 = []

    # Check if there are formatting issues with the partner_jsons before running
    validate_partner_data()

    # Prod has 4 virtual threads, but since there is a large amount of IO operations which would
    # be halting, 6 workers may still be beneficial.
    num_processes = 4
    with multiprocessing.Pool(num_processes) as pool:
        logger.log_info("Starting .dat file transfer to partner")

        # create a list of the partner_data files
        partner_files = glob.glob("./partner_data/*.json")
        partners_json = []

        for partner_file in partner_files:
            try:
                partner_json_file = open(partner_file)
                partner_json_data = json.load(partner_json_file)
                if "run_partner" not in partner_json_data or partner_json_data["run_partner"]:
                    partners_json.append(partner_json_data)
            except json.decoder.JSONDecodeError as e:
                logger.log_fatal_error("Error decoding the JSON file, partner_data.json. Please verify that "
                                       "partner_data.json has the correct formatting. Error: " + e.msg)
                continue

        dat_files = glob.glob(dat_dir + "*.dat")
        station_metadata = pd.read_csv("station_metadata.csv")

        # create a task for each dat file. This is prepping for the multithreading
        # which will send workers to then process each individual dat file
        tasks = [(process_single_dat, (partners_json, station_metadata, dat_file)) for dat_file in dat_files]
        results = [pool.apply_async(pool_calculation, task) for task in tasks]

        # iterate through the result of the workers and merge data
        # order does not matter, thus we can use apply_async safely
        for result in results:
            try:
                result = result.get(timeout=60)
                if result is not None:
                    df_stn = result[0]
                    time_version = result[1]
                    if time_version == "15":
                        list_concat_15.append(df_stn)
                    elif time_version == "60":
                        list_concat_60.append(df_stn)
                    elif time_version == "24":
                        list_concat_24.append(df_stn)
            except multiprocessing.TimeoutError as e:
                logger.log_non_fatal_error("Timed out when waiting for multi-threading to wait for a response "
                                           "TimeoutError: " + str(e))
            except Exception as e:
                stack_trace = ''.join(traceback.TracebackException.from_exception(e).format())
                logger.log_non_fatal_error("Unknown multithreading error occurred attempting to continue. "
                                           "Error message: " + str(e) + "\n" + stack_trace)

    # create single concatenated df based off of the individual dat dfs
    df_concat_15 = pd.concat(list_concat_15)
    df_concat_60 = pd.concat(list_concat_60)
    df_concat_24 = pd.concat(list_concat_24)

    # merge in station metadata
    df_concat_15 = post_processing_concat_file(df_concat_15, station_metadata)
    df_concat_60 = post_processing_concat_file(df_concat_60, station_metadata)
    df_concat_24 = post_processing_concat_file(df_concat_24, station_metadata)

    # check if partners need the concatenated file, move over data if necessary
    copy_concat_stn_data(df_concat_15, df_concat_60, df_concat_24, partners_json)
    logger.log_info("Finished .dat file transfer to partner\n")


def main():
    start_time = time.time()
    tracemalloc.start()
    try:
        process_all_dats()
    except Exception as e:
        logger.log_fatal_error("Found uncaught error with unknown consequences. Prematurely exiting program. " + str(e))
        print(traceback.format_exc())
        exit(1)

    print("Successfully completed running program in", time.time() - start_time, "seconds, memory usage:",
          tracemalloc.get_traced_memory()[1] / (sys.getsizeof([]) * 1000000.0), "MB")
    tracemalloc.stop()


if __name__ == "__main__":
    main()
