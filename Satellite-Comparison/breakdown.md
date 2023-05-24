# Comparison with MERRA2 Weather Data

## Fetching MERRA2 Data
pull down 1 file with total area but 1 attribute, possibly in a 
time frame that is more manageable. Once I have the data, make 
columns based off of geo location. (Maybe do some timed analysis 
of what is faster, downloading one attribute for a large 
area/period of time, or downloading it for one area. Seems like 
its going to be pretty slow...)

### Problems
* Files are too big, and take too long to pull down
  * possible solutions, see if loading files by singular 
    attributes, or for only the areas we need is possible.
* The github repo used to download data's seems ok but will be slow
  * Use my home internet?

### Time trials right now
Have to run for 1 attribute at a time, for 5 years, 1 location, 1 
attribute it says 30 minutes predicted time, actual time is 24 
minutes.
120 (stations) * 24 (minutes) * 10 (attributes) = 480 hours 
download time.

Investigate using other servers, pruning data thats being 
retrieved, reduce time costs.

Internet via wifi (MNIA-AGR) is from 0-600 kbps. 

See if I can reduce the amount of data that is being fetched

Monthly
http://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_MONTHLY/M2TMNXLND.5.12.4/2018/MERRA2_400.tavgM_2d_lnd_Nx.201801.nc4.nc?TSOIL1[0:0][0:360][0:575],lat[0:360],lon[0:575],time[0:0]

hourly
http://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2/M2T1NXFLX.5.12.4/2022/01/MERRA2_400.tavg1_2d_flx_Nx.20220101.nc4.nc?PRECTOT[0:0][0:360][0:575],lat[0:360],lon[0:575],time[0:0]


## Breaking down the grib files from conpernicus
Get the coordinate of a weather station, and compare it to the 
mapped coordinate in the grib file. The grib file is almost 
certainly not continuous. How should the averages be made?

Are the values for an area or for a point on the grid?

keys for the grib file
['globalDomain', 'GRIBEditionNumber', 'eps', 'offsetSection0', 'section0Length', 'totalLength', 'editionNumber', 'WMO', 'productionStatusOfProcessedData', 'section1Length', 'wrongPadding', 'table2Version', 'centre', 'centreDescription', 'generatingProcessIdentifier', 'gridDefinition', 'indicatorOfParameter', 'parameterName', 'parameterUnits', 'indicatorOfTypeOfLevel', 'pressureUnits', 'typeOfLevelECMF', 'typeOfLevel', 'level', 'yearOfCentury', 'month', 'day', 'hour', 'minute', 'second', 'unitOfTimeRange', 'P1', 'P2', 'timeRangeIndicator', 'numberIncludedInAverage', 'numberMissingFromAveragesOrAccumulations', 'centuryOfReferenceTimeOfData', 'subCentre', 'paramIdECMF', 'paramId', 'cfNameECMF', 'cfName', 'cfVarNameECMF', 'cfVarName', 'unitsECMF', 'units', 'nameECMF', 'name', 'decimalScaleFactor', 'setLocalDefinition', 'optimizeScaleFactor', 'dataDate', 'year', 'dataTime', 'julianDay', 'stepUnits', 'stepType', 'stepRange', 'startStep', 'endStep', 'marsParam', 'validityDate', 'validityTime', 'deleteLocalDefinition', 'localUsePresent', 'localDefinitionNumber', 'GRIBEXSection1Problem', 'marsClass', 'marsType', 'marsStream', 'experimentVersionNumber', 'perturbationNumber', 'numberOfForecastsInEnsemble', 'grib2LocalSectionNumber', 'shortNameECMF', 'shortName', 'ifsParam', 'stepTypeForConversion', 'md5Section1', 'md5Product', 'gridDescriptionSectionPresent', 'bitmapPresent', 'angleSubdivisions', 'section2Length', 'radius', 'numberOfVerticalCoordinateValues', 'neitherPresent', 'pvlLocation', 'dataRepresentationType', 'gridDefinitionDescription', 'gridDefinitionTemplateNumber', 'Ni', 'Nj', 'latitudeOfFirstGridPoint', 'latitudeOfFirstGridPointInDegrees', 'longitudeOfFirstGridPoint', 'longitudeOfFirstGridPointInDegrees', 'resolutionAndComponentFlags', 'ijDirectionIncrementGiven', 'earthIsOblate', 'resolutionAndComponentFlags3', 'resolutionAndComponentFlags4', 'uvRelativeToGrid', 'resolutionAndComponentFlags6', 'resolutionAndComponentFlags7', 'resolutionAndComponentFlags8', 'latitudeOfLastGridPoint', 'latitudeOfLastGridPointInDegrees', 'longitudeOfLastGridPoint', 'longitudeOfLastGridPointInDegrees', 'iDirectionIncrement', 'jDirectionIncrement', 'scanningMode', 'iScansNegatively', 'jScansPositively', 'jPointsAreConsecutive', 'alternativeRowScanning', 'iScansPositively', 'jScansNegatively', 'scanningMode4', 'scanningMode5', 'scanningMode6', 'scanningMode7', 'scanningMode8', 'swapScanningAlternativeRows', 'jDirectionIncrementInDegrees', 'iDirectionIncrementInDegrees', 'numberOfDataPoints', 'numberOfValues', 'latLonValues', 'latitudes', 'longitudes', 'distinctLatitudes', 'distinctLongitudes', 'zeros', 'PVPresent', 'PLPresent', 'deletePV', 'md5Section2', 'lengthOfHeaders', 'md5Headers', 'missingValue', 'tableReference', 'section4Length', 'halfByte', 'dataFlag', 'binaryScaleFactor', 'referenceValue', 'referenceValueError', 'sphericalHarmonics', 'complexPacking', 'integerPointValues', 'additionalFlagPresent', 'orderOfSPD', 'boustrophedonic', 'hideThis', 'packingType', 'bitsPerValue', 'constantFieldHalfByte', 'bitMapIndicator', 'values', 'numberOfCodedValues', 'packingError', 'unpackedError', 'maximum', 'minimum', 'average', 'standardDeviation', 'skewness', 'kurtosis', 'isConstant', 'numberOfMissing', 'dataLength', 'changeDecimalPrecision', 'decimalPrecision', 'bitsPerValueAndRepack', 'scaleValuesBy', 'offsetValuesBy', 'gridType', 'getNumberOfValues', 'md5Section4', 'section5Length', 'analDate', 'validDate']

Could do:

```python
for gr in grib:
    if (gr.lat, gr.lon) is station:
        # print column to correct csv (one csv per attribute)
        # list coords -> station
```

Pros: simple, lots of control
Cons: will probably take some hours to process

Could run PyNIO on WSL on my personal device. Then load in entire 
columns of data at a time and load them into a csv.

With ER5 data, if I want to use xarrays to do work on it, it may 
be good to download the files as net cat on one attribute all 5 
years. It seems like this is going to be simplier to parse and to 
download.

### Processes for processing data

ERA5 all together, by year
loop through with pygrib, load in each sub array (2d map with 
metadata) into a xarray. Then go through the xarray load in by 
weather station location (120 stations -> 52 locations (for Merra))
add rows into the db based off of all the locations that are in 
grib file. One point on a map becomes a row. Will this be super 
inefficient? Is it better to do analysis on the multidimensional 
arrays as is; it would probably be more efficient than flattening 
the db.

Its possible that I would be able to load the grib file of one 
attribute into xarray, then I would be able to just loop through 
the lat and longs and fetch it going all the way down the array.


### getting the ERA-5 land data
Seems like it will be ok if I use the ERA5_webscraper.py program.

### File Format
Needs to have an output in a human-readable file (csv)
Should have StnID, StationName, Latitude, Longitude, 
Elevation, StationData, MerraData, EraLandData

Should have 1 file per attribute
This means that each file would have to have all years, all stations

Mapping coordinates to Merra and era. Have a station, get its 
coord, find the box that it is in for merra and era, add those 
attributes to it.
Is it possible to load in 1 day for each, merge the columns?

Download the db file at home (need a local copy)

### Merra Missing Data

| start date | end date   | database  |
|------------|------------|-----------|
| 2021-05-31 | 2021-10-01 | M2T1NXLND |
| 2020-08-31 | 2020-10-01 | M2T1NXLND |


### Waterloo data
CASPAr system at University of Waterloo – not sure if you’ve used 
that but the reanalysis is from the “RDRS” model 


HRDPS:
variables we are getting: wind speed, precipitation, temperature, 
wind direction

https://dd.weather.gc.ca/
