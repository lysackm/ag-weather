from util import each_file, rename, file_exists, drop_prefix, delete, file_empty
from config import temp_folder, consec_folder, merge_temp_folder
import pandas
import os
import log

# merges two data files and overwrites the first file
def merge_data_files(path_to_overwrite, path_other):
    # load the files into dataframes
    frames = [pandas.read_csv(path_to_overwrite), pandas.read_csv(path_other)]

    # merge data into one dataframe
    df = pandas.concat(frames)

    # sort the dataframe by TMSTAMP
    df = df.sort_values(by=["TMSTAMP"])

    # remove any duplicate rows
    df = df.drop_duplicates()

    # save the file back to the path we want to overwrite
    df.to_csv(path_to_overwrite, index=False, header=True)

# this function takes every cleaned data file in
def run():
    log.main("merge cleaned data")

    # delete all empty files in consecutive folder
    for path in each_file(consec_folder):
        if file_empty(path):
            delete(path)

    for path in each_file(merge_temp_folder):
        if file_empty(path):
            delete(path)
            continue

        # remove the directory info to get just the filename and extension
        filename = drop_prefix(path, merge_temp_folder + os.path.sep)
        has_txt_extension = filename.endswith(".txt")
        has_dat_extension = filename.endswith(".dat")

        # if path doesnt have .txt or .dat extension, delete and raise an exception
        # definitely should never happen by the time this function is called
        if not (has_txt_extension or has_dat_extension):
            raise Exception("Invalid data in temp folder after data insertion")

        # get the name of what the corresponding txt/dat file would be in consecutive folder
        if has_txt_extension:
            corresponding_txt = os.path.join(consec_folder, filename)
            corresponding_dat = corresponding_txt.replace("txt", "dat")
        else:
            # has dat extension
            corresponding_dat = os.path.join(consec_folder, filename)
            corresponding_txt = corresponding_dat.replace("dat", "txt")

        # booleans that hold whether corresponding txt/dat files exist
        txt_exists = file_exists(corresponding_txt)
        dat_exists = file_exists(corresponding_dat)

        # if both exist, merge them into the txt and delete the dat
        if txt_exists and dat_exists:
            merge_data_files(corresponding_txt, corresponding_dat)
            delete(corresponding_dat)

        # get the corresponding path if it exists
        # corresponding path is the path to the file that will store data until consecutive value checking is performed
        if txt_exists:
            corresponding_path = corresponding_txt
        elif dat_exists:
            corresponding_path = corresponding_dat
        else:
            corresponding_path = None

        # corresponding file doesn't exist, so just move current file there as a txt file
        if corresponding_path is None:
            rename(path, corresponding_txt)
        else:
            # if the corresponding file exists,
            # merge the data from the files and overwrite corresponding file
            merge_data_files(corresponding_path, path)