import glob
import os
import re

# to go through the files downloaded via wget
# and rename then to be manageable for further parsing

# had to change the directory file from merra_temp_1993-2023 to merra
# because windows only allows for files with 260 characters
# won't work in its current state
data_dir = "D:/merra/merra/"


def main():
    files = os.listdir(data_dir)

    for file in files:
        try:
            new_name = data_dir + re.findall(r"tavg1_2d_slv_Nx\.[0-9]{8}\.nc4", file)[0]

            os.rename(data_dir + file, new_name)
        except Exception as e:
            print("Encountered error while renaming files, exiting")
            print(e)
            exit()


if __name__ == "__main__":
    main()
