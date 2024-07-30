# Production Server Split File Patch

## Purpose
This is a program which is supposed to take the incoming dat file 
data and write it to the partner data. 

## Features
- Needs to be able to run every 15 minutes
- Need to be able to detect new changes
  - Hopefully to be able to see the difference between a total 
    file change and a final line being appended to the file. 
    - This way we could only take and write the last line
    - Pretty unavoidable to read the whole file in, there are ways 
      to read just the last line but its not clean code
    - Could hash the whole document without the last line, if the 
      old .dat file matches the hash then we don't need to push the 
      data (would need a partner who takes the .dat file straight 
      up or else have a hash for each file)
    - GOAL: want to push corrections to partner files
  - Alternatively could just always replace the whole file, but 
    would want to see if this is efficient enough
- Fast
  - Would be nice if it took just a couple of minutes
- Transparent
  - Have a log which records errors with descriptive messages if 
    something goes wrong, and hopefully some way to fix it
- Clean readable code
  - Well documented and commented code which is understandable 
    by a non-technical person
- expandable
  - Have easy procedures which can be expanded upon when new partners 
    and stations are added
- Reversible
  - Never modify older data and do not remove original .dat files
  - Be able to "turn on" split files again and have it updated


## Research and Design
- 3 groups of split files
  - 24
  - 60
  - 15
- split file will have a file its pointing to for reading data and 
  writing data
- Because we want to load each df once, and not overwhelm the 
  system it would make the most sense to load a .dat file, then 
  load it into the appropriate locations. If we store the metadata 
  for each partner then we would have to loop through this data 
  everytime we do an operation, but if we index it by .dat file we 
  would have to add a partner to potentially 120x3 metadata rows.

## Benchmarks
loading .dats files: 17.3 seconds
loading and saving 11 times: 84.5 seconds

# partner_data.json Documentation

## Introduction

The `partner_data.json` file contains all the necessary metadata 
to move partner data from the .dat files which are taken from the 
loggernet system. Data comes in from the weather station through 
the Campbell loggernet software. The raw data is deposited and 
stored in the .dat files located in the DAT (Source?) folder. The 
metadata here is a system to encapsulate the information inside 
the split files. This allows to have a single file that has all 
information needed to move the data from the .dat files to the 
partner file locations which is part of the servers file delivery 
service. This file can be edited using the guide below to extend 
the behaviour for new partners later added to the program. This 
will define what data the partners will receive and in what format.

## Introduction to JSON

The file is in a JSON format which is a type of data object which 
can be easily accessed programmatically but also easily readable 
with the correct visual formatting. JSON has 2 primary ways of 
storing information. Arrays and dictionaries. An array is an 
unordered list of values which are contained by square brackets `[]
`. To separate the values a comma (,) must be used. For example 

```json
[
  1,
  2,
  3
]
```
is a simple list of integers.

A dictionary is a map of one set of items to another set of items. 
This is called a key value pair, as the key maps to the value. In 
the case of the `partner_data.json` this is often an attribute and 
the value of the attribute. A dictionary is For example

```json
{
  "has_value": true,
  "how_many_values": 10,
  "name": "Winnie the Pooh"
}
```

There are different values that can be used in a JSON but the most 
important ones for our situation are booleans (`true` or `false`), 
strings (`"text encapsulated in double quotes"`) and ints (numbers 
like `12`). 


## partner_data.json format

A brief overview of how the json file is formatted is as follows. 
The base structure is a dictionary which maps the name of a 
partner to its properties. Inside each partner are a series of 
properties described in more detail below. If the data will be 
copied over then it will either have to have the property 
`copy_concatenated_stn_data` or `copy_individual_stn_data`. These 
describe if the partner wants the .dat file data in a single file 
or in separate files. These then link to further dictionaries 
which then hold properties for how this data is to be formatted and 
copied over to the partners.

# partner_data.json properties documentation

## Base Level Dictionary
Data format: A dictionary of `"Strings"` to dictionaries `{}`.

Expected data: The name of the partner which we are specifying the 
properties for.

Key required format: A unique string with a dictionary

Value required format: A dictionary

Example: 

```json
{
  "AGOL": {
    ...
  }
}
```

## Inside Partner Dictionary

### Key `"base_directory"`

[//]: # (TODO maybe changing the name of base_directory is worth 
it bc base_directory really seems to imply that its the value 
`C:\WWW\mbagweather.ca\www\Partners` when its really the directory 
appended to it)
Purpose: The partner directory after the base partner directory

Data format: `"String"`

Expected data: The directory from inside the partner folder (As of 
2024-07-05 `C:\WWW\mbagweather.ca\www\Partners`) to the folder 
which the partner data will be placed. 

Required data: The string must be a file that already exists in 
the base partners' folder. Must be the folder which you wish to 
write to.

Example: 
```json
{
  "base_directory": "AGOL"
}
```

### Key `copy_concatenated_stn_data`
Purpose: To indicate the desire to copy over .dat file data which 
has been combined into a single file. That is instead of having 1 
file per station, all stations would be in a single file. Inside 
this dictionary is where most of the metadata for a file is kept.

Value: A dictionary

Example:

```json
{
  "copy_concatenated_stn_data": {
    ...
  }
}
```

### Key `copy_individual_stn_data`
Purpose: To indicate the desire to copy over .dat file data with 
a single station in a single file. Inside 
this dictionary is where most of the metadata for the files is kept.

Value: A dictionary

Example:

```json
{
  "copy_individual_stn_data": {
    ...
  }
}
```

## Dictionary in `copy_concatenated_stn_data`

### Key `"15"`, `"60"`, `"24"`
Purpose: A key which indicates if you want to copy over a single 
file of data at the 15 minute, 60 minute, 24 hour, time frequency. 
You can have choose 0-3 of these options depending on which data 
you would like to transfer over to the other folder. These can 
either be a dictionary or a list of dictionaries. It can be a 
dictionary if only 1 file in each time is needed, or a list of 
dictionaries if several formats of each time is needed. 

Example:

```json
{
  "15": {
    ...
  },
  "60": [
    ...
  ],
  "24": {
    ...
  }
}
```

## Dictionary in `"15"`, `"60"`, or `"24"`

Note: these dictionaries can either be directly under `"15"`, 
`"60"`, or `"24"`, or in a list under `"15"`, `"60"`, or `"24"`.

### Key `"destination_file"`
Purpose: The name of the file in the partners directory

Value: `"String"`

Example: 

```json
{
  "destination_file": "hourly-data.csv"
}
```

### Key `"previous_rows"`
Purpose: The number of previous rows which need to be taken and 
moved to the partners' directory. The amount of time this actually 
is changes depending on the time frequency of the data set which 
is being moved. For example if the `24` data set is chosen and 
`previous_rows: 10`, then the previous 10 days would be taken.

Value: `integer`

Example:

```json
{
  "previous_rows": 10
}
```


### Key `"stations`
Purpose: A list of the `StnID`'s which are fetched and used in the 
makeup of the resulting file. Only used in concatenated station 
data. These station IDs can be found in the `station_metadata.csv` 
file. The IDs should be unique.

Value: List of `integers`

Example:

```json
{
  "copy_concatenated_stn_data": {
    "stations": [
      544,
      253,
      574
    ]
  }
}
```

### Key `"column_mapping`
Purpose: This creates a mapping from an internal column names to 
the external column name. Internal column names are based on the 
dat file definition table, while external column names are what 
are the column names for the file written to the partner. If 
`"column_mapping"` exists as a characteristic then only the mapped 
columns will exist in the resulting dataset. This means it can be 
used to only use specific columns in a partners recieved data. 

Value: Dictionary of `"Strings"`

Expected Value: Every key in the dictionary should be a column in 
the respective data definition table. 

Example:

```json
{
  "column_mapping": {
    "AvgAir_T": "Average Air Temperature",
    "MinAir_T": "Minimum Air Temperature",
    "MaxAir_T": "Maximum Air Temperature"
  }
}
```


### Key `"lower_thresholds"`
Purpose: This is to define a singular threshold such that if any 
of the data values are outside the threshold range then it will be 
removed from the partners output file. This is a lower bound 
defined to remove data where x < threshold.

Value: `Integer`

Expected Value:
A mapping of internal column names, as displayed in the 
Data-Definition-Table document, to an integer. 

Example:

```json
{
  "column_mapping": {
    "AvgAir_T": -50,
    "AvgRH": 0,
    "AvgWD": 0
  }
}
```


### Key `"upper_thresholds"`
Purpose: This is to define a singular threshold such that if any 
of the data values are outside the threshold range then it will be 
removed from the partners output file. This is a upper bound 
defined to remove data where x > threshold.

Value: `Integer`

Expected Value:
A mapping of internal column names, as displayed in the 
Data-Definition-Table document, to an integer. 

Example:

```json
{
  "column_mapping": {
    "AvgAir_T": 50,
    "AvgRH": 100,
    "AvgWD": 360
  }
}
```


### Key `"transformations`
Purpose: To apply some form of transformation to individual 
columns. If the value is numerical then it is multiplied to every 
value in the column. This can be used for simple unit conversions. 
If the value is a string then every value in the column will be 
set to be the string.

Value: Dictionary of `"Strings"` mapping to `"String"` or 
`Numerical` values

Expected Values:
Keys must be a column name. 

Example:

```json
{
  "transformations": {
    "AvgWS": 3.6,
    "MaxWS": 3.6,
    "some_column": "NaN"
  }
}
```

### Key `date_format`, `time_format`, and `timestamp_format`
Purpose: To format the time in the columns DATE, TIME, and TMSTAMP,
respectively. Uses the `strftime` function. The format of dates 
which can be used in this function can be described here: 
[link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
Any combination of these options can be set, if no format is given 
then the default behaviour will be used.

Value: `"String"`

Example:

```json
{
  "date_format": "%m/%d/%Y",
  "time_format": "%H:%M",
  "timestamp_format": "%m/%d/%Y %H:%M"
}
```


### Key `"direct_copy"`
Purpose: To indicate whether individual station files 
should be a one to one copy of the .dat files. If true, all 
processing is ignored and the file is just copied to the new 
directory. Only used for copy_individual_stations.

Value: `Boolean`

Example:

```json
{
  "direct_copy": true
}
```

### Key `"header"`
Purpose: Formatting a header for specific cases. Can remove the 
header, or to write a custom header from a file to the start of 
the partner file before writing data. If it is false then no 
header is added to the file, otherwise it should be a name of a 
file. This file should be inside the directory partner_headers, 
under the directory `base_directory`. For example if `"header": 
header.txt` for AGOL, then `partner_headers/AGOL/header.txt` 
should be a file.

Value: `false` or `"String"`

Expected Value: If a string a valid location as described in purpose.

Example

```json
{
  "header": "header60.txt"
}
```


### Key `"column_format`

