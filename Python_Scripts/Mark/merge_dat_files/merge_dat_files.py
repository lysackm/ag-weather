import glob
import os

import pandas as pd


# This removes the first line of all files in the directory ./dat_files where ever this program is.
# This change is permanent to the files, only run once or else you will start deleting data from the files.
def remove_first_header(input_dir):
    print("Removing the first lines of files that have two headers \n")

    files = glob.glob(input_dir + "/*.dat")
    for file in files:
        with open(file, 'r') as fin:
            data = fin.read().splitlines(True)

        if "TOACI1" in data[0]:
            if "TMSTAMP" in data[3]:
                with open(file, 'w') as fout:
                    fout.writelines(data[3:])
            else:
                with open(file, 'w') as fout:
                    fout.writelines(data[1:])


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

    files = glob.glob(input_dir + "/*.dat")

    # add new appended files
    for file in files:
        df = pd.read_csv(file)

        dat_index = file.index(".dat")
        stn_name = file[:dat_index].replace(input_dir + "\\", "")

        output_file = "output/" + stn_name + ".dat"

        df = df.round(5)
        df.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

    files = glob.glob("output/*.dat")

    delete_duplicates = input("Do you want to delete duplicates in the files? Yes or y to delete duplicates. No to not: ")

    if delete_duplicates.lower() == "yes" or delete_duplicates.lower() == "y":
        print("Deleting duplicate values \n")
        for file in files:
            df = pd.read_csv(file)
            df.drop_duplicates(inplace=True)
            df.to_csv(file, index=False)
    else:
        print("Not deleting duplicate values \n")

    sort_values = input("Do you want to sort the values in the files? Yes or y to sort. No to not: ")

    if sort_values.lower() == "yes" or sort_values.lower() == "y":
        print("Sorting values")
        # sort files
        for file in files:
            df = pd.read_csv(file)
            df = df.sort_values(by=["TMSTAMP"])
            df.to_csv(file, index=False)

    print("program finished successfully (yay). Check the ./output directory")


def main():
    print("Hello! This is Marks program to merge together multiple csv files into one single csv. \n"
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
        remove_first_header(input_dir)
        merge_files(input_dir)
    except Exception as e:
        print("Encountered an error during the running of the program. Did not finish successfully.")
        print(e)
        exit(1)


main()
