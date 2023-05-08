from util import delete

def fix(df, path):
	# to allow for 1-based indexing, pad the 0th element
	header = [None] + list(df.columns)
	
	if len(header) > 1 and header[1] == "TIMESTAMP":
		header[1] = "TMSTAMP"
	
	if len(header) > 3 and header[3] == "StationID":
		header[3] = "StnID"
	
	if len(header) > 4 and header[4] in ("AirT_1min", "AirT_15_Avg"):
		header[4] = "Air_T"
	
	if len(header) > 5 and header[5] in ("RH_1min", "RH_15_Avg"):
		header[5] = "RH"
	
	if len(header) > 6 and header[6] in ("Rain", "Rain_mm_Tot", "Rain_mm_TOT"):
		header[6] = "Pluvio_Rain"
	
	if len(header) > 7 and header[7] == "WS_ms_S_WVT":
		header[7] = "AvgWS"
	
	if len(header) > 8 and header[8] == "WindDir_D1_WVT":
		header[8] = "AvgWD"
	
	if len(header) > 9 and header[9] == "WindDir_SD1_WVT":
		header[9] = "AvgSD"
	
	if len(header) > 10 and header[10] == "Rain2":
		header[10] = "TBRG_Rain"
	
	# return the padded header to the dataframe
	df.columns = header[1:]
	
	df.rename(columns = {
		"Rain_mm2_TOT": "TBRG_Rain",
	}, inplace = True)
	
	return df
