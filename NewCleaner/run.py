from config import data_folder, temp_folder, keep_temp_folder
import log
from util import try_delete, delete, copy, delete_folder_contents, try_create_dir
import traceback
import send_email

# the passes
import download_data
import fix_paths
import fix_pre_headers
import fix_headers
import fix_columns
import load_database

try:
    # create data folder if it doesn't already exist
    try_create_dir(data_folder)

    delete_folder_contents(data_folder, "delete data folder contents from last run")
    try_delete(temp_folder, "delete temp folder from last run")

    # download the data from website
    download_data.run(data_folder)

    copy(data_folder, temp_folder, "create temporary version of raw data to modify")

    fix_paths.run(temp_folder)
    fix_pre_headers.run(temp_folder)
    fix_headers.run(temp_folder)
    fix_columns.run(temp_folder, consec_check=False)
    load_database.run(temp_folder)

    if not keep_temp_folder:
        delete(temp_folder, "clean up temp folder")
except Exception as e:
    email_subject = "An unexpected error occurred adding new data into the database with NewCleaner's run.py. Error code is attached."

    # get a traceback of the error to include in the email as attachment
    tb = traceback.format_exc()
    f = open("tb_error.txt", "w")
    f.write(tb)
    f.close()

    send_email.run(subject=email_subject, files=["tb_error.txt"])
