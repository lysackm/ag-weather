import urllib.request
import bs4
import os
import log

# downloads the .txt or .dat data files from the mb ag weather website

# directory: folder to save the files into
def run(directory):
    log.main("download data")

    # add a path separator to end of directory name
    directory = directory + os.path.sep

    log.main("download data")
    # url being downloaded from
    website = "https://mbagweather.ca/"
    # note: this is downloading the last 3 months of 15 min, 60 min, and 24 hour data
    website_dir = "partners/current/"
    url = website + website_dir

    # location to save the html directory
    html_dir_path = directory + "dir.html"

    # save the html
    urllib.request.urlretrieve(url, html_dir_path)

    # open the html file
    html_file = open(html_dir_path, "r")

    # pass the html file to bs4 for parsing
    soup = bs4.BeautifulSoup(html_file, "html.parser")

    # this will hold the list of files to download
    file_list = []

    # extensions of files to download
    valid_extensions = [".txt", ".dat"]

    # parse the html to get all the filenames to download
    for link in soup.find_all("a"):
        address = link.get("href")
        # final 4 characters
        extension = address[-4:].lower()
        if extension in valid_extensions:
            # add to the list of files to download
            # drop the directory info from the address to get just the filename
            address = address.replace(website_dir, "")
            # may be necessary to remove a period and/or forward slash from start of address
            if address.startswith("."):
                address = address[1:]
            if address.startswith("/"):
                address = address[1:]
            file_list.append(address)

    # download each file to website_data/filename.ext
    for filename in file_list:
        # url + filename is the location of the file on the internet to download
        # path + filename is the location on the pc to save the file to
        # lower() makes the filename lowercase
        urllib.request.urlretrieve(url + filename, directory + filename.lower())

    # close the html file
    html_file.close()







