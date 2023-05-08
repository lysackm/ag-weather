from config import temp_folder
import log
from util import try_delete, try_rename, file_exists
import clean_old_carman
import pandas

def run():
	log.main("bespoke fixes")
	
	# delete several folders that contain no useful data
	try_delete(f"{temp_folder}/2019/Daily")
	try_delete(f"{temp_folder}/2019/PLB")
	try_delete(f"{temp_folder}/2016/SplitWG")
	try_delete(f"{temp_folder}/2012/oldForrest")
	try_delete(f"{temp_folder}/2012/Spud")

	# rename MelitaWADO to bede
	try_rename(f"{temp_folder}/2012/MelitaWADO_60min.txt", f"{temp_folder}/2012/bede60.txt")
	try_rename(f"{temp_folder}/2012/MelitaWADO_24hr.txt", f"{temp_folder}/2012/bede24.txt")
	try_rename(f"{temp_folder}/2012/MelitaWADO_15min.txt", f"{temp_folder}/2012/bede15.txt")

	# bede already exists, so rename to bede to bede_2 and melita to bede
	try_rename(f"{temp_folder}/2014/Summer/bede15.txt", f"{temp_folder}/2014/Summer/bede2_15.txt")
	try_rename(f"{temp_folder}/2014/Summer/bede60.txt", f"{temp_folder}/2014/Summer/bede2_60.txt")
	try_rename(f"{temp_folder}/2014/Summer/bede24.txt", f"{temp_folder}/2014/Summer/bede2_24.txt")

	try_rename(f"{temp_folder}/2014/Summer/MelitaWADO_15min.txt", f"{temp_folder}/2014/Summer/bede15.txt")
	try_rename(f"{temp_folder}/2014/Summer/MelitaWADO_60min.txt", f"{temp_folder}/2014/Summer/bede60.txt")
	try_rename(f"{temp_folder}/2014/Summer/MelitaWADO_24hr.txt", f"{temp_folder}/2014/Summer/bede24.txt")

	# rename melitaWADO to bede
	try_rename(f"{temp_folder}/2013/MelitaWADO_24hr.txt", f"{temp_folder}/2013/bede24.txt")
	try_rename(f"{temp_folder}/2013/MelitaWADO_15min.txt", f"{temp_folder}/2013/bede15.txt")
	try_rename(f"{temp_folder}/2013/MelitaWADO_60min.txt", f"{temp_folder}/2013/bede60.txt")

	try_rename(f"{temp_folder}/2013/summer/MelitaWADO_60min.txt", f"{temp_folder}/2013/summer/bede60.txt")
	try_rename(f"{temp_folder}/2013/summer/MelitaWADO_24hr.txt", f"{temp_folder}/2013/summer/bede24.txt")
	try_rename(f"{temp_folder}/2013/summer/MelitaWADO_15min.txt", f"{temp_folder}/2013/summer/bede15.txt")
	try_rename(f"{temp_folder}/2013/winter/MelitaWADO_60min.txt", f"{temp_folder}/2013/winter/bede60.txt")

	# rename shilo files
	try_rename(f"{temp_folder}/2012/hilo12_15.txt", f"{temp_folder}/2012/shilo2_15.txt")
	try_rename(f"{temp_folder}/2013/hilo12_15.txt", f"{temp_folder}/2013/shilo2_15.txt")
	try_rename(f"{temp_folder}/2011/shilo2011_shilo11_24.txt", f"{temp_folder}/2011/shilo2_24.txt")
	try_rename(f"{temp_folder}/2011/shilo2011_shilo11_60.txt", f"{temp_folder}/2011/shilo2_60.txt")
	try_rename(f"{temp_folder}/2011/shilo2011_shilo11_15.txt", f"{temp_folder}/2011/shilo2_15.txt")
	try_rename(f"{temp_folder}/2013/shilo12_24.txt", f"{temp_folder}/2013/shilo2_24.txt")
	try_rename(f"{temp_folder}/2013/shilo12_60.txt", f"{temp_folder}/2013/shilo2_60.txt")

	# rename swanlake files
	try_rename(f"{temp_folder}/2011/swanlake2011_swanlake11_60.txt", f"{temp_folder}/2011/swanlake2_60.txt")
	try_rename(f"{temp_folder}/2011/swanlake2011_swanlake11_24.txt", f"{temp_folder}/2011/swanlake2_24.txt")
	try_rename(f"{temp_folder}/2011/swanlake2011_swanlake11_15.txt", f"{temp_folder}/2011/swanlake2_15.txt")
	try_rename(f"{temp_folder}/2012/swanlake12_15.txt", f"{temp_folder}/2012/swanlake2_15.txt")
	try_rename(f"{temp_folder}/2012/swanlake12_24.txt", f"{temp_folder}/2012/swanlake2_24.txt")
	try_rename(f"{temp_folder}/2012/swanlake12_60.txt", f"{temp_folder}/2012/swanlake2_60.txt")
	try_rename(f"{temp_folder}/2013/swanlake12_15.txt", f"{temp_folder}/2013/swanlake2_15.txt")
	try_rename(f"{temp_folder}/2013/swanlake12_24.txt", f"{temp_folder}/2013/swanlake2_24.txt")
	try_rename(f"{temp_folder}/2013/swanlake12_60.txt", f"{temp_folder}/2013/swanlake2_60.txt")

	# rename somerset files
	try_rename(f"{temp_folder}/2014/Fall/somerset2_somersetWG60.txt", f"{temp_folder}/2014/Fall/somerset2_WG60.txt")
	try_rename(f"{temp_folder}/2014/Fall/somerset2_somerset15.txt", f"{temp_folder}/2014/Fall/somerset2_15.txt")
	try_rename(f"{temp_folder}/2014/Fall/somerset2_somerset24.txt", f"{temp_folder}/2014/Fall/somerset2_24.txt")
	try_rename(f"{temp_folder}/2014/Fall/somerset2_somerset60.txt", f"{temp_folder}/2014/Fall/somerset2_60.txt")
	try_rename(f"{temp_folder}/2014/Summer/somerset2_somersetWG60.txt", f"{temp_folder}/2014/Summer/somerset2_WG60.txt")
	try_rename(f"{temp_folder}/2014/Summer/somerset2_somerset15.txt", f"{temp_folder}/2014/Summer/somerset2_15.txt")
	try_rename(f"{temp_folder}/2014/Summer/somerset2_somerset24.txt", f"{temp_folder}/2014/Summer/somerset2_24.txt")
	try_rename(f"{temp_folder}/2014/Summer/somerset2_somerset60.txt", f"{temp_folder}/2014/Summer/somerset2_60.txt")

	# rename portage files
	try_rename(f"{temp_folder}/2014/Fall/portage2_portage15.txt", f"{temp_folder}/2014/Fall/portage2_15.txt")
	try_rename(f"{temp_folder}/2014/Fall/portage2_portage24.txt", f"{temp_folder}/2014/Fall/portage2_24.txt")
	try_rename(f"{temp_folder}/2014/Fall/portage2_portage60.txt", f"{temp_folder}/2014/Fall/portage2_60.txt")

	#there are 3 small carberry files in addition to 3 large, rename the small ones
	try_rename(f"{temp_folder}/2017/Summer2017/Carberry15.txt", f"{temp_folder}/2017/Summer2017/carberry2_15.txt")
	try_rename(f"{temp_folder}/2017/Summer2017/Carberry60.txt", f"{temp_folder}/2017/Summer2017/carberry2_60.txt")
	try_rename(f"{temp_folder}/2017/Summer2017/Carberry24.txt", f"{temp_folder}/2017/Summer2017/carberry2_24.txt")

	# 2017 summer
	# fix typo
	try_rename(f"{temp_folder}/2017/Summer2017/StRose224.txt", f"{temp_folder}/2017/Summer2017/sterose224.txt")
	try_rename(f"{temp_folder}/2017/Summer2017/StRose2WG15.txt", f"{temp_folder}/2017/Summer2017/sterose2WG15.txt")

	# rename alonsa file without data rate
	try_rename(f"{temp_folder}/2011/alonsaWG.txt", f"{temp_folder}/2011/alonsaWG60.txt")

	# delete files with invalid data
	try_delete(f"{temp_folder}/2016/Summer/manitouWG15.txt") # too many headers
	try_delete(f"{temp_folder}/2011/swanlake2_24.txt")
	try_delete(f"{temp_folder}/2011/swanlake2_60.txt")
	try_delete(f"{temp_folder}/2011/carmanWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2011/swanlake2_15.txt")
	try_delete(f"{temp_folder}/2011/shilo2_24.txt")
	try_delete(f"{temp_folder}/2011/shilo2_60.txt")
	try_delete(f"{temp_folder}/2011/manitouWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2011/shilo2_15.txt")
	try_delete(f"{temp_folder}/2017/Summer2017/bede15.txt") # empty
	try_delete(f"{temp_folder}/2012/manitouWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2015/Mountainside24.txt") # too many headers
	try_delete(f"{temp_folder}/2015/MountainsideWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2015/InwoodWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2015/Mountainside15.txt") # too many headers
	try_delete(f"{temp_folder}/2015/Mountainside60.txt") # too many headers
	try_delete(f"{temp_folder}/2014/Fall/manitouWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2014/Summer/manitouWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2013/manitouWG60.txt") # too many headers
	try_delete(f"{temp_folder}/2013/summer/manitouWG60.txt") # multiple headers
	try_delete(f"{temp_folder}/2013/winter/manitouWG60.txt") # multiple headers
	try_delete(f"{temp_folder}/2011/hamiotaWG_rtmc.txt") # too many headers
	try_delete(f"{temp_folder}/2011/marchand24.txt") # (1) (2) headers
	try_delete(f"{temp_folder}/2012/marchand24.txt") # (1) (2) headers
	try_delete(f"{temp_folder}/2010/marchand24.txt") # (1) (2) headers
	try_delete(f"{temp_folder}/2012/carmanWG60.txt") # short header
	try_delete(f"{temp_folder}/2015/Inwood15.txt") # too many headers
	try_delete(f"{temp_folder}/2014/Fall/carmanWG60.txt") # unknown column PluvioInit
	try_delete(f"{temp_folder}/2014/Summer/carmanWG60.txt") # unknown column PluvioInit
	try_delete(f"{temp_folder}/2013/carmanWG60.txt") # unknown column PluvioInit
	try_delete(f"{temp_folder}/2013/summer/carmanWG60.txt") # unknown column PluvioInit
	try_delete(f"{temp_folder}/2013/carmanWG_RG60.txt") # unknown data
	try_delete(f"{temp_folder}/2009/forrest_24hr.txt") # contains subset of data in 2009/forrest24.txt

	# delete crbdry files (contain duplicate data)
	try_delete(f"{temp_folder}/2011/CRBDRY15.txt")
	try_delete(f"{temp_folder}/2012/CRBDRY15.txt")
	try_delete(f"{temp_folder}/2013/CRBDRY15.txt")
	try_delete(f"{temp_folder}/2012/CRBDRY24.txt")

	# delete 10 min carman files
	try_delete(f"{temp_folder}/2008/carman10.txt")
	try_delete(f"{temp_folder}/2009/carman10.txt")

	# clean old (2008-2010) carman files by removing extra columns
	clean_old_carman.run()

	# 2008 portage 24 hr file and stpierre 60 min file contain typos in preheader
	portage_path = f"{temp_folder}/2008/portage_24hr.txt"
	if file_exists(portage_path):
		# read file without preheader by skipping first row
		portage_df = pandas.read_csv(portage_path, skiprows=1)
		# rewrite the file to original path
		# without index=False, the rows will start with 1,2,3...
		portage_df.to_csv(portage_path, index=False)

	stpierre_path = f"{temp_folder}/2008/stpierre_60min.txt"
	if file_exists(stpierre_path):
		# read file without preheader
		stpierre_df = pandas.read_csv(stpierre_path, skiprows=1)
		# rewrite the file to original path
		stpierre_df.to_csv(stpierre_path, index=False)

	# delete 2019 mafrd test files
	# summer
	try_delete(f"{temp_folder}/2019/Summer/mafrdtest_15.txt")
	try_delete(f"{temp_folder}/2019/Summer/mafrdtest_24.txt")
	try_delete(f"{temp_folder}/2019/Summer/mafrdtest_60.txt")
	try_delete(f"{temp_folder}/2019/Summer/mafrdtest_WG15.txt")

	# winter
	try_delete(f"{temp_folder}/2019/Winter/mafrdtest_15.txt")
	try_delete(f"{temp_folder}/2019/Winter/mafrdtest_24.txt")
	try_delete(f"{temp_folder}/2019/Winter/mafrdtest_60.txt")
	try_delete(f"{temp_folder}/2019/Winter/mafrdtest_WG15.txt")

	# 2009 winkler 15 file has lots of whitespace at the end, clean it up
	if file_exists(f"{temp_folder}/2009/winkler_15min.txt"):
		# read original file
		orig_winkler_file = open(f"{temp_folder}/2009/winkler_15min.txt", "r")
		# create new file to write to
		new_winkler_file = open(f"{temp_folder}/2009/winkler15.txt", "w")

		# non-whitespace lines
		r = range(1, 32044)
		for n in r:
			# copy over data
			new_winkler_file.write(orig_winkler_file.readline())

		# close the files
		orig_winkler_file.close()
		new_winkler_file.close()

		# delete the original file since we have a new file now
		try_delete(f"{temp_folder}/2009/winkler_15min.txt", "file replaced with whitespace removed")
