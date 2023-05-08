# Using the two programs
The first program is HistoricalCleaner which is used for creating the historical database with the 2008-2020 dataset. The second program is NewCleaner which is used for inserting new data into the historical database. The programs were written in Python 3.8.0, but it will likely work in any Python 3 install. The script also needs MySQLdb and pandas installed.  Running `pip install mysqlclient pandas` should install both.

Various settings are in config.py, notably the settings for the database connection and the location of the raw data folder and temporary workspace folder. These settings will need to be set up separately for each program. Once these are set up appropriately, executing run.py will clean any data present in the raw data folder, and merge it into the database. 

Folders containing raw data files can be placed in the program's data folder, but the temporary workspace will need to be configured to the secure directory provided by MySQL, which during development was `C:\ProgramData\MySQL\MySQL Server 8.0\Data\historical\clean`. Note that the ProgramData directory is hidden on Windows 10, so you may need to make hidden folders visible to access it. 

The following SQL statements have been used to setup database during testing:

```
CREATE DATABASE historical;
CREATE USER 'mbag'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO 'mbag'@'localhost' WITH GRANT OPTION;
```

In addition, you may need to make the following edits to the my.ini configuration file:

* Set the secure_file_priv variable to null (secure_file_priv = "")
* Disable binary logging (include "disable_log_bin=" under the [mysqld] tag)
	* MySQL log files can become cumbersome (10+ 1GB files)
* Increase the size of the buffer table size (innodb_buffer_pool_size=2048M)
	* Only needed for updates in HistoricalCleaner's fix_database.py

After making any change to the MySQL configuration file, you will need to reset the MySQL Server though Windows Services (Windows button + R, type "services.msc") for them to take effect.

For debugging or testing, reset.py is also provided, which simply clears the database of all tables.  Use this with caution!

While running, the script will produce the following log files:

* deleted.csv lists deleted files
* modified.csv lists file modifications
* renamed.csv lists files and their new names
* log.csv lists all of these operations together, in the order they occurred

Each one of these files also includes a column listing the reason for the operation.

* query.sql lists every SQL query executed
* wg60_24.csv lists (day, station) pairs for which the summed WG60 precipitation does not equal the WG24 total

# Detailed Overview
When initializing the database with the 2008-2020 historical dataset, use HistoricalCleaner. When adding new data into the database, use NewCleaner. The programs can be run by executing run.py in their respective directories after its config file has been setup.

## Database initialization - HistoricalCleaner
Execution starts with run.py, which simply created and destroys the temporary folder.  The only time the original data is interacted with at all is the single copy command in run.py.  After this, all mentions of 'delete', 'rename', etc. refer to the temporary folder.
After this, seven passes are performed over the data (plus one data merging step), each with their own Python file.

* fix_bespoke.py
	* Delete several folders that contain no useful data
	* Rename MelitaWADO to bede
	* Rename shilo files
	* Rename swanlake files
	* Rename somerset files
	* Rename portage files
	* Rename gladstone files
	* Rename steinbach files
	* Rename treherne files
	* Rename sterose files
	* Remove extra columns from early carman files
	* Delete 10 minute early carman files
	* Delete carberry files with duplicate data
	* Delete files with invalid data
	* Delete mafrd test files
	* Remove preheader for 2008 portage file (contains typo)
	* Remove preheader for 2008 stpierre file
	* Fix 2009 winkler file with trailing whitespace
* fix_paths.py
	* Delete paths not ending in '.txt' or '.dat'
	* Delete daily summary files
	* Delete glenlea files
	* Delete AG files
	* Rename crb09dry files to carberry
	* Rename WG_RTMC to WG24
	* Rename melitawado/melita to bede
	* Rename swan to swanvalley
	* Attempt to extract the path info, deleting invalid paths
	* Normalize pathinfo to lowercase station, uppercase WG
	* Rename the file to the new path (if a file with the new path name doesn't already exist)
* merge_files.py
	* Combine data from updated station files where multiple files for the same year exist
		* 2016 summer sterose (15, 60, 24)
		* 2017 fall/winter sterose (24)
		* 2017 summer sterose (24, WG15)
		* 2017 summer grandview (24)
* fix_pre_headers.py
	* Try to extract the header info
	* Assume files without pre-headers are correct
	* Delete empty files with zero columns
	* Delete files without 'TOACI1' in their pre-header
	* Delete files with pre-headers not matching their names
		* i.e. the file is named 'altona15.txt', but the pre-header contains 'pipelake15'
* fix_headers.py
	* Extract the file's header, or guess based on the number of columns if there is none
	* Apply the appropriate fixing function
		* For WG files, rename column 'AccTot_NRT' to 'AccTotNRT'
		* Otherwise, apply the fixes from fix_headers_{15,60,24}.py
	* Normalize the files to have the ideal header, padding missing columns and re-arranging as needed
* fix_columns.py
	* Coerce each column to the correct types
		* Every column is either a date, an integer, or a real number
		* This ensures that the database will load every row correctly, as well as discarding rows with formatting errors
	* Move Pluvio_Rain to TBRG_Rain and set Pluvio_Rain to null in files before the corresponding WG file first appears
	* For 60 min files, also move Pluvio_Rain24RT to TBRG_Rain24RT2 and set Pluvio_Rain24RT to null 
	* Set any column which is all zeros to null
	* Add the original path and the station name to the beginning of each row
	* Apply quality assurance thresholds by calling apply_qa.py
		* Applies monthly thresholds to air temperature and soil temperature columns
		* Applies generic thresholds to all non-temperature columns
		* Removes rows with TMSTAMPs pre-2007
		* Removes rows with StnID less than 200 or greater than 800
* load_database.py
	* Create the appropriate tables if they do not exist
		* Primary key for each table is (TMSTAMP, Station)
	* Load each file into the appropriate table
		* Prioritizes data from updated station files (filenames containing "2_") by loading these files first
* fix_database.py
	* Delete rows with invalid TMSTAMPs (post-2021)
	* Update HmMaxRS where missing data has been incorrectly cast as a date
	* Locate places where wg60 and wg24 disagree
		* Sum WG60 AccRT_NRT totals for each day, and compare with the WG24 total recorded
		* Write rows which differ to wg60_24.csv
	* Update letellier and swanlake Pluvio_Rain columns since there is no WG data for these stations

## Insertion of later files - NewCleaner
After the database has been initialized, new data can be inserted to the database by copying the raw files into the NewCleaner data folder, setting up config.py, and then executing run.py. It uses the following files from HistoricalCleaner with changes listed:

* fix_paths.py
* fix_pre_headers.py
	* No longer makes adjustments that were necessary for 2008 files
* fix_headers.py
* fix_columns.py
	* No longer makes changes to precipitation columns for years before WG data is available
	* No longer nulls columns that contain only zeros
* load_database.py
	* No longer attempts to create the database's tables

# Other Files
## pathinfo.py
Defines the PathInfo class.  Given a path, PathInfo(path) parses the path with a regular expression, and creates a structure with all the different components separated.  More explanation is available in the file itself.

## headinfo.py
Similar to PathInfo, this defines a HeadInfo class which parses the headers of a file into structured data.

HeadInfo(path).num_headers is the number of header rows present.  Should be 0, 1, or 2.
HeadInfo(path).header is the actual header, it gives names to each column of data.
HeadInfo(path).pre_header is the short row that sometimes comes before the actual header.
HeadInfo(path).num_columns is the number of columns of data present.  This may not be the same as the header's length.

## columns.py
Defines the ideal columns for each rate, as well as the headers to guess for files which are missing a header.

## apply_qa.py
Called by fix_columns.py to set data outside of thresholds to null. For air temperature and soil temperature columns, thresholds are determined by monthly TMSTAMP.

## clean_old_carman.py
Called by fix_bespoke.py to remove extra columns from early years (2008-2010) of Carman 60 min and 24 hr data.

## config.py
Collects various constants used.  Mainly for database login and data paths.

## log.py
Code to write the various CSV log files.

## util.py
Various utility functions which aren't specific to this script and don't belong anywhere else, mostly file manipulation functions.

## reset.py
Drop all tables.  Good for debugging, to make sure things are running from scratch, but again, be careful with this!

# Known Issues
* The logging in general could be more detailed
