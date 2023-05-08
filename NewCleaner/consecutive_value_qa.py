import pandas
import log
from util import each_file, delete_folder_contents, delete
from config import consec_folder
from pathinfo import PathInfo
import send_email
import perform_consec_updates
from consec_val_thresholds import thresholds_15, thresholds_60, thresholds_24

# reads the log to determine SQL updates to remove consecutive unchanged values
# sends an email about the updates and then calls for the updates to occur
def check_logs():
    log.main("check logs")
    log_file = open("consec_val.csv", "r")

    # list of lines to include in email attachment
    lines = []

    # list of SQL update statements to perform
    updates = []

    # initialize variables
    current_station = ""
    current_rate = ""
    current_column = ""
    start = ""

    # read through the file and create list of updates to perform and summarize them for email
    for line in log_file:
        line = line.replace("\n", "")

        if line.startswith("Station"):
            # format of line is "Station: ABC rate: XY"
            # splitting by spaces gets us a list: ["Station:", "ABC", "rate:", "XY"]
            split_result = line.split(" ")

            # station is in position 1
            current_station = split_result[1]
            # data rate is in position 3
            current_rate = split_result[3]
        elif line.startswith("Column"):
            # format of line is "Column: column_name: num_values_changed"
            split_result = line.split(": ")

            # column is in position 1
            current_column = split_result[1]
        elif line.startswith("Start"):
            # format of line is "Start: timestamp,value"
            split_result = line.split(": ")
            temp = split_result[1]
            split_result = temp.split(",")

            # starting timestamp is in position 0
            start = split_result[0]
        elif line.startswith("End"):
            # format of line is "End: timestamp,value\n"
            split_result = line.split(": ")
            temp = split_result[1]
            split_result = temp.split(",")

            # ending timestamp is in position 0
            end = split_result[0]

            # value is in position 1
            value = split_result[1]

            # generate the SQL statement
            cur_update = f"""
                UPDATE data_{current_rate}
                SET {current_column} = NULL
                WHERE Station = '{current_station}' AND
                TMSTAMP BETWEEN '{start}' AND '{end}';
            """
            # add to list of updates to perform
            updates.append(cur_update)

            # email info the update that will occur
            lines.append(f"{current_station} {current_rate} {current_column}: {start} to {end} with value {value}")
        elif line.startswith("Error"):
            # include any error lines in email
            lines.append(f"{line} Station: {current_station}, data rate: {current_rate}")
        elif line.startswith("Invalid"):
            # include any error lines beginning with invalid
            lines.append(line)
        else:
            continue

    log_file.close()

    if len(lines) > 0:
        # open a file to write summer to
        f = open("consec_val_summary.txt", "w")

        # write every line to the summary
        for cur_line in lines:
            f.write(cur_line + "\n")

        # close the file
        f.close()

        # email summary of updates
        email_subject = "Consecutive value updates were made. Summary file attached."
        send_email.run(subject=email_subject, files=["consec_val_summary.txt"])

        # perform the updates
        perform_consec_updates.run(updates)

# replaces unchanged consecutive values in a dataframe with null

# df: dataframe being altered
# column: current column being considered
# threshold: if this many consecutive rows have the same value, set them all to null
# data_rate: 15, 60, or 24
# consec_zero_allowed: boolean that holds whether to retain any number of consecutive 0s (True) or not (False)
# ignore_winter: boolean that holds whether winter (nov 1-mar 31) dates should be ignored
# ignore_overnight: boolean that holds whether to ignore 0s for overnight times (7pm-6:59am)

def replace_consecutive(df, column, threshold, data_rate, consec_zero_allowed, ignore_winter, ignore_overnight):
    # if the threshold is greater than the number of rows, we're done
    if threshold > len(df.index):
        return df

    # create temporary column storing the number of consecutive values at that point
    # initialize every row's count at 1
    df["Count"] = 1

    # track of the number of changes made (used for logging)
    num_values_set_to_null = 0

    # list of pairs of tmstamps changed (start and end of sequence of unchanged consecutive values)
    tmstamps = []

    if data_rate == 15:
        expected_time_diff = 15
    elif data_rate == 60:
        expected_time_diff = 60
    elif data_rate == 24:
        # number of minutes in a day
        expected_time_diff = 60 * 24
    else:
        log.consec_val(f"Invalid data rate of {data_rate} given to replace_consecutive().")
        print(f"Invalid data rate of {data_rate} given to replace_consecutive().")
        return df

    # data rate should never be 24 if ignore_overnight is True
    if data_rate == 24 and ignore_overnight:
        log.consec_val("Argument ignore_overnight=True for 24 hour data given to replace_consecutive().")
        print(f"Data rate of {data_rate} given to replace_consecutive() with ignore overnight parameter.")

    # current highest count of consecutive values, initially 1
    highest_count = 1

    # generate consecutive counts
    # iterate over the rows (top to bottom)
    # index is row number, row is current row of data
    for index, row in df.iterrows():
        # skip the first row since its count should always be 1
        if index == 0:
            continue

        # if consecutive 0s are fine, don't bother generating counts
        if pandas.notna(row[column]) and row[column] == 0 and consec_zero_allowed:
            continue

        # timestamp of current row
        time_cur_row = pandas.to_datetime(row["TMSTAMP"])

        # year in current row's timestamp
        year = time_cur_row.year

        # for any data rate, greater than this is considered winter
        winter_start = pandas.to_datetime(f"{year}-11-01 00:00:00")

        # for any data rate, a TMSTAMP less than/equal to this is considered winter
        # note: winter start and end have the same year, but that is correct
        # since the current row's timestamp may be at the start or end of the year
        winter_end = pandas.to_datetime(f"{year}-04-01 00:00:00")

        # if winter month (Nov1-Mar31) consecutive values should be ignored for this column,
        # don't generate counts
        if ignore_winter and (time_cur_row > winter_start or time_cur_row <= winter_end):
            # set count for current row to 0 to prevent next row's count from becoming 2 if consecutive
            df.loc[index, "Count"] = 0
            continue

        # if overnight (7pm-7am) consecutive values <= 0.01 should be ignored for this column
        # don't generate counts
        if ignore_overnight and pandas.notna(row[column]):
            # ignore values <= 0.01 overnight
            if row[column] <= 0.01:
                # for 60 min data, tmstamp between 20:00 and 08:00
                if data_rate == 60 and (time_cur_row.hour >= 20 or time_cur_row.hour <= 8):
                    # set count for current row to 0 to prevent next row's count from ever becoming 2
                    df.loc[index, "Count"] = 0
                    continue

        # if theres a row of missing data, this can cause an error
        # if that happens, just skip the current row
        try:
            # timestamp of previous row
            time_prev_row = pandas.to_datetime(df.loc[index-1, "TMSTAMP"])
        except:
            continue

        # total number of minutes between cur and prev timestamps
        mins_between = pandas.Timedelta(time_cur_row - time_prev_row).total_seconds() / 60.0

        # boolean that holds whether minutes between timestamps is the expected time difference (based on data rate)
        timestamps_consecutive = mins_between == expected_time_diff

        # if value of the column is the same as the row above and timestamps are consecutive
        if pandas.notna(row[column]) and pandas.notna(df.loc[index-1, column]) and row[column] == df.loc[index-1, column] and timestamps_consecutive:
            # this row's count becomes prev row's count + 1
            new_count = df.loc[index-1, "Count"]+1
            df.loc[index, "Count"] = new_count

            # update highest count
            highest_count = max(highest_count, new_count)

    # number of consecutive values to null
    remaining_values_to_null = 0

    # only need to replace values if highest count meets threshold
    if highest_count >= threshold:
        # set values that lead to an above threshold count to null
        # iterate over dataframe (bottom to top)
        # index is row number, row is current row of data
        for index, row in df[::-1].iterrows():
            # if out of values to null
            if remaining_values_to_null == 0:
                # check if number of consecutive values is at/above threshold
                if row["Count"] >= threshold:
                    # get the number of consecutive values that should be set to null
                    remaining_values_to_null = row["Count"]
                    # this is the last value in the sequence of unchanged
                    tmstamps.insert(0, ("End", row["TMSTAMP"], row[column]))
            # if there are values to set to null
            if remaining_values_to_null > 0:
                # set current row's value to null
                df.loc[index, column] = None
                if remaining_values_to_null == 1:
                    # this is the first value in the sequence of unchanged consecutive values
                    tmstamps.insert(0, ("Start", row["TMSTAMP"], row[column]))
                # decrement count of remaining values to set to null
                remaining_values_to_null -= 1
                # increment count of values changed
                num_values_set_to_null += 1

    # remove temporary count column
    df.drop(columns=["Count"], inplace=True)

    # log the total number of values changed in this column
    if num_values_set_to_null > 0:
        log.consec_val(f"Column: {column}: {num_values_set_to_null}")

        # for each timestamp that is the beginning/end of an unchanged consecutive sequence
        for tm in tmstamps:
            # log the tmstamp, the unchanged value, and whether the timestamp is the start or end of a sequence
            start_or_end = tm[0]
            timestamp = tm[1]
            value = tm[2]
            log.consec_val(f"{start_or_end}: {timestamp}", value)

    return df
# end replace_consecutive()

# takes a dataframe and then for each column, calls to have consecutive values replaced
# the threshold for unchanged consecutive values to be replaced depends on the data rate and column name
def consecutive_value_qa(cur_df, data_rate):
    # get the columns and thresholds based on data rate
    # col_thresh_dict is a key-value dictionary that maps columns to their thresholds
    if data_rate == 15:
        col_thresh_dict = thresholds_15
    elif data_rate == 60:
        col_thresh_dict = thresholds_60
    elif data_rate == 24:
        col_thresh_dict = thresholds_24
    else:
        log.consec_val(f"Invalid data rate of {data_rate} given to replace_consecutive().")
        print(f"Invalid data rate of {data_rate} given to replace_consecutive().")
        return cur_df

    # select each column from the list, and call the consecutive value check function
    for col in col_thresh_dict:
        # get the correct threshold for the current column
        thresh = col_thresh_dict[col]
        # call the consecutive value function with the correct parameters based on the column name
        try:
            if col in ("Pluvio_Rain", "TBRG_Rain"):
                # allow consecutive zeroes for precipitation columns
                cur_df = replace_consecutive(
                    df=cur_df,
                    column=col,
                    threshold=thresh,
                    data_rate=data_rate,
                    consec_zero_allowed=True,
                    ignore_winter=False,
                    ignore_overnight=False)
            elif "VMC" in col:
                # ignore winter months for soil moisture columns
                cur_df = replace_consecutive(
                    df=cur_df,
                    column=col,
                    threshold=thresh,
                    data_rate=data_rate,
                    consec_zero_allowed=False,
                    ignore_winter=True,
                    ignore_overnight=False)
            elif col == "SolarRad" or (col == "AvgRS_kw" and data_rate == 60) or (col == "TotRS_MJ" and data_rate == 60):
                # ignore overnight for solar radiation columns
                cur_df = replace_consecutive(
                    df=cur_df,
                    column=col,
                    threshold=thresh,
                    data_rate=data_rate,
                    consec_zero_allowed=False,
                    ignore_winter=False,
                    ignore_overnight=True)
            else:
                # all other columns do not allow consecutive zeroes, do not ignore winter months, or overnight times
                cur_df = replace_consecutive(
                    df=cur_df,
                    column=col,
                    threshold=thresh,
                    data_rate=data_rate,
                    consec_zero_allowed=False,
                    ignore_winter=False,
                    ignore_overnight=False)
        except Exception as e:
            # if something goes wrong, don't crash the program
            # just add a note in the log with an error message indicating the column check that failed
            log.consec_val(f"Error with column {col} consecutive value check.")
            log.consec_val(e)

    return cur_df
# end consecutive_value_qa()






