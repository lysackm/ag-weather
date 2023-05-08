data_folder = "data" # folder to copy raw data from
temp_folder = r"C:\ProgramData\MySQL\MySQL Server 8.0\Data\historical\clean" # folder to use as a temporary workspace
consec_folder = "consec_check"
merge_temp_folder = "merge_temp"

# database connection info
database_host = "localhost"
database_port = 3306
database_user = "mbag" # manitoba agriculture
database_pass = "password" # change this for production

database_name = "historical" # name of the database to use

keep_temp_folder = False # delete the temporary data
# keep_temp_folder = True # leave the temporary data instead of deleting it, useful for debugging
