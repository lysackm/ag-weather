import datetime
import glob
import os
import re
import shutil


def get_current_date_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H %M %S')


class CreateBackup:
    def __init__(self, file_regex, files, dats_dir):
        self.file_regex = file_regex
        self.files = files
        self.dats_dir = dats_dir.replace("\\", "/")
        self.backup_dir = "./dat_backups_" + get_current_date_string()

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
        for dat_file in self.get_dat_files():
            print(dat_file)


class CreateBackupSavePreviousRows(CreateBackup):
    # saved_days: variable which indicates how
    def __init__(self, file_regex, files, dats_dir, previous_rows):
        super().__init__(file_regex, files, dats_dir)
        self.previous_rows = previous_rows

    def clear_dat_data(self, dat_file):
        with open(dat_file, 'r') as file:
            file_data = file.readlines()
            header = file_data[0:2]
            data = file_data[len(file_data) - self.previous_rows: len(file_data)]
            file_content = header + data
            file_content = "".join(file_content)

        with open(dat_file, "w") as file:
            file.write(file_content)

    def clear_dats_data(self):
        dat_files = self.get_dat_files()
        for dat_file in dat_files:
            self.clear_dat_data(dat_file)


class CreateBackupSaveFromDate(CreateBackup):
    def __init__(self, file_regex, files, dats_dir, start_datetime):
        super().__init__(file_regex, files, dats_dir)
        if type(start_datetime) is datetime.datetime:
            self.start_datetime = start_datetime
        elif type(start_datetime) is str:
            self.start_datetime = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
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

            file_content = header + data
            file_content = "".join(file_content)

        with open(dat_file, "w") as file:
            file.write(file_content)

    def clear_dats_data(self):
        dat_files = self.get_dat_files()
        for dat_file in dat_files:
            self.clear_dat_data(dat_file)


def user_interface_bootstrap():
    create_backup = None
    print("This is a program to automatically preform backups on the dat files.")
    backup_type = input("For each file would you like to (1) save the last n lines of the file, or "
                        "(2) save data after a date? Enter 1 or 2 to continue: ")

    dats_dir = input("Please type the absolute file directory to the dat files (default is C:/Campbellsci/Dats/)."
                     " Type your answer or press enter for default: ")

    if dats_dir == "":
        dats_dir = "C:/Campbellsci/Dats/"

    dat_regex = input("Please enter in a regular expression to select the specific files which you want to select. "
                      "Some common regex expressions have been listed: \n"
                      "\\\\MB\\\\(.+).dat : selects all dat files in the MB directory\n"
                      "*24.dat : selects all 24 hour dat files\n"
                      "*WG15.dat : selects all WG 15 minute dat files\n"
                      "Type in regular expression or enter to skip: ")

    dat_file = input("If there is a file which has a list of dat files which you want to backup, type the name of "
                     "the file or press enter to skip: ")

    if backup_type == "1":
        num_saved = input("Please enter in the number of lines at the end of the file you would like to save: ")
        create_backup = CreateBackupSavePreviousRows(dat_regex, dat_file, dats_dir, num_saved)
    elif backup_type == "2":
        print("In the format of YYYY-MM-DD HH:mm:ss please type in the date which all data on or after will be saved. "
              "All data before this date will not be saved.")
        date = input("Enter date: ")
        create_backup = CreateBackupSaveFromDate(dat_regex, dat_file, dats_dir, date)

    print_effected_dats = input("Would you like to see a list of the dat files which will be changed in this "
                                "operation? 1 for yes, 2 for no: ")
    if print_effected_dats == "1":
        create_backup.print_effected_dirs()

    continue_program = input("Would you like to continue with the operation? 1 for yes, 2 for exiting the program: ")
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
    # create_backup = CreateBackupSavePreviousRows(mb_regex, "", dats_dir, 500)
    # create_backup = CreateBackupSaveFromDate(mb_regex, "", dats_dir, "2024-06-21 00:00:00")
    # create_backup = CreateBackupSaveFromDate("", "non_potato_dats.csv", dats_dir, "2024-06-21 00:00:00")

    # comment/uncomment these to stop the prompts from appearing
    # create_backup.backup_dats()
    # create_backup.clear_dats_data()

    user_interface_bootstrap()


if __name__ == "__main__":
    main()
