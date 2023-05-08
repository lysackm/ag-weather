import log
from config import temp_folder, database_host, database_port, database_user, database_pass, database_name
from pathinfo import PathInfo
from util import each_file
from columns import *
import MySQLdb
import re
from warnings import filterwarnings

# suppresses MySQLdb warnings (like "duplicate entry" warnings, since duplicate entries are already ignored)
filterwarnings("ignore", category=MySQLdb.Warning)

def run(directory):
	log.main("load database")
	
	conn = MySQLdb.Connection(
		host=database_host,
		port=database_port,
		user=database_user,
		passwd=database_pass,
		db=database_name
	)

	curs = conn.cursor()
	
	def execute(sql):
		log.query(sql)
		curs.execute(sql)
		curs.nextset()

	# inserts files into the database
	# priority is a boolean:
	# if true, insert only the updated ("2_") station files
	# if false, insert only the non-updated station files
	# since we are using the IGNORE modifier in SQL statements, data with the same primary key will be ignored
	# so as long as we insert the updated station files first, those will take priority
	def insert_files(priority):
		for path in each_file(directory):
			# fix_paths.py ensures this won't raise exceptions
			try:
				pathinfo = PathInfo(path)
			except:
				continue

			# if priority = true, skip the files without "2_"
			if priority and not pathinfo.updated_station:
				continue
			# if priority = false, skip the files with "2_"
			if not priority and pathinfo.updated_station:
				continue

			# make sure we're using the appropriate table
			if pathinfo.wg:
				table = f"data_wg_{pathinfo.rate}"
			else:
				table = f"data_{pathinfo.rate}"

			try:
				# ensure path can be read in SQL statement
				path = path.replace("\\", "\\\\")

				# need to use lines terminated by \r\n on windows systems
				load_data_infile_statement = f"""
					LOAD DATA INFILE '{path}'
					IGNORE INTO TABLE {table}
					FIELDS TERMINATED BY ','
					ENCLOSED BY '"'
					ESCAPED BY '"'
					LINES TERMINATED BY '\r\n'
					IGNORE 0 ROWS;
					"""

				execute(load_data_infile_statement)
			except Exception as e:
				print(f"Couldn't insert {path} into database. File ignored.")
				print(e)

			# commit the changes to the DB after each file
			conn.commit()

	# insert files from updated stations (filenames with "2_") first
	insert_files(priority=True)

	# insert the remaining files
	insert_files(priority=False)

	# close the cursor
	curs.close()

	# close the connection to the database
	conn.close()
