import log
from config import temp_folder
from pathinfo import PathInfo
from headinfo import HeadInfo
from util import each_file, drop_suffix, delete, file_empty

def run(directory):
	log.main("fix pre-headers")

	for path in each_file(directory):
		# fix_paths.py ensures that this will always work
		pathinfo = PathInfo(path)
		
		# try to extract the header info
		try:
			headinfo = HeadInfo(path)
		except Exception as e:
			delete(path, "invalid header or pre-header", e)
			continue

		# delete file if its empty
		if file_empty(path):
			delete(path, "file was empty")
			continue

		# assume files without pre-headers are correct
		if headinfo.pre_header in (None, []):
			continue
		
		# delete empty files with zero columns
		if headinfo.num_columns in (None, 0):
			delete(path, "empty file")
			continue
		
		# delete files without 'TOACI1' in their pre-header
		if headinfo.pre_header[1 - 1] != 'TOACI1':
			delete(path, "pre-header does not contain 'TOACI1'")
			continue
		
		# station as given by the path
		path_station = pathinfo.station

		# swan valley stations often contain just "swan" in pre-header
		# so we want to consider "swan" a match as well
		if path_station == "swanvalley":
			path_station = "swan"
		
		# station as given by the pre-header
		# well, it's just the lowercased pre-header, but this is an easy way of checking it
		file_station = "".join(headinfo.pre_header).lower()
		
		# delete files with pre-headers not matching their names
		# slightly different for 2008 files
		if path_station not in file_station:
			delete(path, "pre-header station does not match file path station", headinfo.pre_header[1], pathinfo.station)
			continue

if __name__ == "__main__":
	try:
		import sys
		folder = sys.argv[1]
	except IndexError:
		folder = temp_folder
	run(folder)
