# Mark's Plan for Cleaning Data

start with the 24-hour data set (`data_24`), find 
inconsistencies in the data. That is to find data that is from 
faulty sensors or was not collected properly as well as making 
it so that the columns and data that are in columns are 
consistent throughout the years, in particular through the 
year 2015 when the network was greatly expanded.
1. Write a program that finds the 3 nearest weather stations for 
   every weather station, this shouldn't be too difficult since 
   there are ~120 weather stations and each has a coordinate.
   1. get metadata for each weather station (host it on GitHub?)
   2. write algorithm, document and prove algorithm
   3. write program to implement algorithm
2. Find standards for replacing bad data, check environment canada, 
stats canada and other organizations
3. Go through all columns with a basic bound check and find major 
   problems (way off data, wrong data in columns, ect)
4. Fix problems with data rows, replace outliers with industry 
   standard (empty, error bitmap, ect)
5. reload the data into the SQL server

## Mark's Notes on Cleaning the Data

In [this](https://library.wmo.int/?lvl=notice_display&id=12793#ZFFMRXbMJPY),
section 3, pg. 60, it describes the WMO standards on land surface 
observations. It also provides a definition on what is a "gross 
error". This may be useful for choosing what data to eliminate 
from our data set.

environment canada standards documentation: [here](https://climate.weather.gc.ca/doc/Technical_Documentation.pdf)

### Algorithm for finding the closest n stations
Its naive but it should work. Since we have a small number of 
stations it should not be a problem.
```python
def get_n_closest_stations():
   closest_stations = [n]   # array of size n
   for station in stations:
       # do trig to get stationDist
       if stationDist < closestStations:
           closest_stations[i] = station
   return closest_stations
```

### Looking through the data
The code that makes the database is held on the remote desktop server 
under C:\Users\Administrator\Documents\NewCleaner. The readme is 
pretty thorough and the code is well documented, so it's pretty 
easy to read. I will likely be modifying these scripts. In 
particular add a step after apply_qa.py which would do my own 
quality assurance. Right now it seems pretty solid in the data, 
but I will have to double-check that everything is good.

Carberry around the 2014-2015 era seems a bit funky. It is missing 
more 
columns than other stations as well as printing null for many of 
the min battery readings. (It was giving negative readings as well 
as very outlier readings, eliminated by qa probably.)
Carberry's data quality seems especially bad, but it seems like QA 
just turned everything to null, possibly erroneously. There must 
be a different table somewhere because I can't see where some data 
is coming from.


## Process for doing quality assurance relative to neighboring stations
```python
# load in 1 chunk of data across all stations (minute, hour, day)
for station in stations:
    if station[attribute] > avg + avg * 0.25 
       or station[attribute] < avg - avg * 0.25:
        # outside of bounds
        station[attribute] = NULL # none?
```
