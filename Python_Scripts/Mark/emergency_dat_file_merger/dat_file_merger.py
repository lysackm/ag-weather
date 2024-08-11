import glob
import os
import shutil

# old is the backup files
old_dir = ".\\old_dats\\"
# old_dir = 'C:\\Users\\Administrator\\Documents\\2024_08_09\\Dats-April14-July222024-15\\'
# new is the as-up-to-date files that exist
new_dir = ".\\new_dats\\"
# new_dir = 'C:\\Users\\Administrator\\Documents\\2024_08_09\\new_dats_2024_08_09\\'
# dest is the newly created merged file in the correct destination
dest_dir = ".\\dest_dats\\"
# dest_dir = 'C:\\Users\\Administrator\\Documents\\2024_08_09\\dat_destination_2024_08_09\\'

missing_line_dir = ".\\missing_15_line\\"

# file suffixes
file_suffixes = ['alonsa15.dat', 'moosehorn2_15.dat', 'minto15.dat', 'baldur15.dat', 'miniota15.dat', 'elma15.dat', 'cartwright15.dat', 'stonewall15.dat', 'SteRose2_15.dat', 'pierson2_15.dat', 'dominioncity15.dat', 'oakburn15.dat', 'holland15.dat', 'stclaude15.dat', 'carman15.dat', 'saintlabre15.dat', 'dand15.dat', 'Forkriver15.dat', 'ashville15.dat', 'treherne15.dat', 'minnedosa2_15.dat', 'rivers15.dat', 'sanclara15.dat', 'newdale15.dat', 'deloraine15.dat', 'pipelake15.dat', 'glenboro15.dat', 'virden2_15.dat', 'beausejour15.dat', 'eriksdale2_15.dat', 'forrest15.dat', 'Grandview2_15.dat', 'findlay15.dat', 'erickson15.dat', 'swanvalley2_15.dat', 'Plumas15.dat', 'steinbach15.dat', 'lakeland15.dat', 'minitonas15.dat', 'clarkleigh15.dat', 'birtle2_15.dat', 'arborg15.dat', 'clearwater15.dat', 'brandonMBFI15.dat', 'argue15.dat', 'vivian15.dat', 'teulon2_15.dat', 'waskada15.dat', 'wawanesapotato2_15.dat', 'killarney2_15.dat', 'glenleatest15.dat', 'winkler2_15.dat', 'kola15.dat', 'kane15.dat', 'woodlands2_15.dat', 'rorketon15.dat', 'poplarfield15.dat', 'laurier15.dat', 'petersfield15.dat', 'ruthenia15.dat', 'Marchand15.dat', 'stadolphe15.dat', 'richer15.dat', 'lacdubonnet15.dat', 'boissevain15.dat', 'elmcreek15.dat', 'eden15.dat', 'reston2_15.dat', 'narcisse15.dat', 'zhoda15.dat', 'neepawa15.dat', 'birchriver15.dat', 'mcauley15.dat', 'Riverton15.dat', 'bagot15.dat', 'elie15.dat', 'austin15.dat', 'amaranth15.dat', 'reedycreek15.dat', 'gardenton15.dat', 'ninette15.dat', 'souris15.dat', 'stlazare15.dat', 'dugald2_15.dat', 'kenton15.dat', 'taylorspoint15.dat', 'keld15.dat', 'stpierre2_15.dat', 'manitou15.dat', 'selkirk15.dat', 'sinclair15.dat', 'Mountainside15.dat', 'wawanesa15.dat', 'brunkild15.dat', 'starbuck15.dat', 'ethelbert15.dat', 'fisherton15.dat', 'jordan15.dat', 'portage2_15.dat', 'hamiota2_15.dat', 'lakefrancis15.dat', 'shilo15.dat', 'gladstone15.dat', 'windygates15.dat', 'prawda15.dat', 'somerset2_15.dat', 'ingelow15.dat', 'Snowflake15.dat', 'alexander15.dat', 'altona15.dat', 'inwood15.dat', 'spraguelakebog15.dat', 'lakeaudy15.dat', 'bede2_15.dat', 'morris2_15.dat', 'Stead15.dat', 'russell15.dat', 'driftingriver15.dat', 'inglis15.dat', 'Rosa15.dat']


def filter_15_dats(file):
    if "15.dat" in file and "WG15.dat" not in file:
        return True
    else:
        return False


def fetch_file_names(dat_dir):
    files = glob.glob(dat_dir + "*.dat")
    files = filter(filter_15_dats, files)
    return files


def dest_file_from_other(file, generic_dir=dest_dir):
    suffix = ""
    if "/" in file:
        suffix = file.split("/")[-1]
    elif "\\" in file:
        suffix = file.split("\\")[-1]
    else:
        print("Error could not find the last part of the file to create a destination file")
        exit(1)

    # print("dest_file_from_other", dest_dir + suffix)
    return generic_dir + suffix


def copy_old_dats():
    dat_files = fetch_file_names(new_dir)

    for old_dat in dat_files:
        # print("old_dat", old_dat)
        dest_dat = dest_file_from_other(old_dat)
        assert (not os.path.isfile(dest_dat))
        shutil.copyfile(old_dat, dest_dat)


def copy_new_dats():
    dat_files = fetch_file_names(new_dir)

    for new_dat in dat_files:
        if "/" in new_dat:
            suffix = new_dat.split("/")[-1]
        elif "\\" in new_dat:
            suffix = new_dat.split("\\")[-1]
        if suffix in file_suffixes:
            # print("old_dat", old_dat)
            dest_dat = dest_file_from_other(new_dat)
            assert (not os.path.isfile(dest_dat))
            shutil.copyfile(new_dat, dest_dat)


def verify_file_in_old_dats(dat):
    if "/" in dat:
        suffix = dat.split("/")[-1]
    elif "\\" in dat:
        suffix = dat.split("\\")[-1]
    else:
        return False

    dat_files = fetch_file_names(old_dir)
    for file in dat_files:
        if "/" in file:
            suffix_old = file.split("/")[-1]
        elif "\\" in file:
            suffix_old = file.split("\\")[-1]
        else:
            continue

        if suffix == suffix_old:
            return True

    return False


def line_to_date(line):
    date = line[0:21]
    # print(date)
    return date


def concat_new_files_onto_dest():
    dat_files = fetch_file_names(new_dir)
    date_of_backup = '"2024-08-06 15:30:00"'

    for new_dat in dat_files:
        if verify_file_in_old_dats(new_dat):
            dest_dat = dest_file_from_other(new_dat)
            assert (os.path.isfile(dest_dat))

            dest_f = open(dest_dat, "a")
            new_f = open(new_dat, "r")
            line_num = 0

            while True:
                # Get next line from file
                line = new_f.readline()
                # print(line)
                date = line_to_date(line)

                if date >= date_of_backup and line_num >= 2:
                    # append line to new file
                    dest_f.write(line)
                line_num += 1

                # if line is empty
                # end of file is reached
                if not line:
                    break

            dest_f.close()
            new_f.close()


def check_which_line_missing(contents):
    i = -1
    while i > -len(contents):
        if contents[i][0:21] == '"2024-08-09 11:00:00"':
            print(contents[i - 1][0:21])
            if contents[i - 1][0:21] == '"2024-08-09 10:45:00"':
                return None
            assert(contents[i - 1][0:21] == '"2024-08-09 10:30:00"')
            return i
        i -= 1


def add_missing_line():
    # go through dat files
    # find the line before "2024-08-09 10:45:00" <- what we want to insert

    # can we assert that "2024-08-09 10:30:00" exists? similarly can we assert that "2024-08-09 11:00:00" exists?
    # probably tbh, raise exception if it doesn't
    copy_new_dats()
    dest_files = fetch_file_names(dest_dir)

    for file in dest_files:
        with open(file, "r") as f:
            contents = f.readlines()

        if "/" in file:
            suffix = file.split("/")[-1]
        elif "\\" in file:
            suffix = file.split("\\")[-1]

        missing_line_file = dest_file_from_other(file, missing_line_dir)

        # needs to manually be changed
        index = check_which_line_missing(contents)

        if index is not None and suffix in file_suffixes:
            print(contents[index][0:21], file)
            assert (contents[index][0:21] == '"2024-08-09 11:00:00"')

            with open(missing_line_file, 'r') as f:
                lines = f.read().splitlines()
                inserted_line = lines[-1]
                inserted_line = inserted_line + '\n'

            contents.insert(index, inserted_line)

            with open(file, "w") as f:
                contents = "".join(contents)
                f.write(contents)


def main():
    # copy old dats to new dat location
    # iterate through new dats line by line and find dates which are greater than or equal to "2024-08-06 15:30:00"
    # concat filtered lines to new file
    # get list of files from backups and backups only

    # merge 2 sets of dat files
    # copy_old_dats()
    # concat_new_files_onto_dest()

    # replace missing line of data
    add_missing_line()


if __name__ == "__main__":
    main()
