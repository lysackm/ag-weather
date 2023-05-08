import pandas
from config import temp_folder
from util import try_delete, file_exists

# files that weren't able to be inserted into database with cleaner
def run():
    # 24 hr paths
    paths_24 = [
        f"{temp_folder}/2008/carman24.txt",
        f"{temp_folder}/2009/carman24.txt",
        f"{temp_folder}/2010/carman24.txt"
    ]

    # 60 min paths
    paths_60 = [
        f"{temp_folder}/2008/carman60.txt",
        f"{temp_folder}/2009/carman60.txt",
        f"{temp_folder}/2010/carman60.txt"
    ]

    car_24_cols_to_drop = [
        "AvgSoilT_10",
        "MaxSoil_T10",
        "MinSoil_T10",
        "AvgAir_T2",
        "MaxAir_T2",
        "HmMaxAir_T2",
        "MinAir_T2",
        "HmMinAir_T2",
        "AvgRH2",
        "MaxRH2",
        "HmMaxRH2",
        "MinRH2",
        "HmMinRH2"
    ]

    car_60_cols_to_drop = [
        "Soil_T10",
        "Air_T2",
        "AvgAir_T2",
        "MaxAir_T2",
        "MinAir_T~2",
        "RH2",
        "AvgRH2"
    ]

    for path in paths_24:
        if not file_exists(path):
            continue
        try:
            # read into dataframe
            df = pandas.read_csv(path, skiprows=1)

            # rename column Rain -> Pluvio_Rain
            df = df.rename(columns={"Rain": "Pluvio_Rain"})

            # delete extra columns
            df = df.drop(columns=car_24_cols_to_drop)

            # write the file back
            df.to_csv(path, index=False)
        except:
            print(f"Error cleaning old Carman 24 file {path}. File ignored.")
            try_delete(path, "couldn't clean old carman 24 file")

    for path in paths_60:
        if not file_exists(path):
            continue
        try:
            # read into dataframe
            df = pandas.read_csv(path, skiprows=1)

            # rename columns
            df = df.rename(columns={"Rain": "Pluvio_Rain", "Rain24RT": "Pluvio_Rain24RT", "WD _2Min": "WD_2Min"})

            # delete extra columns
            df = df.drop(columns=car_60_cols_to_drop)

            # write the file back
            df.to_csv(path, index=False)
        except:
            print(f"Error cleaning old Carman 60 file {path}. File ignored.")
            try_delete(path, "couldn't clean old carman 60 file")

