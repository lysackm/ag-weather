import requests
import rsa
import pandas as pd

import xml.etree.ElementTree as ET
import base64
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import post_session


# returns encrypted password in base 64
# takes in the password in string form and the xml representation of the public key
# and exponent returned from GET session
def encrypt_password(response, password):
    root = ET.fromstring(response["Xml"])
    modulo_string = root[0].text
    exponent_string = root[1].text

    password_encoded = password.encode('utf8')

    modulo_int = int(base64.b64decode(modulo_string).hex(), 16)
    exponent_int = int(base64.b64decode(exponent_string).hex(), 16)

    public_key = rsa.PublicKey(modulo_int, exponent_int)
    public_key.save_pkcs1(format='PEM').decode('utf-8')

    # Load the RSA public key from XML
    rsa_key = RSA.import_key(public_key.save_pkcs1(format='PEM').decode('utf-8'))
    # Create an RSA cipher object with OAEP padding
    cipher = PKCS1_OAEP.new(rsa_key)
    # Encrypt the plaintext bytes
    encrypted_bytes = cipher.encrypt(password_encoded)
    # Convert the encrypted bytes to Base64
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    return encrypted_base64


# a file containing the username and password need to be made.
# DO NOT ADD THIS TO GITHUB!!!!
# If you do the credentials would be accessible to anyone!
# credentials.txt format:
# <username>
# <password>
def authentication(api="Provisioning", version="v1"):
    password = ""
    username = ""
    with open("credentials.txt", "r") as file:
        line_num = 0
        for line in file:
            if line_num == 0:
                username = line
                username = username.strip()
            else:
                password = line
            line_num += 1

    # receive public key
    # GET /session/publickey
    # public_key = get_session_publickey.GetPublicKey()
    public_key_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/{api}/{version}/session/publickey"
    public_key_response = requests.get(public_key_url).json()

    encrypted_password = encrypt_password(public_key_response, password)

    # create session
    # POST /session
    session = post_session.PostSession()
    session.username = username
    session.encrypted_password = encrypted_password
    session.locale = 'English'

    session_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/{api}/{version}/session"
    response = requests.post(session_url,
                             params={"Username": session.username, "EncryptedPassword": session.encrypted_password})
    print("Should get 200 response for authentication", response, sep="\n")

    # token needed for all other response codes
    token = response.content.decode(response.encoding)

    return token


# uses publishing api, and therefore needs to use the token from the publishing api
def get_locations(token, location_identifier):
    session_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Publish/v2/GetLocationData?LocationIdentifier={location_identifier}"
    response = requests.get(session_url, headers={"X-Authentication-Token": token})

    print("should be 200 response", response)
    return response


# GET locationsTimeSeries
# https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/swagger-ui/#!/timeseries/GetTimeSeriesTimeSeriesUniqueId_Get
def get_locations_time_series(token, location_unique_id):
    session_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/locations/{location_unique_id}/timeseries"
    response = requests.get(session_url, headers={"X-Authentication-Token": token})

    # print(f"<GET locations/{location_unique_id}/timeseries> should be 200 response", response)
    return response


# POST locationsTimeSeriesCalculated
# https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/swagger-ui/#!/locations/PostCalculatedDerivedTimeSeriesLocationUniqueIdtimeseriescalculated_Post
def post_locations_time_series_calculated(token, location_unique_id, params):
    session_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/locations/{location_unique_id}/timeseries/calculated"
    response = requests.post(session_url, headers={"X-Authentication-Token": token}, params=params)
    return response


# PUT locationsTimeSeriesCalculated
# https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/swagger-ui/#!/timeseries/PutTimeSeriesTimeSeriesUniqueId_Create
def put_locations_time_series_calculated(token, time_series_unique_id, params):
    session_url = f"https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Provisioning/v1/timeseries/{time_series_unique_id}"
    response = requests.put(session_url, headers={"X-Authentication-Token": token}, params=params)
    return response


# return a formula to apply thresholds to the time series based on
# a high or low threshold
# Syntax standards (mostly just C++) can be found here:
# https://mbaqts-prod.aquaticinformatics.net/AQUARIUS/Help-en/Default.htm
def get_formula(low_threshold, high_threshold):
    return f"if ({low_threshold} < x1 && x1 < {high_threshold}) {{ y = x1; }} else {{ y = double.NaN;}}"


# iterates through the dataframe of timeseries ids and other data and sends a PUT http request to Aquarius to
# change the publish status of the time series to false
# label_df should have columns UniqueId (the time series id), and a column with the labels indicated by label_column
def un_publish_series(label_df, location_row, label_column, token):
    for index, row in label_df.iterrows():
        time_series_unique_id = row["UniqueId"]
        label = row[label_column]
        params = {
            "TimeSeriesUniqueId": time_series_unique_id,
            "Label": label,
            "Publish": False,
        }
        response = put_locations_time_series_calculated(token, time_series_unique_id, params)

        print("Response: ", location_row["StationName"], label, response.status_code)


# unpublished telemetry and working time series
def un_publish_timeseries(token):
    stations_df = pd.read_csv("StationList.csv")
    parameter_df = pd.read_csv("unpublished_parameter_data.csv")

    for index, row in stations_df.iterrows():
        location_unique_id = row["location_unique_id"]
        response = get_locations_time_series(token, location_unique_id)

        time_series = response.json()["Results"]
        time_series_df = pd.json_normalize(time_series)

        time_series_telemetry_df = time_series_df.merge(parameter_df, how="inner", left_on=["Parameter", "Label"],
                                                        right_on=["parameter", "label_telemetry"])
        label_telemetry_df = time_series_telemetry_df[["label_telemetry", "UniqueId"]]
        time_series_working_df = time_series_df.merge(parameter_df, how="inner", left_on=["Parameter", "Label"],
                                                      right_on=["parameter", "label_working"])
        label_working_df = time_series_working_df[["label_working", "UniqueId"]]
        time_series_derived_df = time_series_df.merge(parameter_df, how="inner", left_on=["Parameter", "Label"],
                                                      right_on=["parameter", "label_derived"])
        label_derived_df = time_series_derived_df[["label_derived", "UniqueId"]]

        # un_publish_series(label_telemetry_df, row, "label_telemetry", token)
        # un_publish_series(label_working_df, row, "label_working", token)
        un_publish_series(label_derived_df, row, "label_derived", token)


# given a list of time series ids to source the new calculated time series from and other data, create a calculated
# time series
def create_new_calculated_time_series(label, parameter, unit, publish, formula, get_time_series_ids, token):
    method = "DefaultNone"
    utc_offset = "-PT6H"
    interpolation_type = "InstantaneousValues"

    stations_df = pd.read_csv("StationList.csv")

    for index, row in stations_df.iterrows():
        location_unique_id = row["location_unique_id"]
        response = get_locations_time_series(token, location_unique_id)

        time_series = response.json()["Results"]
        time_series_df = pd.json_normalize(time_series)

        # this would need to created for other time_series_added
        time_series_ids = get_time_series_ids(time_series_df)

        params = {
            "LocationUniqueId": location_unique_id,
            "Label": label,
            "Parameter": parameter,
            "Unit": unit,
            "InterpolationType": interpolation_type,
            "UtcOffset": utc_offset,
            "Publish": publish,
            "Method": method,
            "TimeSeriesUniqueIds": time_series_ids,
            "Formula": formula,
        }
        response = post_locations_time_series_calculated(token, location_unique_id, params)
        if response.status_code != 201:
            print(response.status_code, "error at station", row["StationName"])


def get_wet_bulb_ids(time_series_df):
    air_temp_id = \
        time_series_df[(time_series_df["Label"] == "Telemetry15") & (time_series_df["Parameter"] == "TA")][
            "UniqueId"].values[0]
    rel_humidity_id = \
        time_series_df[(time_series_df["Label"] == "Telemetry15") & (time_series_df["Parameter"] == "XR")][
            "UniqueId"].values[0]

    return [air_temp_id, rel_humidity_id]


# Formula taken from the paper Wet-Bulb Temperature from Relative Humidity and Air Temperature
# Stull, R., 2011: Wet-Bulb Temperature from Relative Humidity and Air Temperature. J. Appl. Meteor. Climatol.,
# 50, 2267–2269, https://doi.org/10.1175/JAMC-D-11-0143.1.
def create_wet_bulb_time_series(token):
    label = "15"
    parameter = "WBT"
    unit = "degC"
    publish = True
    # x1: 2m temperature
    # x2: RH
    formula = "double T = x1;\ndouble RH = x2;\ny = T * atan(0.151977 * pow(RH + 8.313659, 0.5)) + atan(T + RH) - atan(RH - 1.676331) + 0.00391838 * pow(RH, 1.5) * atan(0.023101 * RH) - 4.686035"

    create_new_calculated_time_series(label, parameter, unit, publish, formula, get_wet_bulb_ids, token)


# Parameters
#  token: token for authentication (provisioning)
# Purpose
# To create a time series for each station and each parameter for those stations

# # Process Settings
# ## Processing Type and Time Period
# process type: pass through
# ## Process Inputs
# Location: location name -> need to get id
# Time-Series: time series which is being derived from
# Measurement Method: Copy from source time series (default)

# # Time-Series Attributes
# label: see Excel sheet
# parameter: Should be correlated to the time series
# unit: correlated to the time series
# Interpolation: instantaneous values
# UTC Offset: - -PT6H
def post_calculated_time_series(token):
    method = "DefaultNone"
    utc_offset = "-PT6H"
    interpolation_type = "InstantaneousValues"

    stations_df = pd.read_csv("StationList.csv")
    parameter_df = pd.read_csv("parameter_data.csv")

    for index, row in stations_df.iterrows():
        location_unique_id = row["location_unique_id"]
        response = get_locations_time_series(token, location_unique_id)

        time_series = response.json()["Results"]
        time_series_df = pd.json_normalize(time_series)

        time_series_df = time_series_df.merge(parameter_df, how="right", left_on=["Parameter", "Label"],
                                              right_on=["parameter", "label_current"])
        time_series_df[["label_new", "parameter", "unit", "published", "unique_id", "threshold_high", "threshold_low",
                        "parameter_long", "label"]] = \
            time_series_df[
                ["label_new", "Parameter", "unit", "published", "UniqueId", "threshold_high", "threshold_low",
                 "parameter_long", "Label"]]

        for time_series_index, time_series_row in time_series_df.iterrows():
            label = time_series_row["label_new"]
            parameter = time_series_row["parameter"]
            unit = time_series_row["unit"]
            publish = time_series_row["published"]
            time_series_unique_ids = time_series_row["unique_id"]
            formula = get_formula(time_series_row["threshold_low"], time_series_row["threshold_high"])

            params = {
                "LocationUniqueId": location_unique_id,
                "Label": label,
                "Parameter": parameter,
                "Unit": unit,
                "InterpolationType": interpolation_type,
                "UtcOffset": utc_offset,
                "Publish": publish == "yes",
                "Method": method,
                "TimeSeriesUniqueIds": [
                    time_series_unique_ids
                ],
                "Formula": formula,
            }
            response = post_locations_time_series_calculated(token, location_unique_id, params)
            if response.status_code != 200:
                print("error at", row["StationName"], time_series_row["parameter_long"], time_series_row["label"],
                      response.status_code)


# Parameters
# token: the token for the Publish Aquarius api
# Purpose
# read in the station list data and map the station id to
# the unique aquarius id
def map_location_to_id(token):
    stations_df = pd.read_csv("StationList.csv")

    stations_df["location_unique_id"] = stations_df["StnID"].map(lambda id: get_locations(token, id).json()["UniqueId"])

    print(stations_df)
    stations_df.to_csv("StationList.csv", index=False)


def main():
    token_provisioning = authentication()
    # token_publish = authentication("Publish", "v2")
    # get_locations_time_series(token_provisioning, "e154f37b36a140f4af7991d0d4cf8f48")
    # response = get_locations(token_publish, "201")
    # un_publish_timeseries(token_provisioning)
    create_wet_bulb_time_series(token_provisioning)


if __name__ == "__main__":
    main()
