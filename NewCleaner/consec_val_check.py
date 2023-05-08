from config import consec_folder
import log
from util import try_delete, delete_folder_contents, try_create_dir
import send_email
import traceback

# the passes
import download_data
import fix_paths
import fix_pre_headers
import fix_headers
import fix_columns
import consecutive_value_qa

try:
    # create data folder if it doesn't already exist
    try_create_dir(consec_folder)

    # delete consec folder contents from last run
    delete_folder_contents(consec_folder, "clear consec folder contents")

    # delete the log from last run
    try_delete("consec_val.csv")

    # download the data from website
    download_data.run(consec_folder)

    # clean the data and perform consecutive value checking
    fix_paths.run(consec_folder)
    fix_pre_headers.run(consec_folder)
    fix_headers.run(consec_folder)
    fix_columns.run(consec_folder, consec_check=True)

    consecutive_value_qa.check_logs()

    delete_folder_contents(consec_folder, "clear consec folder contents")
except Exception as e:
    email_subject = "An unexpected error occurred checking consecutive values with NewCleaner's run.py. Error code is attached."

    # get a traceback of the error to include in the email as attachment
    tb = traceback.format_exc()
    f = open("tb_error.txt", "w")
    f.write(tb)
    f.close()

    send_email.run(subject=email_subject, files=["tb_error.txt"])
    print(e)