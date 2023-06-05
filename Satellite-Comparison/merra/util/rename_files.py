import glob
import os

# files = glob.glob("../../../../../data/merra/M2T1NXSLV-2")
files = glob.glob("D:/data/merra/M2T1NXRAD/*.nc")

for file in files:
    new_name = file.replace("_401", "_400")
    os.rename(file, new_name)

