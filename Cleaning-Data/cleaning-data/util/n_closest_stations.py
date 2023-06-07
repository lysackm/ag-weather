# This is a program that is to be run on the csv of all active stations retrieved from StationList.xlsx
# This program can easily be modified though to be used on any csv output for any weather stations, if you modify the
# lat_index and long_index to be pointing to the correct index in the csv row.
# It goes through each station in the csv and returns the n nearest stations. Output is in a csv file called output.txt.
# Format of the output is station, neighbor1, neighbor2, ..., neighborN


# column names for StationList.xlsx
# SN,StnID,StationName,LatDD,LongDD,Region,Column1,Air_T,RH,Pluvio,TBRG,AvgWS,
# AvgWD,Sol Rad,Soil Temp (5 cm),Soil Moisture & Temp (5 and 20 cm),Soil Moisture & Temp (50 and 100 cm),Barometric
# Pressureimport
import geopy.distance
import csv

lat_index = 3
long_index = 4
name_index = 1


# goes through closest stations and sees if stored dist is lower than any of the distances in
# the closest_stations array of tuples.
# parameters:
#   closest_stations: array of size n of arrays of size 2, [dist, [row from csv]]v])
#   dist: distance of a different station
def check_lowest(closest_stations, dist):
    is_closer = False
    for data in closest_stations:
        if data[0] > dist:
            is_closer = True
    return is_closer


# replaces the station that is the furthest away with the new closer station (new_data)
# parameters:
#   closest_stations: array of size n of arrays of size 2, [dist, [row from csv]]
#   new_data: array of size 2, [dist, [row from csv]]
def replace_furthest(closest_stations, new_data):
    index = 0
    for i in range(0, len(closest_stations)):
        if closest_stations[i][0] > closest_stations[index][0]:
            index = i
    closest_stations[index] = new_data
    return closest_stations


# given n, find the n closest stations to all the stations provided in the csv "station-metadata.csv"
# parameters:
#   n: number of neighbors wanted, default is 3
def n_closest_stations(n=3):
    stations = []

    f = open("../neighboring-stations.csv", "w")
    f.write("Station")
    for i in range(n):
        f.write(f",Neighbor{i}")
    f.write("\n")
    f.close()

    with open('station-metadata.csv', newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            stations.append(row)

    # station is the station we are getting n closest neighbors
    for station in stations:
        closest_stations = []
        # neighbor is any other station
        neighbors = stations.copy()
        neighbors.remove(station)

        station_coord = (station[lat_index], station[long_index])

        # inefficient algorithm but it works in a few seconds right now, so it's ok, O(n^2)
        for neighbor in neighbors:
            neighbor_coord = (neighbor[lat_index], neighbor[long_index])
            dist = geopy.distance.geodesic(station_coord, neighbor_coord)
            if len(closest_stations) < n:
                closest_stations.append([dist, neighbor])
            elif check_lowest(closest_stations, dist):
                closest_stations = replace_furthest(closest_stations, [dist, neighbor])

        f = open("../neighboring-stations.csv", "a")
        output = [station[name_index]]
        for closest_station in closest_stations:
            output.append(closest_station[1][name_index])
        f.write(", ".join(output))
        f.write("\n")
        f.close()


n_closest_stations(3)
print("Program finished successfully, check 'neighboring-stations.csv' in the dir of this script to find the sqr-err.")
