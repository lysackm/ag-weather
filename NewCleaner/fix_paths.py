import log
from config import temp_folder
from util import each_file, delete, rename, try_rename, drop_suffix, drop_prefix, RenameException
from pathinfo import PathInfo, PathException
import pandas

def run(directory):
	log.main("fix paths")
	for path in each_file(directory):
		if not (path.lower().endswith(".txt") or path.lower().endswith(".dat")):
			delete(path, "path doesn't end in .txt or .dat")
			continue
		
		# delete daily summary files
		if path.endswith("_Daily_Summary.txt"):
			delete(path, "path ends in '_Daily_Summary.txt'")
			continue
		
		# delete glenlea files
		if 'glenlea' in path.lower():
			delete(path, "path contains 'glenlea'")
			continue
		
		# delete AG files
		if 'AG' in path:
			delete(path, "path contains 'AG'")
			continue

		# delete potato files
		if 'potato' in path.lower():
			delete(path, "path contains 'potato'")
			continue

		# delete template files
		if 'template' in path.lower():
			delete(path, "path contains 'template'")
			continue

		# rename WG_RTMC to WG24
		if 'WG_rtmc' in path:
			new_path = path.replace('WG_rtmc', 'WG24')
			path = rename(path, new_path, "WG_rtmc to WG24")
		if 'WG_RTMC' in path:
			new_path = path.replace('WG_RTMC', 'WG24')
			path = rename(path, new_path, "WG_RTMC to WG24")

		# rename crb09dry files to carberry
		if 'crb09dry' in path.lower():
			new_path = path.replace('crb09dry', 'carberry')
			path = rename(path, new_path, "crb09dry to carberry")

		# rename melita files to bede
		if 'melitawado' in path.lower():
			new_path = path.replace('melitawado', 'bede')
			path = rename(path, new_path, "melitawado to bede")

		# rename melita files to bede
		if 'melita' in path.lower():
			new_path = path.replace('melita', 'bede')
			path = rename(path, new_path, "melita to bede")

		# rename swan files to swanvalley
		if 'swan' in path.lower() and 'swanvalley' not in path.lower() and 'swanlake' not in path.lower():
			new_path = path.replace('swan', 'swanvalley')
			path = rename(path, new_path, "swan to swanvalley")

		# rename spraguelake files to spraguelakebog
		if 'spraguelake' in path.lower() and 'spraguelakebog' not in path.lower():
			new_path = path.replace('spraguelake', 'spraguelakebog')
			path = rename(path, new_path, "spraguelake to spraguelakebog")
		
		# attempt to extract the path info, deleting invalid paths
		try:
			pathinfo = PathInfo(path)
		except PathException:
			delete(path, "invalid path format")
			continue
		
		# normalize pathinfo to lowercase station, uppercase WG
		pathinfo.station = pathinfo.station.lower()
		pathinfo.wg = pathinfo.wg.upper()
		
		# rename the file to the new path if it doesn't already exist
		# (sometimes data for a year is split into multiple files)
		new_path = pathinfo.render()
		try_rename(path, new_path, "normalize path name")

if __name__ == "__main__":
	import sys
	try:
		folder = sys.argv[1]
	except IndexError:
		folder = temp_folder
	run(folder)
