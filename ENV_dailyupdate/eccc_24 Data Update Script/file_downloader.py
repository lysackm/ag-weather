# Author: Zeel Khokhariya
#Supervisor: Timi Ojo
#Last edited: 2022-03-08
#purpose: Insert and update daily Datra for eccc_24
from msilib.schema import Error
import mysql.connector
from ast import And
from tqdm import tqdm, trange
from tqdm import trange
import requests
import pandas as pd
from datetime import datetime, timedelta
from mysql.connector import Error
import os

# Size to download from server at a time
chunk_size = 1024


# function to get active station list from activeStations.txt
def getActiveStationList():
    my_file = open(
        "C:/Users\Administrator/Documents/ENV_dailyupdate/eccc_24 Data Update Script/activeStations.txt", "r")
    content = my_file.read()
    activeStnList = content.split("\n")
    return activeStnList


# getting active station list
stationList = getActiveStationList()
currentDate = datetime.now()
currentYear = str(currentDate)[0:4]
currentMonth = str(currentDate)[5:7]
lastMonthDate = datetime.now() - timedelta(days=30)
lastMonth = str(lastMonthDate)[5:7]


monthList = [lastMonth, currentMonth]


with open("C:/Users/Administrator/Documents/ENV_dailyupdate/eccc_24 Data Update Script/Download_daily_data/downloadedData.csv", 'wb') as f:

    for Stn in tqdm(iterable=stationList, desc='Downloading Station Data'):
        #print('\tDownloading for Stn:{}...'.format(Stn));

        for month in monthList:
            if month == lastMonth and lastMonth == '12':
                url = "https://dd.weather.gc.ca/climate/observations/daily/csv/MB/climate_daily_MB_{}_{}-{}_P1D.csv".format(
                    Stn, (currentYear-1), month)
            else:
                url = "https://dd.weather.gc.ca/climate/observations/daily/csv/MB/climate_daily_MB_{}_{}-{}_P1D.csv".format(
                    Stn, (currentYear), month)

            url = url.rstrip()
            req = requests.get(url, stream=True)

            # for data in tqdm(iterable= req.iter_content(chunk_size=chunk_size), total=total_size/chunk_size, unit='KB'):
            for data in req.iter_content():
                f.write(data)


print("download compelete")
f.close()


# reading csv
df = pd.read_csv("C:/Users/Administrator/Documents/ENV_dailyupdate/eccc_24 Data Update Script/Download_daily_data/downloadedData.csv",
                 index_col=False, encoding='unicode_escape')
df = df[df['Date/Time'] != 'Date/Time']
df.reset_index(drop=True, inplace=True)

df.to_csv("C:/Users/Administrator/Documents/ENV_dailyupdate/eccc_24 Data Update Script/Download_daily_data/downloadedData.csv",
          encoding="utf=8", index=False)

coloumn_list = df.columns.values.tolist()
print(len(coloumn_list))
print(coloumn_list)
print(df)
for col in coloumn_list:
    df.update(df[[col]].applymap('"{}"'.format))

df = df.replace(to_replace='"nan"', value="null")
print(df)
# connecting to database
try:
    cnx = mysql.connector.connect(user='brian', password='4wVNgwev',
                                  host='localhost',
                                  database='historical', auth_plugin='mysql_native_password')

    cursor = cnx.cursor()
    for index, row in df.iterrows():
        os.system("cls")
        helper_string = ""
        StnID = ""
        count = 1
        for col in coloumn_list:
            helper_string += '{} as col{},'.format(row[col], count)
            count = count + 1

            if col == "Latitude (y)":

                if row["Station Name"] == '"BRANDON A"':
                    StnID = 2
                elif row["Station Name"] == '"CARBERRY CS"':
                    StnID = 4
                elif row["Station Name"] == '"MELITA"':
                    StnID = 26
                elif row["Station Name"] == '"CARMAN U OF M CS"':
                    StnID = 5
                elif row["Station Name"] == '"CYPRESS RIVER RCS"':
                    StnID = 8
                elif row["Station Name"] == '"DAUPHIN"':
                    StnID = 9
                elif row["Station Name"] == '"DEERWOOD RCS"':
                    StnID = 55
                elif row["Station Name"] == '"EMERSON AUTO"':
                    StnID = 11
                elif row["Station Name"] == '"FISHER BRANCH (AUT)"':
                    StnID = 56
                elif row["Station Name"] == '"GIMLI CLIMATE"':
                    StnID = 14
                elif row["Station Name"] == '"GRETNA (AUT)"':
                    StnID = 17
                elif row["Station Name"] == '"KLEEFELD (MAFRI)"':
                    StnID = 22
                elif row["Station Name"] == '"MCCREARY"':
                    StnID = 25
                elif row["Station Name"] == '"MORDEN CDA CS"':
                    StnID = 29
                elif row["Station Name"] == '"PILOT MOUND (AUT)"':
                    StnID = 34
                elif row["Station Name"] == '"PINAWA"':
                    StnID = 35
                elif row["Station Name"] == '"PORTAGE SOUTHPORT A"':
                    StnID = 37
                elif row["Station Name"] == '"ROBLIN"':
                    StnID = 38
                elif row["Station Name"] == '"SHOAL LAKE CS"':
                    StnID = 40
                elif row["Station Name"] == '"SPRAGUE"':
                    StnID = 41
                elif row["Station Name"] == '"SWAN RIVER RCS"':
                    StnID = 44
                elif row["Station Name"] == '"THE PAS A"':
                    StnID = 45
                elif row["Station Name"] == '"WASAGAMING"':
                    StnID = 51
                elif row["Station Name"] == '"WINNIPEG INTL A"':
                    StnID = 52
                helper_string += "{} as col{},".format(StnID, count)
                count = count + 1

        stationname = '{}'.format(row["Station Name"])
        stnID = '{}'.format(StnID)
        datetime = '{}'.format(row["Date/Time"])

        #helper_string = helper_string.replace('"nan"', "null")
        helper_string = helper_string[:-1]

        insertQuery = "Insert into eccc_24 (Longitude, Latitude, StnID,Station_name,Climate_ID, DateTime, Year, Month, Day, Data_Quality,Max_TempC, Max_Temp_Flag,Min_TempC, Min_Temp_Flag,Mean_TempC, Mean_Temp_Flag,Heat_Deg_DaysC,Heat_Deg_Days_Flag,Cool_Deg_DaysC, Cool_Deg_Days_Flag,Total_Rain_mm,Total_Rain_Flag,Total_Snow_cm,Total_Snow_Flag,Total_Precip_mm,Total_Precip_Flag,Snow_on_Grnd_cm,Snow_on_Grnd_Flag,Dir_of_Max_Gust_10s_deg,Dir_of_Max_Gust_Flag,Spd_of_Max_Gust_km_per_h,Spd_of_Max_Gust_Flag)  SELECT * FROM (SELECT {}) as tmp where NOT EXISTS (SELECT StnID,Station_name,DateTime from eccc_24 where StnID = {} and Station_name = {} and DateTime ={})LIMIT 1;".format(helper_string, stnID, stationname, datetime)
        #print(insertQuery, end="\r")
        print("Inserting data for Station: {} for a Date:{}...".format(
            stationname, datetime))
        cursor.execute(insertQuery)

        updateQuery = 'update eccc_24 set Longitude = {}, Latitude= {}, StnID = {},Station_name= {},Climate_ID= {},DateTime= {},Year ={},Month= {},Day= {},Data_Quality={},Max_TempC={},Max_Temp_Flag={},Min_TempC={},Min_Temp_Flag= {},Mean_TempC= {},Mean_Temp_Flag={},Heat_Deg_DaysC= {},Heat_Deg_Days_Flag= {},Cool_Deg_DaysC= {},Cool_Deg_Days_Flag= {},Total_Rain_mm= {},Total_Rain_Flag= {},Total_Snow_cm= {},Total_Snow_Flag= {},Total_Precip_mm= {},Total_Precip_Flag= {},Snow_on_Grnd_cm= {},Snow_on_Grnd_Flag= {},Dir_of_Max_Gust_10s_deg={},Dir_of_Max_Gust_Flag= {},Spd_of_Max_Gust_km_per_h={},Spd_of_Max_Gust_Flag={} where Station_Name={} and DateTime={} and StnID={};'.format(
            row[0], row[1], StnID, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[2], row[4], StnID)
        updateQuery = updateQuery.replace("nan", "null")
        # print(updateQuery)
        cursor.execute(updateQuery)

        cnx.commit()

    cursor.close()
    cnx.close()
    print("Inserted Data Successfully!!")
except Error as e:
    print("Error while connecting to MySQL Workbench", e)
