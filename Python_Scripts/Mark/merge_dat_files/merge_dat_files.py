import glob
import os
import csv
import traceback

import pandas as pd


# creates copies of the files to be worked on. This is so that the original files will not be modified,
# and the original data can be restored if necessary. Clones the files with the last characters being
# <original_file_name>_working.dat, with the original .dat being replaced by _working.dat
def create_working_files(input_dir):
    files = glob.glob(input_dir + "/**/*.dat") + glob.glob(input_dir + "/*.dat")
    for file in files:
        with open(file, 'r') as fin:
            data = fin.read().splitlines(True)

        file_working = file.replace(".dat", "_working.dat")

        with open(file_working, 'w') as fout:
            fout.writelines(data)


# deletes working files created
def remove_working_files(input_dir):
    files = glob.glob(input_dir + "/**/*_working.dat") + glob.glob(input_dir + "/*_working.dat")
    for file in files:
        try:
            os.remove(file)
        except FileExistsError:
            print("No file to delete, continuing")
        except Exception as e:
            print("Ran into an unexpected error trying to delete the working files,"
                  " possibly that you dont have permissions to delete files")
            print("Exception: ", e)
            print("Continuing, non lethal error")


# given a file name and input directory, return the station name and hour it is
def get_stn_name(file, input_dir):
    dat_index = file.index(".dat")
    dir_and_stn_name = file[:dat_index].replace(input_dir + "\\", "")
    try:
        dir_index = dir_and_stn_name.index("\\")
        stn_name = dir_and_stn_name[(dir_index + 1):].replace("_working", "")
    except ValueError:
        stn_name = dir_and_stn_name.replace("_working", "")

    return stn_name


# This removes the first line of all files in the directory ./dat_files where ever this program is.
def remove_first_header(input_dir):
    print("Removing the first lines of files that have two headers \n")

    files = glob.glob(input_dir + "/**/*_working.dat") + glob.glob(input_dir + "/*_working.dat")
    for file in files:
        with open(file, 'r') as fin:
            data = fin.read().splitlines(True)

        # should change this to modify a different file
        if "TOACI1" in data[0]:
            if "TMSTAMP" in data[3]:
                with open(file, 'w') as fout:
                    fout.writelines(data[3:])
            else:
                with open(file, 'w') as fout:
                    fout.writelines(data[1:])

        elif "TMSTAMP" not in data[0]:
            stn_name = get_stn_name(file, input_dir)
            header_line = ""

            if "15" in stn_name:
                header_line = '"TMSTAMP","RECNBR","StnID","Air_T","RH","Pluvio_Rain","AvgWS","AvgWD","AvgSD","TBRG_Rain","MaxWS","Press_hPa"\n'
            elif "24" in stn_name:
                header_line = '"TMSTAMP","RECNBR","StnID","BatMin","ProgSig","AvgAir_T","MaxAir_T","HmMaxAir_T","MinAir_T","HmMinAir_T","AvgRH","MaxRH","HmMaxRH","MinRH","HmMinRH","Pluvio_Rain","MaxWS","HmMaxWS","AvgWS","AvgWD","AvgSD","AvgSoil_T05","MaxSoil_T05","MinSoil_T05","AvgRS_kw","MaxRS_kw","HmMaxRS","TotRS_MJ","TBRG_Rain","Avg_Soil_TP5_TempC","Max_Soil_TP5_TempC","Min_Soil_TP5_TempC","Avg_Soil_TP5_VMC","Max_Soil_TP5_VMC","Min_Soil_TP5_VMC","Avg_Soil_TP20_TempC","Max_Soil_TP20_TempC","Min_Soil_TP20_TempC","Avg_Soil_TP20_VMC","Max_Soil_TP20_VMC","Min_Soil_TP20_VMC","Avg_Soil_TP50_TempC","Max_Soil_TP50_TempC","Min_Soil_TP50_TempC","Avg_Soil_TP50_VMC","Max_Soil_TP50_VMC","Min_Soil_TP50_VMC","Avg_Soil_TP100_TempC","Max_Soil_TP100_TempC","Min_Soil_TP100_TempC","Avg_Soil_TP100_VMC","Max_Soil_TP100_VMC","Min_Soil_TP100_VMC","EvapTot24"\n'
            elif "60" in stn_name:
                header_line = '"TMSTAMP","RECNBR","StnID","BatMin","Air_T","AvgAir_T","MaxAir_T","MinAir_T","RH","AvgRH","Pluvio_Rain","Pluvio_Rain24RT","WS_10Min","WD_10Min","AvgWS","AvgWD","AvgSD","MaxWS_10","MaxWD_10","MaxWS","HmMaxWS","MaxWD","Max5WS_10","Max5WD_10","WS_2Min","WD_2Min","Soil_T05","AvgRS_kw","TotRS_MJ","TBRG_Rain","TBRG_Rain24RT","Soil_TP5_TempC","Soil_TP5_VMC","Soil_TP20_TempC","Soil_TP20_VMC","Soil_TP50_TempC","Soil_TP50_VMC","Soil_TP100_TempC","Soil_TP100_VMC","Evap60","SolarRad","Press_hPa"\n'
            else:
                print("File " + file + " does not have a header, and the correct header for this file is ambiguous. Exiting \n")
                exit(1)

            insert_header = input("File " + file + " does not have a header, type y or yes to insert the header \n" + header_line
                                  )

            if insert_header.lower() == "yes" or insert_header.lower() == "y":
                with open(file, "w") as fout:
                    print("data", data)
                    fout.writelines([header_line] + data)
            else:
                print("cleaning working files and exiting. Cannot continue")
                remove_working_files(input_dir)
                exit()


# round each column of the output by a given amount
def round_columns():
    files = glob.glob("output/*.dat")

    columns = {
        "Air_T": 3,
        "RH": 1,
    }

    # for file in files:


# merge_files will run through all the files in the directory ./dat_files
# and concatenate the files into one file if they
# have the same suffix (ex. altona15.dat and altona15.datx)
# Output is in the directory ./output where ever this file is ran.
# You will need read/write access for the folder where this is ran.
def merge_files(input_dir):
    files = glob.glob("output/*.dat")
    # clean ./output
    for file in files:
        try:
            os.remove(file)
        except FileExistsError:
            print("No file to delete, continuing")

    files = glob.glob(input_dir + "/**/*_working.dat") + glob.glob(input_dir + "/*_working.dat")

    # add new appended files
    for file in files:
        df = pd.read_csv(file)

        stn_name = get_stn_name(file, input_dir)

        output_file = "output/" + stn_name + ".dat"

        df = df.round(5)
        df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    files = glob.glob("output/*.dat")

    delete_duplicates = input(
        "Do you want to delete duplicates in the files? Yes or y to delete duplicates. No to not: ")

    if delete_duplicates.lower() == "yes" or delete_duplicates.lower() == "y":
        print("Deleting duplicate values \n")
        for file in files:
            df = pd.read_csv(file)
            df.drop_duplicates(inplace=True)
            df.to_csv(file, index=False)
    else:
        print("Not deleting duplicate values \n")

    sort_values = input("Do you want to sort the values by date in the files? Yes or y to sort. No to not: ")

    if sort_values.lower() == "yes" or sort_values.lower() == "y":
        print("Sorting values by date")
        # sort files
        for file in files:
            df = pd.read_csv(file)
            df = df.sort_values(by=["TMSTAMP"])
            df.to_csv(file, index=False)
    else:
        print("Not sorting values by date \n")

    quote_dates = input("Do you want your dates formatted with or without quotes? Ex \"2023-11-01 00:15:00\" compared "
                        "to 2023-11-01 00:15:00. Yes or y for quotes, No to not: ")

    if quote_dates.lower() == "yes" or quote_dates.lower() == "y":
        print("Adding quotes to dates")
        # sort files
        for file in files:
            df = pd.read_csv(file)
            df["TMSTAMP"] = df["TMSTAMP"].astype(str)
            df.to_csv(file, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    else:
        print("Not adding quotes to dates\n")

    print("program finished successfully (yay). Check the ./output directory")


def main():
    print("Hello! This is Mark\'s program to merge together multiple csv files into one single csv. \n"
          "The normal way to run this program is to have two sub directories where this program is placed, \n"
          "one called output, and one called dat_files. dat_files contains the raw .dat files. output is \n"
          "the directory that contains the output after the program ran.\n"
          "It also rounds all numbers to 5 digits, removes duplicates, and sorts the output. \n")
    print("First make sure that this program is being ran in the right spot.")

    if os.path.isdir("output"):
        print("Found the directory './output'. This where the output files will be placed.")
    else:
        try:
            os.mkdir("./output")
        except:
            print("Cannot find the directory './output', exiting. Create the directory output where this file is"
                  "and run the program again. No files were modified or created.")
            exit(1)

    input_dir = "dat_files"
    if os.path.isdir(input_dir):
        print("Found the directory dat_files will use the files in that location.")
    else:
        while not os.path.isdir(input_dir):
            input_dir = input(input_dir + " is not an existing directory. If there is a different directory you want "
                                          "to use that contains the files used for input?"
                                          " exit to quit. \nType new directory or exit: ")
            if input_dir.lower() == "exit":
                print("Exiting program.")
                exit(1)

    try:
        remove_working_files(input_dir)
        create_working_files(input_dir)
        remove_first_header(input_dir)
        merge_files(input_dir)
        # round_columns()
        remove_working_files(input_dir)
    except Exception as e:
        print("Encountered an error during the running of the program. Did not finish successfully.")
        print(e)
        traceback.print_exc()
        exit(1)


main()
