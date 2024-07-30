import glob
import time
import pandas as pd

# directory of the .dat files where the incoming data is coming
# dat_dir = "../../../data/remote_server_mock/.dats/"
# dest_dir = "../../../data/remote_server_mock/.saved_data/"
dat_dir = ""
dest_dir = "C:\\WWW\\mbagweather.ca\\www\\Partners\\"


# Test how long it takes to load the .dat files into a
# pandas dataframe
def benchmark_pandas_load():
    files = glob.glob(dat_dir + "*.dat")
    start_time = time.time()

    for file in files:
        print(file)
        pd.read_csv(file)

    end_time = time.time()
    print("Time to run:", end_time - start_time, "seconds")


# test how long it takes to load and save the .dat
# files num_saves times. Uses the pandas dataframe
def benchmark_pandas_load_and_save(num_saves=11):
    files = glob.glob(dat_dir + "*.dat")
    start_time = time.time()

    for file in files:
        print(file)
        df = pd.read_csv(file, header=1)
        output_file = file.replace(".dats", "bin")
        for i in range(num_saves + 1):
            df.to_csv(output_file, index=False)

    end_time = time.time()
    print("Time to run:", end_time - start_time, "seconds")
