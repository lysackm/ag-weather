import requests
import json
import pandas as pd
import datetime


missed_days = 0


def create_url(year, month, day, hour="06"):
    assert(hour == "00" or hour == "06" or hour == "12" or hour == "18")

    if len(str(month)) == 1:
        month = "0" + str(month)

    if len(str(day)) == 1:
        day = "0" + str(day)

    return "https://live.mbagweather.ca/models/WindForecast/archives/wx_" + str(year) + "-" + str(month) + "-" + str(day) + "_" + hour + ".json"


def get_wind_data(url):
    global missed_days

    r = requests.get(url)
    if r.status_code == 200:
        json_data = json.loads(r.text[8:-1])
    else:
        missed_days += 1
        json_data = None

    return json_data


def process_data(json_data, df, year, month, day):
    df_new = pd.DataFrame(json_data)

    date = datetime.datetime(year, month, day)
    iso_string = date.isoformat()
    df_new["date"] = iso_string

    df_new["offset"] = df_new.index % 53

    df = pd.concat([df, df_new])
    return df


def cycle_dates(df, hour="06"):
    for year in range(2020, 2024):
        for month in range(1, 13):

            if month in [1, 3, 5, 7, 8, 10, 12]:
                num_days = 31
            elif month in [4, 6, 9, 11]:
                num_days = 30
            elif month in [2]:
                # ignoring leap years in statistical analysis
                num_days = 28

            for day in range(1, num_days + 1):
                url = create_url(year, month, day, hour)
                print(url)
                data = get_wind_data(url)
                if data is not None:
                    df = process_data(data, df, year, month, day)

    return df


def scrape_data():
    global missed_days

    for hour in ["00", "06", "12", "18"]:
        print("hour", hour)
        df = pd.DataFrame()
        df = cycle_dates(df, hour)

        df.to_csv(hour + "_wind_data.csv", index=False)

    print("Missed days:", missed_days)


if __name__ == "__main__":
    scrape_data()
