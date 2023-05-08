from util import delete

def fix(df, path):
	header = [None] + list(df.columns)
	
	if len(header) > 3 and header[3] in ("SM_100_C8", "IntRT", "Year", "PluvioInit", "BatMin_Min", "ST1_1_Avg", "BatMin"):
		delete(path, "bad header in column 3")
		return None
	
	if len(header) > 4 and header[4] == 'BatMin_Min':
		delete(path, "bad header 'BatMin_Min' in column 4")
		return None
	
	if len(header) > 11 and header[11] in ("Rain", "Rain_mm_Tot", "Rain_mm_TOT"):
		header[11] = "Pluvio_Rain"
	
	if len(header) > 12 and header[12] in ("Rain24RT", "Tot24"):
		header[12] = "Pluvio_Rain24RT"
	
	if len(header) > 30 and header[30] == "Rain2":
		header[30] = "TBRG_Rain"
	
	if len(header) > 31 and header[31] == "Rain2":
		header[30] = "TBRG_Rain"
	
	df.columns = header[1:]
	
	df.rename(columns = {
		"TIMESTAMP": "TMSTAMP",
		"StationID": "StnID",
		"Batt_Volt_MIN": "BatMin",
		"AirT_1min": "Air_T",
		"AirT_1min_AVG": "AvgAir_T",
		"AirT_1min_MAX": "MaxAir_T",
		"AirT_1min_MIN": "MinAir_T",
		"RH_1min": "RH",
		"RH_Percnt_AVG": "AvgRH",
		"Rain_mm_TOT": "Pluvio_Rain",
		"Tot24": "Pluvio_Rain24RT",
		#"WD_10MinV": "WS_10Min",
		"WD_10MinV": "WD_10Min",
		"WS_ms_S_WVT": "AvgWS",
		"WindDir_D1_WVT": "AvgWD",
		"WindDir_SD1_WVT": "AvgSD",
		"WS_10Min_MAX": "MaxWS_10",
		"WD_10MinV_SMM": "MaxWD_10",
		"WS_ms_MAX": "MaxWS",
		"WS_ms_Time_MAX": "HmMaxWS",
		"WindDir_SMM": "MaxWD",
		"WS_ms_10": "Max5WS_10",
		"WD_ms_10": "Max5WD_10",
		"WS_2Min": "WS_2Min",
		"WD_2MinV": "WD_2Min",
		"SoilT_1min": "Soil_T05",
		"AvgRS_kw_AVG": "AvgRS_kw",
		"TotRS_MJ_TOT": "TotRS_MJ",
		"Rain_mm2_TOT": "TBRG_Rain",
		"Tot24_2": "TBRG_Rain24RT",
		"AirTemp_C_Avg": "AvgAir_T",
		"AirTemp_C_Max": "MaxAir_T",
		"AirTemp_C_Min": "MinAir_T",
		"RH_60_Avg": "RH",
		"RH_Percnt_Avg": "AvgRH",
		"Rain_mm_Tot": "TBRG_Rain",
		"missing": "AvgRS_kw",
		"missing~2": "TotRS_MJ",
	}, inplace = True)
	
	if 'carberry' in path:
		df.rename(columns = {
			"Rain": "TBRG_Rain",
			"Rain24RT": "TBRG_Rain24RT",
		}, inplace = True)
	
	df.rename(columns = {
		"TBRG_Rain24RT": "TBRG_Rain24RT2",
		"Rain24RT2": "TBRG_Rain24RT2",
	}, inplace = True)
	
	return df
