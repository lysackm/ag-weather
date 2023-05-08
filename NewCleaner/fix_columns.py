import log
from config import temp_folder, merge_temp_folder, consec_folder
import csv
import pandas as pd
import numpy as np
from pathinfo import PathInfo
from util import each_file, delete, drop_prefix
from apply_qa import *
import datetime
import os
from consecutive_value_qa import consecutive_value_qa

# given a column name, return the SQL datatype
def column_dtype(column_name):
	if column_name == "TMSTAMP" or column_name.startswith("Hm"):
		return "DATE"
	if column_name in ("RECNBR", "StnID"):
		return "INTEGER"
	return "REAL"

# consec_check is a boolean whether to run consecutive value checking QA
# it is not used by run.py
def run(directory, consec_check):
	log.main("fix columns")

	for path in each_file(directory):
		# fix_paths.py ensures this won't raise exceptions
		try:
			pathinfo = PathInfo(path)
		except:
			print(f"Could not retrieve path info for {path}. File ignored.")
			delete(path, f"Could not retrieve path info for {path}")
			continue

		# fix_headers.py ensures this won't raise exceptions
		try:
			df = pd.read_csv(path)
		except:
			print(f"{path} could not be read into pandas dataframe. File ignored.")
			delete(path, "error reading into pandas dataframe")
			continue

		for column in df.columns:
			type = column_dtype(column)

			# coerce each column to the correct types
			if type == "DATE":
				# errors=coerce tells pandas to replace badly-formatted dates with NULLs
				df[column] = pd.to_datetime(df[column], errors="coerce")

			elif type == "INTEGER":
				df[column] = pd.to_numeric(df[column], errors="coerce") # same as above

				# this is really tricky, some integer columns are formatted as 123.0
				# first we round, then convert to Int64
				# note the capital I, pandas' Int64 type allows nulls, but 'int64' does not
				# copy=False is just an optimization, this will just be slower without it
				df[column] = df[column].round().astype("Int64", copy=False)
				# errors=ignore?

			elif type == "REAL":
				# similar to the above, but float64 allows NULLs as NaN values
				df[column] = pd.to_numeric(df[column], errors="coerce")
				df[column] = df[column].astype("float64", copy=False)

		# if there is ever a blank line in the data file, it can create a row with a null timestamp
		# so remove any rows with a null TMSTAMP
		df.dropna(subset=["TMSTAMP"], inplace=True)

		# the chance of a column being 0 for an entire season is extremely low
		# if that is the case, it's an error, replace with NULLs
		# the .fillna(True) is required because comparing can return NaN
		# NaN == NaN is not True or False, it's Nan, so we replace NaNs with True

		# sometimes 0 is used repeatedly to show a missing value (ie. carberry's Pluvio)
		# however, we will only perform this check if there are at least 60 days of data
		if not pathinfo.wg:
			num_rows = len(df.index)

			# 5760 = 4 * 24 * 60 (4 reports per hour, 24 hours in a day, 60 days)
			# 1440 = 24 * 60 (24 reports a day, 60 days)
			if (pathinfo.rate == 15 and num_rows >= 5760) or (pathinfo.rate == 60 and num_rows >= 1440) or (pathinfo.rate == 24 and num_rows >= 60):
				for column in df.columns:
					if all((df[column] == 0).fillna(True)):
						df[column] = pd.NA

		# we are going to remove data with a TMSTAMP older than 45 days
		# get current datetime
		dt = datetime.datetime.now()

		# previous number of days of data to keep
		days_to_keep = 45

		# subtract days from current datetime to determine min datetime to keep
		min_dt = pandas.to_datetime(
			f"{dt.year}-{dt.month}-{dt.day} {dt.hour}:{dt.minute}:00") - pandas.Timedelta(days=days_to_keep)

		# only keep the rows before min datetime
		df = df[df.TMSTAMP >= min_dt]

		# record the file of origin (useful for updating database later)
		# shortened path is just the path without info about temporary folder and where the temp folder is located
		# shortened_path = drop_prefix(path, f"{directory}" + os.path.sep)
		# df.insert(0, "Path", shortened_path)

		# for new cleaner, no need to keep path info
		df.insert(0, "Path", pd.NA)

		# insert column into dataframe
		df.insert(1, "Station", pathinfo.station)

		# create a Date column which is TMSTAMP minus data rate
		if pathinfo.rate == 15:
			df.insert(2, "Datetime", df["TMSTAMP"] - pandas.Timedelta(minutes=15))
		elif pathinfo.rate == 60:
			df.insert(2, "Datetime", df["TMSTAMP"] - pandas.Timedelta(minutes=60))
		elif pathinfo.rate == 24:
			df.insert(2, "Date", df["TMSTAMP"] - pandas.Timedelta(days=1))

		# apply QA thresholds
		if not pathinfo.wg:
			if pathinfo.rate == 15:
				df = qa_15(df)
			elif pathinfo.rate == 60:
				df = qa_60(df)
			elif pathinfo.rate == 24:
				df = qa_24(df)

		# write it all back
		# no header needed because we know it's the ideal header now
		# represent NAs as NULL because MySQL sets missing values to default value
		# (what default value is depends on data type)
		df.to_csv(path, index=False, header=False, na_rep="NULL")

		if not pathinfo.wg and consec_check:
			# call for consecutive value checking
			log.consec_val(f"Station: {pathinfo.station} rate: {pathinfo.rate}")
			consecutive_value_qa(df, data_rate=pathinfo.rate)
			# add a blank line after each station
			# log.consec_val()

