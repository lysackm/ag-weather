import log
from config import temp_folder
import pandas as pd
from headinfo import HeadInfo
from pathinfo import PathInfo
from util import each_file, delete, has_duplicates
from fix_headers_15 import fix as fix_15
from fix_headers_60 import fix as fix_60
from fix_headers_24 import fix as fix_24
from columns import *

# return the header the file likely has
# i.e. the actual header, or a guess if there is none
def likely_header(pathinfo, headinfo):
	# the file has a header present, just return it
	if headinfo.header not in (None, []):
		return headinfo.header
	
	# for WG files, use the pre-made guesses
	if pathinfo.wg:
		if headinfo.num_columns == 12:
			return ideal_columns_wg
		
		if headinfo.num_columns == 11:
			return columns_wg_11
		
		if headinfo.num_columns == 3:
			return columns_wg_3
		
		raise Exception("WG file has the wrong number of columns " + str(headinfo.header))
	
	# for 15-minute files, the missing columns are always at the end
	if pathinfo.rate == 15:
		return ideal_columns_15
	
	# for 60-minute files, columns are deleted from the middle if there are 27-37 columns
	if pathinfo.rate == 60:
		if 27 <= headinfo.num_columns <= 37:
			return ideal_columns_60_27_to_37
		
		return ideal_columns_60
	
	# for 24-hour files, columns are deleted from the middle if there are 28-29 columns
	if pathinfo.rate == 24:
		if 28 <= headinfo.num_columns <= 29:
			return ideal_columns_24_28_to_29

		if headinfo.num_columns == 42:
			return ideal_columns_24_42

		return ideal_columns_24

# return the ideal header for the file
def ideal_header(pathinfo, headinfo):
	if pathinfo.wg:
		return ideal_columns_wg
	
	if pathinfo.rate == 15:
		return ideal_columns_15
	
	if pathinfo.rate == 60:
		return ideal_columns_60
	
	if pathinfo.rate == 24:
		return ideal_columns_24

# make df.columns == header, or fail loudly
# missing columns are padded with blanks
def normalize_header(df, ideal_header):
	actual_columns = set(df.columns)
	ideal_columns = set(ideal_header)
	
	if has_duplicates(df.columns):
		raise Exception("Duplicate columns")
	
	# extra columns that aren't in the ideal header
	# this should always be an empty set
	extra_columns = actual_columns - ideal_columns
	if extra_columns != set():
		raise Exception("Unknown extra columns: ", extra_columns)
	
	# missing columns that need to be padded
	missing_columns = ideal_columns - actual_columns
	
	# empty column to use as padding
	blank_column = [""] * len(df.index)
	for column_name in missing_columns:
		df.insert(0, column_name, blank_column)
	
	# select the ideal header
	return df[ideal_header]

def run(directory):
	log.main("fix headers")
	for path in each_file(directory):
		# path must be well formed, fix_paths.py ensures this
		pathinfo = PathInfo(path)
		
		# header must be well formed, fix_pre_headers.py ensures this
		headinfo = HeadInfo(path)
		
		# extract the file's header, or guess based on the number of columns if there is none
		file_header = likely_header(pathinfo, headinfo)
		
		# sometimes there are more data columns than header columns
		# these can safely be deleted, but pandas defaults to aligning things poorly:
		# A,B
		# 1,2,3
		# would be parsed so that 2 would be in A's column, and 3 in B's
		# this is backwards from what we want, so we pad the columns on the right
		# we'll delete these extra columns soon
		while len(file_header) < headinfo.num_columns:
			file_header.append("delete_me")
		
		# header=None tells pandas not to try parsing the header from the file
		# we just did that, so we use names=file_header to tell pandas the real header
		# then skiprows=headinfo.num_headers will cause the header rows to be ignored
		try:
			df = pd.read_csv(
				path,
				header = None,
				names = file_header,
				skiprows = headinfo.num_headers
			)
		except:
			print(f"Could not open {path} as pandas dataframe. File ignored.")
			continue

		# delete the padding columns we added before, along with their data
		# this is always null data, so no worries about losing anything important
		while "delete_me" in df.columns:
			del df["delete_me"]
		
		# apply the appropriate fixing function
		if pathinfo.wg:
			df.rename(columns = {
				"AccTot_NRT": "AccTotNRT",
			}, inplace = True)
		else:
			if pathinfo.rate == 15:
				df = fix_15(df, path)
			elif pathinfo.rate == 60:
				df = fix_60(df, path)
			elif pathinfo.rate == 24:
				df = fix_24(df, path)
		
		# if the dataframe is gone, then the file got deleted and we're done
		if df is None:
			continue
		
		try:
			# normalize the dataframe to have the ideal header, padding and re-arranging columns as needed
			df = normalize_header(df, ideal_header(pathinfo, headinfo))
		except Exception as e:
			print(path)
			print(e)
			continue
		
		# write the dataframe back to the CSV file
		# without index=False, the rows will start with 1,2,3...
		df.to_csv(path, index=False)
