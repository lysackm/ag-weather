import pandas
from util import try_delete, delete, file_exists
from config import temp_folder

# purpose is to merge pairs of files from updated ("2") stations, as well as some 2009 files where the data is split between files
# updated station files are meant to have priority, so we have to make sure they get inserted into the database before
# files from the old station by keeping the "2_" in the final file name
def run():
    pairs_list = []

    # get pairs of files to merge
    # 2016 summer
    pairs_list.append((f"{temp_folder}/2016/Summer/sterose2_15.txt", f"{temp_folder}/2016/Summer/sterose215.txt"))
    pairs_list.append((f"{temp_folder}/2016/Summer/sterose2_24.txt", f"{temp_folder}/2016/Summer/sterose224.txt"))
    pairs_list.append((f"{temp_folder}/2016/Summer/sterose2_60.txt", f"{temp_folder}/2016/Summer/sterose260.txt"))
    pairs_list.append((f"{temp_folder}/2016/Summer/sterose2_WG15.txt", f"{temp_folder}/2016/Summer/sterose2WG15.txt"))

    # 2017 fall/winter
    pairs_list.append((f"{temp_folder}/2017/FallWinter/sterose2_24.txt", f"{temp_folder}/2017/FallWinter/sterose224.txt"))

    # 2017 summer
    # note: sterose224 and sterose2WG15 exist because of earlier renaming in fix_bespoke.py
    pairs_list.append((f"{temp_folder}/2017/Summer2017/sterose2_24.txt", f"{temp_folder}/2017/Summer2017/sterose224.txt"))
    pairs_list.append((f"{temp_folder}/2017/Summer2017/sterose2_WG15.txt", f"{temp_folder}/2017/Summer2017/sterose2WG15.txt"))
    pairs_list.append((f"{temp_folder}/2017/Summer2017/grandview2_24.txt", f"{temp_folder}/2017/Summer2017/grandview224.txt"))

    # merge the updated station files
    for pair in pairs_list:
        first_file = pair[0]
        second_file = pair[1]
        if file_exists(first_file) and file_exists(second_file):
            try:
                #add the files to the frame
                frames = [pandas.read_csv(first_file, skiprows=1), pandas.read_csv(second_file, skiprows=1)]

                # merge the files
                df = pandas.concat(frames)

                # remove all duplicate rows
                df = df.drop_duplicates()

                # overwrite first file in pair (the one with the underscore)
                df.to_csv(first_file, index=False)

                # delete the other file because all of its data is now in the first file
                delete(second_file, "data merged into another file")
            except:
                # display a message if something goes wrong
                print(f"{first_file} and {second_file} could not be merged into single pandas dataframe")