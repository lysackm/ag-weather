import pandas as pd


# year = change values in command line (`seq 1998 2008)
# month = change values in command line (`seq 1 12)
# format= [csv|xml]: the format output
# timeframe = 1: for hourly data
# timeframe = 2: for daily data
# timeframe = 3 for monthly data
# Day: the value of the "day" variable is not used and can be an arbitrary
#      value
# For another station, change the value of the variable stationID
# For the data in XML format, change the value of the variable format to xml
# in the URL.
def station_wget_script(row):
    start_year = str(row["First Year"])
    end_year = str(row["Last Year"])
    stn_id = str(row["Station ID"])
    timeframe = "2"
    stn_script = r'for year in `seq ' + start_year + " " + end_year + '`;do for month in `seq 1 12`' \
                 r';do wget --content-disposition ' \
                 r'"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?' \
                 r'format=csv&stationID=' + stn_id + r'&Year=${year}&Month=${month}&Day=14&timeframe=' + timeframe + \
                 r'&submit= Download+Data";done;done'
    return stn_script


def load_metadata():
    stn_df = pd.read_csv("D:/data/environment_canada/Manitoba_ECCC_metadata.csv")
    mbag_df = pd.read_csv("D:/data/environment_canada/mbag_eccc_threads.csv")["EcccID"]
    # stn_df = stn_df.merge(mbag_df, left_on="Climate ID", right_on="EcccID", how="inner")
    stn_df = stn_df[~stn_df["Climate ID"].astype(str).isin(mbag_df.astype(str))]
    return stn_df


def generate_wget_script():
    stn_df = load_metadata()
    stn_df["script"] = stn_df.apply(station_wget_script, axis=1)
    script = stn_df["script"].str.cat(sep="\n")
    print(script)


generate_wget_script()
