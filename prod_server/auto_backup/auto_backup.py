# auto_backup.py
#
# Created by: Mark.Lysack@gov.mb.ca
# Date: 2024-09-04
#
# The purpose of this program is to be able to run a semi automated backup of the dat files on the prod server. There
# are several ways that a backup can be made using this program. This means that it will copy the data over from the
# dat directory as well as modifying the dats in the dat directory, to make the files smaller. The features are as
# follows:
#   - Save data as the last n lines
#   - Save data from a specific date
#   - Use a regex to select the files operated on, this regex is applied to the directory of the dats specified
#   - Use a file with names of the dats which should be operated on. These files will be appended to the dats directory
#     specified
#   - Choose to keep May 1st in the dat file
#   - Automatically creates a backup of the data
#   - A simple text based UI to select these configurations1


import datetime
import glob
import os
import re
import shutil


def get_current_date_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H %M %S')


class CreateBackup:
    def __init__(self, file_regex, files, dats_dir, kp_splt_st_dt):
        self.file_regex = file_regex
        self.files = files
        self.dats_dir = dats_dir.replace("\\", "/")
        self.backup_dir = "./auto_backup/dat_backups_" + get_current_date_string()
        self.keep_split_start_date = kp_splt_st_dt
        # May 1st. Change if the start date for the split files is different
        self.split_start_date_regex = r"[0-9]{4}-05-01 [0-9]{2}:[0-9]{2}:[0-9]{2}"

    def create_backup_dir(self):
        if not os.path.isdir(self.backup_dir):
            os.mkdir(self.backup_dir)

    def get_dat_files(self):
        dat_files = []
        if self.file_regex != "":
            dat_files = self.get_dat_files_regex()
        if os.path.isfile(self.files) and self.files != "":
            dat_files += self.get_dat_files_list()
        return dat_files

    def get_dat_files_regex(self):
        files = glob.glob(self.dats_dir + "**/*.dat", recursive=True)
        dat_files_filtered = []
        for file in files:
            if re.search(self.file_regex, file):
                dat_files_filtered.append(file)

        return dat_files_filtered

    def get_dat_files_list(self):
        dat_files = []
        with open(self.files, "r") as file:
            for line in file:
                dat_files.append(self.dats_dir + line.rstrip())
        return dat_files

    def backup_file_from_dat_file(self, dat_file):
        dest_dir = self.backup_dir
        dat_file_std_file_sep = dat_file.replace("\\", "/")
        dat_file_suffix = dat_file_std_file_sep.replace(self.dats_dir, "")

        for dir_extension in dat_file_suffix.split("/")[:-1]:
            if not os.path.isdir(dest_dir + "/" + dir_extension):
                os.mkdir(dest_dir + "/" + dir_extension)
            dest_dir = dest_dir + "/" + dir_extension

        return self.backup_dir + "/" + dat_file_suffix

    def copy_dats(self):
        for dat_file in self.get_dat_files():
            backup_file = self.backup_file_from_dat_file(dat_file)
            shutil.copy(dat_file, backup_file)

    def backup_dats(self):
        self.create_backup_dir()
        self.copy_dats()

    def print_effected_dirs(self):
        print("printing dirs")
        if self.get_dat_files() is []:
            print("No chosen files.")

        for dat_file in self.get_dat_files():
            if not os.path.isfile(dat_file):
                print(dat_file + " is not a valid file")
            else:
                print(dat_file)

    def save_start_date(self, line):
        if re.search(self.split_start_date_regex, line[0:22]):
            return True
        else:
            return False


class CreateBackupSavePreviousRows(CreateBackup):
    # saved_days: variable which indicates how
    def __init__(self, file_regex, files, dats_dir, kp_splt_st_dt, previous_rows):
        super().__init__(file_regex, files, dats_dir, kp_splt_st_dt)
        self.previous_rows = previous_rows

    def clear_dat_data(self, dat_file):
        with open(dat_file, "r") as file:
            file_data = file.readlines()
            header = file_data[0:2]

            if self.previous_rows > len(file_data) - 2:
                data = file_data[2:]
            else:
                data = file_data[len(file_data) - self.previous_rows: len(file_data)]

            if self.keep_split_start_date:
                index = 2
                start_date = []
                for line in file_data[2:]:
                    if self.save_start_date(line) and len(file_data) - index > self.previous_rows:
                        start_date.append(line)
                    index += 1
                file_content = header + start_date + data
            else:
                file_content = header + data
            file_content = "".join(file_content)

        with open(dat_file, "w") as file:
            file.write(file_content)

    def clear_dats_data(self):
        dat_files = self.get_dat_files()
        for dat_file in dat_files:
            self.clear_dat_data(dat_file)


class CreateBackupSaveFromDate(CreateBackup):
    def __init__(self, file_regex, files, dats_dir, kp_splt_st_dt, start_datetime):
        super().__init__(file_regex, files, dats_dir, kp_splt_st_dt)
        if type(start_datetime) is datetime.datetime:
            self.start_datetime = start_datetime
        elif type(start_datetime) is str:
            self.start_datetime = datetime.datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        else:
            # undefined behaviour
            print("Date in unexpected format, please enter in format YYYY-MM-DD HH:mm:ss. Exiting the program.")
            exit(1)

    def clear_dat_data(self, dat_file):
        with open(dat_file, 'r') as file:
            file_data = file.readlines()
            header = file_data[0:2]
            data = []

            for line in file_data[2:]:
                # matches date format "YYYY-MM-DD HH-mm-00"
                if re.search('[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:00', line[0:22]):
                    line_datetime = datetime.datetime.strptime(line[1:20], '%Y-%m-%d %H:%M:%S')
                    if line_datetime >= self.start_datetime:
                        data.append(line)
                    elif self.keep_split_start_date and re.search(self.split_start_date_regex, line[0:22]):
                        data.append(line)

            file_content = header + data
            file_content = "".join(file_content)

        with open(dat_file, "w") as file:
            file.write(file_content)

    def clear_dats_data(self):
        dat_files = self.get_dat_files()
        for dat_file in dat_files:
            self.clear_dat_data(dat_file)


def get_user_backup_type():
    backup_type = False
    while backup_type != "1" and backup_type != "2":
        backup_type = input("For each file would you like to (1) save data after a date, or "
                            "(2) save the last n lines of the file? Enter 1 or 2 to continue: ")

        if backup_type != "1" and backup_type != "2":
            print("Unexpected input, please try again")
    return backup_type


def is_dats_dir_valid(dats_dir):
    valid_dir = True
    if dats_dir == "":
        return True

    if dats_dir[-1] != "/":
        print("Make sure your directory ends with a /")
        valid_dir = False

    if not os.path.isdir(dats_dir):
        print("This directory cannot be found.")
        valid_dir = False

    return valid_dir


def get_user_dats_dir():
    valid_dir = False
    dats_dir = ""
    while not valid_dir:
        dats_dir = input("Please type the absolute file directory to the dat files (default is C:/Campbellsci/Dats/)."
                         " Type your answer or press enter for default: ")
        valid_dir = is_dats_dir_valid(dats_dir)

        if dats_dir == "":
            if os.path.isdir("C:/Campbellsci/Dats/"):
                dats_dir = "C:/Campbellsci/Dats/"
                valid_dir = True
            else:
                print("C:/Campbellsci/Dats/ is an invalid path on this computer, try entering a valid directory")
                valid_dir = False

    return dats_dir


def get_user_dat_file():
    valid_file = False
    dat_file = ""
    while not valid_file:
        dat_file = input("If there is a file which has a list of dat files which you want to backup, type the name of "
                         "the file or press enter to skip: ")

        if dat_file == "":
            return ""

        if not os.path.isfile(dat_file):
            print("The file specified does not exist, try entering the complete file directory.")
        else:
            valid_file = True

    return dat_file


def get_user_keep_may():
    valid_input = False
    keep_may = False
    while not valid_input:
        keep_may = input("Would you like to keep May 1st in the split file? Type 1 for yes, 2 for no: ")
        if keep_may != "1" and keep_may != "2":
            print("Invalid input.")
        else:
            keep_may = keep_may == "1"
            valid_input = True
    return keep_may


def get_user_num_lines():
    valid_input = False
    num_lines = False
    while not valid_input:
        num_lines = input("Please enter in the number of lines at the end of the file you would like to save: ")
        try:
            num_lines = int(num_lines)
            valid_input = True
        except ValueError:
            print("Not a valid number.")
    return num_lines


def get_user_date():
    valid_date = False
    date = ""
    print("In the format of YYYY-MM-DD HH:mm:ss please type in the date which all data on or after will be saved. "
          "All data before this date will not be saved.")

    while not valid_date:
        date = input("Enter a date: ")

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            valid_date = True
        except ValueError:
            print("Invalid date format, make sure to follow the format YYYY-MM-DD HH:mm:ss (Ex. 2024-09-10 00:00:00): ")
    return date


def get_user_regex():
    valid_regex = False
    dat_regex = ""

    while not valid_regex:
        dat_regex = input("Please enter in a regular expression to select the specific files which you want to select. "
                          "Some common regex expressions have been listed: \n"
                          "\\\\MB\\\\(.+)\\.dat : selects all dat files in the MB directory\n"
                          ".*24\\.dat : selects all 24 hour dat files\n"
                          ".*WG15\\.dat : selects all WG 15 minute dat files\n"
                          "Type in regular expression or enter to skip: ")
        try:
            re.compile(dat_regex)
            valid_regex = True
        except re.error:
            valid_regex = False

    print("\n\ndat_regex", dat_regex, "\n\n")
    return dat_regex


def user_interface_bootstrap():
    create_backup = None
    print("This is a program to automatically preform backups on the dat files.")
    backup_type = get_user_backup_type()
    dats_dir = get_user_dats_dir()

    dat_regex = get_user_regex()
    dat_file = get_user_dat_file()
    keep_split_file_date = get_user_keep_may()

    if backup_type == "2":
        num_saved = get_user_num_lines()
        create_backup = CreateBackupSavePreviousRows(dat_regex, dat_file, dats_dir, keep_split_file_date, num_saved)
    elif backup_type == "1":
        date = get_user_date()
        create_backup = CreateBackupSaveFromDate(dat_regex, dat_file, dats_dir, keep_split_file_date, date)

    print_effected_dats = input("Would you like to see a list of the dat files which will be changed in this "
                                "operation? 1 for yes, 2 for no: ")
    if print_effected_dats == "1":
        create_backup.print_effected_dirs()

    continue_program = input("Would you like to continue with the operation? 1 for yes, anything else for "
                             "exiting the program: ")
    if continue_program != "1":
        print("Exiting the program")
        exit(1)

    print("Creating dat backup")
    create_backup.backup_dats()
    print("Modifying the original dat files")
    create_backup.clear_dats_data()
    print("Successfully finished program")


def main():
    dats_dir = "D:/data/remote_server_mock/.dats/"
    mb_regex = r"\\MB\\(.+).dat"
    # create_backup = CreateBackupSavePreviousRows("", "non_potato_dats.csv", dats_dir, True, 6)
    # create_backup = CreateBackupSaveFromDate(mb_regex, "", dats_dir, True, "2024-06-21 00:00:00")
    # create_backup = CreateBackupSaveFromDate("", "non_potato_dats.csv", dats_dir, True, "2024-06-21 00:00:00")

    # comment/uncomment these for non prompted execution
    # create_backup.backup_dats()
    # create_backup.clear_dats_data()

    # comment/uncomment to run with user prompts
    user_interface_bootstrap()


if __name__ == "__main__":
    main()
