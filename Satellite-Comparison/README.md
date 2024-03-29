# Comparison of Satellite Reanalysis Data and Weather Station Data


# Table of Contents
1. [Merra-2](#merra-2)
2. [Era-5 Land](#era-5-land)
3. [CaSPAr](#caspar)
4. [Station Data](#station-data)
5. [A Very Detailed Look into the Data Correction Process](#data-correction)
6. [Random Forest](#random-forest)

## <a name="merra-2"></a>
## Merra-2
Merra 2 is a data set provided by NASA that describes weather 
conditions globally since 1980. 

### File format
The file structure of the data for Merra-2 is described 
[here.](https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf)
To understand this document you first need to understand how the 
data for Merra-2 is hosted. The data for Merra-2 is hosted on 
several disks in some facility operated by NASA. When 
you fetch data from the database, you have to specify which 
database you are wanting the data from. The document linked above 
lists the naming specifications for each database in section 5.2 
on page 12. For example `M2T1NXRAD` is the name of the database 
for radiation data. The document also lists all the attributes 
that are stored in each database. Note that attribute IDs are 
*not* unique across databases. Make sure that you are downloading 
from the correct database. There are multiple databases for 
different time calculations, eg. 1 hour time frame, 3 hour time 
frame ect.

### Downloading Data
To download the data you will need to register to get an account 
with GEO DISC. It is free and fast.

There are a few ways of downloading data. The Merra-2 databases 
hold the data for the entire world. So to download just one date 
of data for one database can be an extremely large amount of data. 
It can be as high as hundreds of MBs per day. This makes 
downloading data without restrictions completely impractical. You 
can download directly from the Goddard Earth Sciences Data and 
Information Services Center (GEO DISC) by searching for the 
database that you want. However, this does not allow for 
downloading subsets directly. Be wary of the size of data that you 
are downloading.

GEO DISC has a web api service that allows you to use http 
requests to fetch data from them. The fastest way to download the 
data is to go onto GEO DISC, search for the database you are 
wanting to use, select "subset/get data", then choose "Get File 
Subsets using the GES DISC Subsetter". Then input the dates, 
variables, bounding box of area that covers the data you are 
needing, and other prompted information. Then click "get data". 
Then it will generate a text file filled with http request links. 
To test a link you can paste a link into any browser, and you will 
download the corresponding netcat file.

To download the data from the compiled list of links, you can 
follow directions from [here.](https://disc.gsfc.nasa.gov/information/documents?title=Data%20Access)
Personally I used curl to download the links by following this 
[tutorial.](https://disc.gsfc.nasa.gov/information/howto?title=How%20to%20Access%20GES%20DISC%20Data%20Using%20wget%20and%20curl)

This process is much easier to do on a linux machine, or on a 
Windows machine with [WSL](https://learn.microsoft.com/en-us/windows/wsl/install)
installed. Note that WSL is installed on some government machines, 
but requires admin access to use. I personally used an installed 
version of WSL on my personal machine.

This process will likely download one netcat (.nc) file per day. 
You will have to run the program once for every database that you 
query.

There is a GitHub repo with a 
[merra-data scraper](https://github.com/emilylaiken/merradownload)
online but this tool has limited usefulness. For some reason when 
using the tool it can run into issues where a http request will 
get an 503 (internal server issue) error often. This left substantial 
gaps in the data. It 
also took exponentially longer to use. I would recommend using the 
official documented ways of downloading the data. 

### Missing Data
I have had problems with all methods of downloading data. I would 
verify that all the days have been downloaded, check that the 
file size is appropriate (> 1KB) and other precautions. When using 
the webscraper I ran into several 503 http responses, and when 
using curl there were large chunks of data (months) that were not 
properly downloaded.

### Merra-2 Data Downloaded

All attributes are downloaded for the years 2018 to 2022, inclusive

| Database   | Attribute Short Name               | Attribute Long Name                      | Units      |     |
|------------|------------------------------------|------------------------------------------|------------|-----|
| M2T1NXSLV  | T2M                                | Temperature 2 meters                     | Kelvin     |     |
| M2T1NXSLV  | V10M and U10M                      | Vectorized wind components               | m/s        |     |
| M2T1NXSLV  | QV2M                               | 2 meter specific humidity                | Kg/Kg      |     |
| M2T1NXSLV  | PS                                 | Surface pressure                         | Pa         | new |
| M2T1NXSLV  | T2MDEW                             | dew point temperature at 2m              | Kelvin     | new |
| M2T1NXLND  | TSOIL1, TSOIL2, TSOIL3, and TSOIL4 | Soil temperature, level 1-4              | Kelvin     |     |
| M2T1NXLND  | PRECTOTLAND                        | Total precipitation land; bias corrected | Kg/(m^2 s) |     |
| M2T1NXLND  | RZMC                               |                                          | m^3/m^3    | new |
| M2T1NXLND  | SFMC                               |                                          | m^3/m^3    | new |
| M2T1NXLND  | PRMC                               |                                          | m^3/m^3    | new |
| M2T1NXRAD  | SWGDN                              | Incident shortwave land                  | W/m^2      |     |

Note that kg per meter squared is equivalent to mm of rain.


| Attribute                  | depth           | units  | locations | mapped to                          |
|----------------------------|-----------------|--------|-----------|------------------------------------|
| TSOIL1                     | 9.88            | cm     | all       | Soil_TP5_TempC + Soil_TP20_TempC   |
| TSOIL2                     | 19.52           | cm     | all       | Soil_TP20_TempC                    |
| TSOIL3                     | 38.59           | cm     | all       | Soil_TP50_TempC                    |
| TSOIL4                     | 76.26           | cm     | all       | Soil_TP50_TempC + Soil_TP100_TempC |
| TSOIL5                     | 150.71          | cm     | all       | None                               |
| SFMC                       | 5               | cm     | all       | Soil_TP5_VMC                       |
| RZMC                       | 100             | cm     | all       | Soil_TP100_VMC                     |
| PRMC                       | 133.3 - 382.0   | cm     | varies    | None                               |
| Max Water Holding Capacity | 296.59 - 1171.5 | kg m^2 | varies    | None                               |

Note that for TSOIL1-4, SFMC, RZMC, and PRMC the constant data 
summerized above can be found in 
[this document](https://gmao.gsfc.nasa.gov/pubs/docs/Bosilovich785.pdf)
if you search for the corresponding attribute. It is held in the 
database M2CONXLND.

You can use this link for your convience to download the data for 
southern manitoba:
[link](ap/MERRA2_MONTHLY/M2C0NXLND.5.12.4/1980/MERRA2_100.const_2d_lnd_Nx.00000000.nc4.nc4?cdcr2[0:0][277:292][125:137],dzgt1[0:0][277:292][125:137],dzgt2[0:0][277:292][125:137],dzgt3[0:0][277:292][125:137],dzgt4[0:0][277:292][125:137],dzgt5[0:0][277:292][125:137],dzgt6[0:0][277:292][125:137],dzpr[0:0][277:292][125:137],dzrz[0:0][277:292][125:137],dzsf[0:0][277:292][125:137],time,lat[277:292],lon[125:137])

#### Derived Values
Using the equation outlined in this 
[forum post](https://earthscience.stackexchange.com/questions/2360/how-do-i-convert-specific-humidity-to-relative-humidity)
to derive the **relative humidity** from specific humidity, 
temperature, and pressure.

## <a name="era-5-land"></a>
## ERA-5 Land 
ERA-5 Land is a reanalysis of weather data ran by Copernicus, 
which is based in the EU.

### File Format
The ERA-5 Land data can be downloaded as a grib file or as a 
zipped netcat file. There are limitations to the size of a single 
piece of data that you can retrieve from their servers, but you 
are able to customize almost everything. There is only one place 
that you have to query.

The [official documentation](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation)
can be found here.

### Downloading the Data
[official documentation](https://confluence.ecmwf.int/display/CKB/How+to+download+ERA5)

Notice that technical development of the ERA-5 services are all 
done on linux. This makes it so that a lot of the tools used to 
download the tools will only work on a linux machine. This 
includes some python packages that they use.

To download the data you have to first get an account. It is an 
easy process. You can then go to this [link](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview)
to download the data. Fill in the parameters that you want and 
then at the end click `Show API request`. This is the pythonic way 
of downloading the data. There is a python script here that can 
get the data from the request through their official downloading 
method called ERA5_webscraper.py. That program will send a request 
to their servers which will prepare it. The preparation process 
can take some time. After the program will download it. The 
program is designed to download 1 year of data for 1 attribute at 
a time. Program is taken from [this page](https://confluence.ecmwf.int/display/CKB/How+to+convert+NetCDF+to+CSV)

To run the program there is some preliminary steps that you have 
to take described on the webpage and in the header comments in the 
file. 

This download process can take a while to complete. (~2 hours per 
5 years per attribute)

### Era5-Land Downloaded Data

| Attribute Name                    | Short Name    | Units   |     |
|-----------------------------------|---------------|---------|-----|
| 2m temperature                    | T2M           | Kelvin  |     |
| Wind speed vectorized             | v10m, u10m    | m/s     |     |
| soil temperature level 1-3        | st1, st2, st3 | Kelvin  |     |
| surface solar radiation downwards | rad           | J/m^2   |     |
| total precipitation               | totprec       | m       |     |
| volumetric soil water layer 1-3   | sw1, sw2, sw3 | m^3/m^3 |     |
| 2m dewpoint temperature           |               | Kelvin  | new |
| Surface pressure                  |               | Pa      | new |

Note the temperature levels and layers are a predetermined depth 
range. 0-7 cm for level 1, 7-28 cm for level 2, 28-100 cm for 
level 3. We will be averaging station data at 20cm, 50cm, 100cm.

Note that humidity would be calculated using pressure, temperature,
and 2m dewpoint temperature. It would become a derived value.

[Documentation for attributes](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview)

## <a name="caspar"></a>
## CaSPAr
CaSPAr is the Canadian Surface Prediction Archive, which is made 
in conjunction with several Canadian universities and Environment 
Canada. 


### Downloading the Data
To download the data you can follow the instructions
[here.](https://github.com/julemai/CaSPAr/wiki/How-to-get-started-and-download-your-first-data)
You will have to create at least a couple accounts, one for CaSPAr 
itself and one for Globus. Once you send your request you will 
recieve an email with a link to the data in the Globus file 
sharing system. To download this data directly to your computer 
you will need to install a version of Globus Connect Personal. It 
is offered for Windows, Linux, and macOS. 
[Download link.](https://www.globus.org/globus-connect-personal)
Once the software is downloaded, and you have given access to one 
of your drives or folders in your drive you go back to the browser 
Globus file share and once you have both file locations set up you 
can press `start` to start the file transfer process.


This is something that the executable is unable to be downloaded 
onto government computers due to firewalls and compartmentalization 
computer. If you are able to run an executable in a drive with 
permissions then it is able to operate as per its documentation.


### Datasets
We are able to access several reanalysis products through casper. 
One of which we will do our comparison with is the HRDPS, or the 
High Resolution Deterministic Prediction System, which provides 
forecasts for Canada. Direct, unfiltered data can be accessed
[here.](https://dd.weather.gc.ca/model_hrdps/continental/2.5km/00/)
These files are quite large since it covers all attributes and all 
of Canada. I would recommend the subset generator tool that can be 
found [here.](https://caspar-data.ca/caspar)

[HRDPS readme](https://eccc-msc.github.io/open-data/msc-data/nwp_hrdps/readme_hrdps-datamart_en/)


### Downloaded HRDPS Data

Note these were chosen somewhat arbitrarily to test the data 
download process.

| Attribute Short Name | Attribute Description               | units           |
|----------------------|-------------------------------------|-----------------|
| HRDPS_P_FB_SFC       | Downward solar flux                 |                 |
| HRDPS_P_LA_SFC       | Latitude                            | Decimal Degrees |
| HRDPS_P_LO_SFC       | Longitude                           | Decimal Degrees |
| HRDPS_P_PR_SFC       | Forecast: Quantity of precipitation |                 |
| HRDPS_P_TT_10000     | Forecast: Air temperature           |                 |
| HRDPS_P_UU_10000     | Forecast: U component of wind       |                 |
| HRDPS_P_VV_10000     | Forecast: V component of wind       |                 |


## <a name="station-data"></a>
## Station Data
There are several ways to access our own weather station data to 
use for comparison against Merra and Era datasets. One of the 
easiest ways to do through is through the use of the historical 
data links found [here](https://mbagweather.ca/historical/CSV/). This 
link gets semi-regularly updated from the mySQL database which 
holds all the data in a queryable format. These links provide 
csv formatted data.

To download the data from a query to use for analysis, it is best 
to write a mySQL query that directly places the output into a csv. 
This can be by following this syntax:

```SQL
SELECT * FROM data_60
INTO OUTFILE 'output-data.csv'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
```

The directory that will output the file is 
`C:\ProgramData\MySQL\MySQL Server 8.0\Data\historical` on the 
remote server. You are able to add directories in the 
`\historical` directory to clean up that location.

You can find more information on the weather station attributes 
and units in the file `Data-Definition-Table.xlsx`.

#### Missing Data
Holland has significant missing data from `2018-03-12 17:00` to 
`2018-04-20 15:00`

There has also been some preprocessing that has been done on the 
2022 data that was used. The current database has preprocessing 
done on it, but the csvs that are hosted on the server do not have 
any preprocessing done to it.

### Station Data Used
| Attribute Name                    | Units   |
|-----------------------------------|---------|
| AvgAir_T                          | Celsius |
| AvgWS                             | m/s     |
| AvgWD                             | Degrees |
| RH                                | %       |
| Soil_TP5_TempC - Soil_TP100_TempC | Celsius |
| SolarRad                          | MJ/m^2  |
| TBRG_Rain or Pluvio_Rain          | mm      |
| Soil_TP5_VMC - Soil_TP100_VMC     | %       |
| press_hPa                         | hPa     |

Note for wind direction, 0 and 360 degrees is true north.
Note when available use Pluvio for measuring precipitation.

Other attributes taken from our data table

| Attribute Name | Table Name  | Units |
|----------------|-------------|-------|
| Station ID     | StnID       |       |
| Station Name   | StationName |       |
| Latitude       | LatDD       |       |
| Longitude      | LongDD      |       |
| TMSTAMP        | Time stamp  |       |
| Elevation      | Elevation   | m     |


## File Format of Compiled Data
It is good to notice that while the human-readable format exists, 
it is not the most efficient in terms of space and speed. If you 
are needing to do large amounts of processing work on the data, and 
you are running into physical limitations, then it may be required 
to instead use the raw data provided. The xarray python library is 
able to do operations on netCDF files extremely efficiently. The 
downside to using the raw data is that it is fragmented, by day 
for Merra-2, and by attribute and year for ERA5 Land.

The data is compiled into a file with the columns StnID, 
StationName, Latitude, Longitude, 
Elevation, StationData, MerraData, EraLandData. There will be 1 
row for every hour, for every weather station, for 5 years. The 
years used were from 2018 to 2022 inclusive. It is important to 
note that since both the Merra-2 and ERA5-Land data sets are based 
on a grid, the latitude and longitude coordinates of the weather 
station is not exactly the center of the grid. This also means 
that there can be several mappings to one grid if weather stations 
are sufficiently close together. There will be a separate csv for 
every attribute that the analysis is done on.

#### Analysis
The statistical analysis done on the columns will be root square 
mean error. This will happen per station, per month for the 
ability to create human-readable data that can easily be charted. 
There will also be columns made for every row to have the 
individual root square mean error. The function to calculate the 
root square mean error is 
[math.dist](https://docs.python.org/3/library/math.html#math.dist)
which is used to calculate the distance between two points. The 
equation is equivalent to
`sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))`.

Given two vectors with n dimensions (ie a column of size n) this 
function will return the root square mean error.

#### Time Shift
Merra2 and Era5 are both in UTC while our station data is in 
central time. This means that in the winter our station time will 
need to be offset by 6 +- 1 hours and 6 hours in the summer.

Because of this timeshift the first and last day of the data will 
be discarded. This is because our data will not be perfectly 
aligned with the data provided from Merra-2 and Era5.

A note on time change for the weather stations. Normally in 
Manitoba time change will happen by skipping the hour between 2 am 
and 3 am in the spring, and in the winter from 2 am to 1 am. 
Weather stations will only skip the hour once they make a 
connection to send data. This can be day in some cases. The 
weather stations will update their own local time using their 
internal clock but there is zero consideration for time zone 
corrections. This is a problem for trying to align the data 
perfectly with data that UTC time. Especially if the time skip 
happens a full day after the timezone incident. Our current method 
of dealing with this is to remove any days of data that is 
incomplete and to note that days around the time change in the 
spring and winter may have off by one inaccuracies.  

## Tracing the Data
The program `make_combined_csv.py` is used to take data from all 3 
data sources and create a singular data source. This data results 
are stored in the output directory where you run 
`make_combinged_csv.py`, which is `./make_combined_csv/output` in 
this repository. The CSVs that are created by that process store 
information on the actual station, the equivalent data on that 
hour for merra and era 5. The files are sorted by attribute. One 
row in the file represents an hour time frame. It stores the 
station data, reanalysis data unaltered, metadata, 
difference, and square error. This is for both merra and Era 5. 
The calculation for error is `stn_data - reanalysis_data`. The 
calculation for square error is `(stn_data - reanalysis_data)^2`.

Since the amount of significant figures in the CSVs is quite a lot 
you can use `truncate_decimals.py` to limit the number of decimals 
stored in each value.

From the combined csvs the program `get_graphable_data.py` can 
further process the data by mapping the data to specific ways that 
can be graphed. In particular, `get_line_chart_data`, averages the 
data over a month for one particular station. Calculating the 
root-mean-square error. This data can then be charted to see the 
rmse over time.

## <a name="data-correction"></a>
# A Very Detailed Look into the Data Correction Process

## Raw Data
Raw data is taken directly from our database, with a time change 
to change the timezone to UTC. UTC is the same timezone which 
Merra and Era5 operate on. Outliers were removed from the raw data.
There have been outliers removed from the database if they pass 
certain thresholds. (Mark: I cannot speak to the precise effects 
of these as this was done before my time. Probably though it is what 
is in `NewCleaner/apply_qa.py`) 

Further outlier detection was done to remove outliers that were 
inside seasonal norms. An analysis was done on the 4 closest 
neighbors for every station, and if that stations value for its 
attribute was over a certain threshold then the value was 
considered an outlier. This removed some clearly rough stations 
and outliers that can be seen in the original graphs generated, 
before the data cleaning occurred. The thresholds for each 
attribute can be found below. Certain attributes could not be 
predicted if they were an outlier by the values of their neighbors,
so it is possible that those attributes contain more outliers 
than others. The file that does this cleaning is 
`Satellite-Comparison/make_combined_csv/clean_csvs.py`. 

| Attribute  | Threshold | Unit    |
|------------|-----------|---------|
| Air Temp   | 7         | Celsius |
| Wind Speed | 10        | m/s     |
| Pressure   | 15        | hPa     |
| Humidity   | 20        | %       |
| Solar Rad  | 1         | MJ/m^2  |

Merra and Era 5 Land data were both converted to the units which 
are measured by the Manitoba weather stations. Most values 
were just a simple unit conversation. Notably some values 
had to be calculated and used different attributes in the 
calculated value. This may introduce more error into the final 
result. Wind is vectorized in both Merra and Era 5 Land which 
needed to be converted to a scalar value. Relative Humidity needed 
to be calculated in both Merra and Era 5 using specific humidity. 
This was done using this equation sourced 
[here](https://www.omnicalculator.com/physics/relative-humidity).
Merra and Era 5 both gave readings of surface pressure, when the 
weather stations report their pressure readings as pressure at sea 
level. Thus, a conversion using temperature was done on pressure 
values for Merra and Era 5. The conversion used this
[formula](https://keisan.casio.com/exec/system/1224575267).

Data was then merged with metadata and a csv file was created for 
every attribute. These files can be found in `/output`.

## Initial Statistical Analysis

The statistics are calculated on the files in 
`Satellite-Comparison/make_combined_csv/output` using the program 
in `Satellite-Comparison/make_combined_csv/get_stats.py`. 

The first of the statistics calculated is a total Root 
Mean-Square-Error which takes the square error for each hour, 
means the square error, and takes the root. Every attribute is 
returned its own RMSE value.
This is calculated for 
the raw data and any corrections attempted on the data. 

The next statistic is the monthly Root Mean-Square-Error. This 
takes the square error in one calendar month over the whole 5-year 
period, takes the average, then takes the root. This process is 
done 12 times for every month in the year. 12 values is returned 
for every attribute analyzed.

The last statistic is the Correlation Coefficients. This is 
calculated using the pandas library `corr()` function call. We use 
the Pearson method.
[link](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.corr.html)

## Monthly Mean Error Correction

This correction takes the average of the error for each month over 
all 5 years. Then subtracts the average error from every analysis 
attribute value
that is in that month. The new value is considered the corrected 
value. The output of the mean correction is put into 
`monthly_mean_error.json`

## Linear Regression Error Correction

This correction is also done to every month in the year, for 5 
years. The data is grouped by month. Then the data is fed into the 
sci kit learn linear regression algorithm. 
(`linear_model.LinearRegression`) The X axis for the 
linear regression is the attribute value given by the analysis 
product. The Y axis, or output of the equation is the expected 
value. It is trained on all the data. Once the data is fitted, the 
coefficients are exported to `monthly_linear_regression.json`. After 
the corrected value for each hour is given by putting the analysis 
attribute value into the generated equation as the x value. 


## <a name="random-forest"></a>
## Random Forests

Random Forests are made using the Sci Kit Learn 
`sklearn.ensemble.RandomForestRegressor` class. There are two 
initial methods I used to make the random forest. 

The first method is using the attribute and specific metadata for 
input for the random forest. The attributes are as follows: 
Analysis latitude, analysis longitude, analysis attribute value, 
elevation, month, hour, distance between analysis location and 
station location. The output is the station attribute value at 
that time.

The second method is using the same metadata as input but 
including 6 reanalysis attributes, instead of the one that was 
being predicted. The thought process behind this decision is that 
when a weather model gives a prediction for weather we do not know 
where error is being introduced. We expect for the model to have 
some concept of the tight woven relationship between different 
weather attributes. Then if say there was a large error in 
humidity it may imply that there is a large error in temperature 
as well. By including all attributes we get a better understanding 
of what sort of inputs indicates how the model is over or 
underestimating the attribute we are studying.

An alternative to both of these models is to rather train it to 
predict the error between the expected and given attribute value 
rather than the actual correct value. This drastically changed 
variables importance and slightly decreased the RSME.

Month and hour are both integer values which are the day of the 
month and hour of the day respectively. 

Testing values are randomly sampled from the set, with 20% being 
put aside for testing. This is the equivalent of 1 years worth of 
data. The random values are seeded so that for all different 
iterations of the random forest will have the same random split of 
testing and training data. The other 80% is dedicated to training 
the random forest. 

Separate trees have to be trained for both Merra and Era 5, as 
well as separate forests for every attribute being studied. This 
means for the 6 attributes that are being studied 12 random 
forests will have to be made. 

Similarly to the other correction models the data used to train 
the models is in `output`. A single joined file with only 
the required data was made to speed up loading times. 

Once every forest is generated, a series of test statistics is 
automatically ran to evaluate the effectiveness of the model. 
Those statistics are Root mean squared error, R-2 score, Spearman 
correlation, Pearson correlation, and feature importance expressed 
as a percentage. These stats are used as a type of benchmark. 
Every forest has special hyperparameters that can used to adjust 
the model. The parameters we focused on for tuning the model were 
n_estimators, max_features, and min_samples_leaf. These were 
chosen based on information from 
[this website](https://www.analyticsvidhya.com/blog/2015/06/tuning-random-forest-model/)
. When tuning hyperparameters options were iterated through each 
of the 3 parameters until all combinations were tested. Notice 
that these models were ran on a machine with an Intel(R) Xeon(R) 
W-11855M CPU @ 3.20GHz processor and 16 GB of ram. The models that 
were tested were pushing the boundaries of this machine.

#### Non Attribute Random Forest Parameters
| Attribute                     | Type  | Used in final Model |
|-------------------------------|-------|---------------------|
| Month                         | int   | yes                 |
| Hour                          | int   | yes                 |
| Latitude                      | float | yes                 |
| Longitude                     | float | yes                 |
| Elevation                     | float | yes                 |
| Distance from closest Station | float | no                  |

## Random Forest Tuning
Random forests are made in the get_corrections.py file.

The random forest is made using the scikit learn python library 
using the RandomForestRegression class. We are using a regression 
random forest instead of a classification since our output is a 
float. 

For the first method of creating the random forest, that is where 
the only weather attribute fed into the model is the one we are 
studying, the initial testing showed this preformed only marginally 
better than the other 2 methods of correcting the data.
Merra average air temperature testing showed to have a RMSE 
of 2.09 when the output was the expected temperature, and 1.96 
when the output was the error or correction. The best preforming 
model was when the n_estimators=150, max_features=None, and
min_samples_leaf=1. My hypothesis why it was most effective when 
max_features=None (that is when all attributes are used in every 
tree) is that it relied so heavily on temperature that when 
temperature was not included in the trees the prediction ability 
dropped drastically.

The second method where 6 attributes are fed into the model had 
better results. For Merra average air temperature has a RMSE of
1.24 in the best result. The best preforming 
model was when the n_estimators=100, max_features=0.5, and
min_samples_leaf=1. This is when predicting the error and not the 
expected temperature. These parameters were ran on Era5 as well 
and produced a model with a RMSE of 1.08.

It is very possible that the effectiveness of the model could be 
improved by increasing the n_estimators, but I would need to run 
these models on a better computer first.

To improve performance the model was 
[pickled](https://docs.python.org/3/library/pickle.html) to reduce 
the time of regenerating the model everytime. A seed was used to 
generate the test, train data to ensure the same data was 
collected the saved model. However, the saved models are quite 
large, being almost 18 GB. Any forests with more than 60 trees 
cannot fit onto the 16 GB of RAM on the standard government laptop.
Models can be created in RAM with 100 trees (the default option) 
however only incremental gains are realized using 100 trees over 50.
In total there would be roughly 250 GB of stored random forest 
models.



# Code Overview

## make_combined_csv
This directory holds the program that takes the raw Merra and Era 
data as well as the station data and then merges it all into a 
series of csv files, found in `output/precleaning`. There are then 
programs that clean this data and moves it to `output`. Then 
programs can extract and modify data from `ouput`.

### make_combined_csv.py
Program that fetches and combines the data from Merra, Era and 
our station data. Calling the main function will run all the 
functions necessary to extract the data and combine it. Some data 
processing is done by default, such as unit conversions, changing 
cumulative data to hourly, and other operations. The data being 
fetched relative path needs to be added in `data_dir` variable. 
The data directory shape is described below

<!-- language: lang-none -->
<pre>
data
 |-> station-csv
    |-> MBAg-60min-2018.csv
    |-> MBAg-60min-2019.csv
    |-> ...
 |-> conpernicus
    |-> ERA5-Land
        |-> v10m2022
            |-> data.nc
        |-> v10m2021
            |-> data.nc
        |-> ...
        |-> d2m2018
            |-> data.nc
 |-> merra
    |-> M2T1NXSLV
        |-> MERRA2_400.tavg1_2d_slv_Nx.20180101.SUB.nc
        |-> ...
    |-> M2T1NXLND
        |-> MERRA2_400.tavg1_2d_lnd_Nx.20180101.SUB.nc
        |-> ...
    |-> M2T1NXLND_2
        |-> MERRA2_400.tavg1_2d_lnd_Nx.20180101.SUB.nc
        |-> ...
    |-> M2T1NXRAD
        |-> MERRA2_400.tavg1_2d_rad_Nx.20180101.SUB.nc
        |-> ..
</pre>

`station-csv` holds the data for our observed stations data. It 
needs to keep the file naming scheme shown above where only the 
year changes. `conpernicus` holds all the data from Era5. This is 
the format of the unzipped data when downloading the data from the 
conpernicus data portal. The `merra` directory holds the merra 
data. Each of the subdirectories represents a database. Inside 
each file is a nc file for every for the timeframe which was 
downloaded. There are sometimes when the files downloaded have a 
different file name, such as having 401 instead of 400. The 
program in `merra\util\rename_files.py` can replace the filenames 
to make it uniform. You just need to set the directory where you 
want the program running should run to.

Alternatively the naming schemes can be changed by changing the 
functions `get_merra_filename`, `get_era_filename`, and 
`get_stn_filename`.

To only compile files for certain attributes the lists stn_attrs, 
era5_attrs, merra_attrs can be modified. Only the attributes in 
those lists will be fetched and processed.

Once the program is complete `/output/pre_cleaning` with have 1 
file per attribute. The csv structure is described below.

| Column Description      | Air Temp Column Name | Column Name Regex |
|-------------------------|----------------------|-------------------|
| UTC time                | time                 | time              |
| Station ID              | StnID                | StnID             |
| Station Name            | Station              | Station           |
| Attribute value         | stn_AvgAir_T         | stn_attr_name     |
| Station longitude value | stn_long             | stn_long          |
| Station latitude value  | stn_lat              | stn_lat           |
| Location Id             | location             | location          |
| Elevation at station    | elevation            | elevation         |
| Era5 longitude          | era5_long            | era5_long         |
| Era5 latitude           | era5_lat             | era5_lat          |
| Era5 attribute value    | era5_AvgAir_T        | era5_attr_name    |
| Merra longitude         | merra_lon            | merra_lon         |
| Merra latitude          | merra_lat            | merra_lat         |
| Merra attribute value   | merra_AvgAir_T       | merra_attr_name   |
| Merra Error             | merra_err            | merra_err         |
| Merra Square Error      | merra_sqr_err        | merra_sqr_err     |
| Era5 Error              | era5_err             | era5_err          |
| Era5 Square Error       | era5_sqr_err         | era5_sqr_err      |

If you are running this on newly downloaded merra data, and you are 
getting errors that a file does not exist, please run 
`merra/util/rename_files.py` which will rename the files to make 
them uniform to be able to be read by this program.

### clean_csvs.py
Once the data is in pre_cleaning then running `clean_csvs.py` can 
clean a portion of the csvs. Note that it does not move all the 
files over from pre_cleaning, and you need to copy some 
files over that are not cleaned. If you copy all the files over 
and skip the ones that already exist then that works. Cleaning is 
based off of neighbors values and thresholds.

### get_graphable_data.py
This takes the data from output and processes it in ways that 
makes it ready to be graphed. Different functions will process 
graphs for different reasons. The three 
functions that can be run are get_line_chart_data_daily, 
get_map_data, get_line_chart_data.

### get_stats.py
This does analysis on the data and returns stats such as RMSE, 
correlation, ect. Change the type of stats that are retrieved by 
changing the enum's value which is passed to print_stats.

### graph_line_chart.py
This file contains data for several methods which generate graphs 
which summarizes the data for the MERRA and ERA5-Land model work.
There are 3 functions that are the main functions that you would 
call in this file. Namely, `generate_all_graphs` which generate 
all mean graphs, and station graphs. Notice that the files when 
generated are generated outside this repo. You can change where 
they are generated by modifying the variables `root_path` in 
graph_mean and graph_all_stns. Alternatively you can change the 
line where it saves the figure (close to the end of the function) 
with `plt.show()` to show and not save it. Get averaged time is a 
function that can show the averages of all stations for varying 
time resolutions, ranging from 1 hour to a month. Similarly, it is 
saving to a file outside this directory. The final function 
creates nice looking graphs which shows the mean bias as a scatter 
plot for all 5 years. These charts are not saved and rather are shown.

### trucate_decimals.py
Simple program which reads the data from output, and then 
truncates the data to a specified decimal point.

## error_correction
Directory which holds programs that are dedicated to building of 
models used to correct merra and era5.

### get_corrections.py
This program contains methods to correct merra and era5 data in 
several machine learning ways. In general there is 
random forests, for merra, era5, with all the attributes, or 
just the one being corrected, with all the attributes in the 
past x hours, or just the hour being predicted. We can treat 
random forest as a black box which is trained on input of size n 
and gives a single output (the corrected weather value at location 
x, and time y). This file also contains methods to correct via 
linear regression which will create a file of all the 
coefficients. A main function was created to generate the linear 
regression data. The function called make_merra_era5_random_forest
() when given the right parameters will generate a random forest 
and then display statistics about that random forest. 

An important helper function is merge_files() this takes the 
individual attributes csv's and merges into one csv which the 
random forest will use. This is to reduce disk loading time during 
run time. This file can be seen in this directory called 
`random_forest_data.csv`. 

### gradient_boosting.py
A program which is used to generate corrections for merra and era 
using the stochastic gradient descent method. Simpley run the 
program to generate the results. The data is pulled from 
`random_forest_data.csv` to generate the model. Once the model is 
completed it will print out various statistics on the quality of 
the model. If you want to train using time fading, then when 
calling `load_data` set the parameter `is_time_faded=True`. 


### graph_monthly_stats.py
Used to generate prettier graphs for the paper using the results 
from the different models. Gets the information from the stats 
directory, and also saves the graphs in that directory. Run main 
to make new graphs. 


### neural_network.py
A rough version of the neural network code. The complete version 
is on amazon sagemaker studio. This code runs the neural network 
on the CPU. To use a gpu you will need to install CUDA which is 
not installed on any government devices. This program takes some 
time to run, and will print statistics after each epoch. This is 
mostly used to track performance rather than actually save a model 
to use in corrections later on. 

Note that neural network performance is similar to random forests, 
although my design was fairly trivial. Possible large improvements 
could have been made.

## merra
Small programs used to investigate merra data. Only important 
program is `util/rename_files.py` which will rename the downloaded 
files so that they can be read by `make_combined_csv.py`. This 
saves you from doing work by hand.

## util
Small utility programs.

### ERA5_stn_coords_converter.py
Program used to map stations to ERA5 coordinates. Rounds so that it 
snaps to the closest ERA5 coordinate grid.

### station_to_merra_mapping.py
Maps stations to merra coordinates. Based on the merra grid system.