from datetime import datetime, timedelta
from itertools import count
import os
from turtle import pd
from tqdm import tqdm
import requests
import os
import pandas as pd
from mysql.connector import Error
import mysql.connector


# Size to download from server at a time
chunk_size = 1024

# function to get active station list from activeStations.txt


def getActiveStationList():
    my_file = open("C:/Users/Administrator/Documents/ENV_hourlyupdate/Env_data_update_script_hourly/Code/Station_input.txt","r");
    content = my_file.read()
    activeStnList = content.split("\n")
    return activeStnList


# getting active station list

stationList = getActiveStationList()
currentDate = datetime.now()
currentYear = int(str(currentDate)[0:4])
currentMonth = str(currentDate)[5:7]
currentDay = str(currentDate)[8:10]
todayDate = str(currentDate)[0:10]
lastMonthDate = datetime.now() - timedelta(days=30)

monthList = []
DateList = []
YearList = []
for x in range(3):
    tempDate = datetime.now() - timedelta(days=x+1)

    tempDate = str(tempDate)[0:10]
    DateList.append(tempDate)

    tempMonth = str(tempDate)[5:7]
    if not tempMonth in monthList:
        monthList.append(tempMonth)

    tempYear = str(tempDate)[0:4]
    if not tempYear in YearList:
        YearList.append(tempYear)


lastMonth = str(lastMonthDate)[5:7]

print("DateList: {}".format(DateList))
print("monthList: {}".format(monthList))
print("yearList: {}".format(YearList))
print("LastMonth: {}".format(lastMonth))


with open("C:/Users/Administrator/Documents/ENV_hourlyupdate/Env_data_update_script_hourly/Code/downloaded_data/downloadedData.csv", 'wb') as f:

    for Stn in tqdm(iterable=stationList, desc='Downloading Station Data'):

        print('\tDownloading for Stn:{}...'.format(Stn))

        for month in monthList:

            if month == lastMonth and lastMonth == '12':
                url = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={}&Year={}&Month={}&timeframe=1&submit=Download+Data".format(
                    Stn, (currentYear-1), (month))
                print(url)
            else:
                url = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={}&Year={}&Month={}&timeframe=1&submit=Download+Data".format(
                    Stn, (currentYear), month)

            url = url.rstrip()
            req = requests.get(url, stream=True)

            for data in req.iter_content():
                f.write(data)


print("download compelete")
f.close()


# reading csv
df = pd.read_csv("C:/Users/Administrator/Documents/ENV_hourlyupdate/Env_data_update_script_hourly/Code/downloaded_data/downloadedData.csv",
                 index_col=False, encoding='unicode_escape')

df = df[df['Date/Time (LST)'] != 'Date/Time (LST)']
df.reset_index(drop=True, inplace=True)

df.to_csv("C:/Users/Administrator/Documents/ENV_hourlyupdate/Env_data_update_script_hourly/Code/downloaded_data/downloadedData.csv",
          encoding="utf=8", index=False)

coloumn_list = df.columns.values.tolist()


# refactoring data
print(todayDate)
df.drop(df[df['Date/Time (LST)'] >= todayDate].index, inplace=True)
DateList.sort()


df.drop(df[df['Date/Time (LST)'] < DateList[0]].index, inplace=True)

for col in coloumn_list:
    df.update(df[[col]].applymap('"{}"'.format))

df = df.replace(to_replace='"nan"', value="null")


print(df);

try:
    cnx = mysql.connector.connect(user='brian', password='4wVNgwev',
                                  host='localhost',
                                  database='historical', auth_plugin='mysql_native_password')

    cursor = cnx.cursor()
    for index, row in df.iterrows():
        os.system("cls")
        helper_string = ""
        count = 1
        for col in coloumn_list:
            helper_string += '{} as col{},'.format(row[col], count)
            count = count + 1

        stationname = '{}'.format(row["Station Name"])
        datetime = '{}'.format(row["Date/Time (LST)"])

        # removing last "," from the string
        helper_string = helper_string[:-1]

        insertQuery = "Insert into eccc_60 (Longitude, Latitude, Station_Name,Climate_ID,DateTime, Year, Month, Day, Time_LST,Temp_C, Temp_Flag,Dew_Point_Temp_C, Dew_Point_Temp_Flag,Rel_Hum_percent, Rel_Hum_Flag,Precip_Amount_mm,Precip_Amount_Flag,Wind_Dir_10s_deg, Wind_Dir_Flag,Wind_Spd_km_per_h,Wind_Spd_Flag,Visibility_km,Visibility_Flag,Stn_Press_kPa,Stn_Press_Flag,Hmdx,Hmdx_Flag,Wind_Chill,Wind_Chill_Flag,Weather)  SELECT * FROM (SELECT {}) as tmp where NOT EXISTS (SELECT Station_name,DateTime from eccc_60 where  Station_name = {} and DateTime ={})LIMIT 1;".format(helper_string, stationname, datetime)
        print("Inserting data for Station: {} for a Date:{}...".format(
            stationname, datetime))

        cursor.execute(insertQuery)

        updateQuery = updateQuery = 'update eccc_60 set Longitude={}, Latitude={}, Station_Name={},Climate_ID={},DateTime={}, Year={}, Month={}, Day={}, Time_LST={},Temp_C={}, Temp_Flag={},Dew_Point_Temp_C={}, Dew_Point_Temp_Flag={},Rel_Hum_percent={}, Rel_Hum_Flag={},Precip_Amount_mm={},Precip_Amount_Flag={},Wind_Dir_10s_deg={}, Wind_Dir_Flag={},Wind_Spd_km_per_h={},Wind_Spd_Flag={},Visibility_km={},Visibility_Flag={},Stn_Press_kPa={},Stn_Press_Flag={},Hmdx={},Hmdx_Flag={},Wind_Chill={},Wind_Chill_Flag={},Weather={} where Station_Name={} and DateTime={};'.format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[2], row[4])

        cursor.execute(updateQuery)
        cnx.commit()

    cursor.close()
    cnx.close()
    print("Iserted Data Successfully!!!")
except Error as e:
    print("Error while connecting to MySQL Workbench", e)
