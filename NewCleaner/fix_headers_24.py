from util import delete

def fix(df, path):
	header = [None] + list(df.columns)
	
	if len(header) > 3 and header[3] in ("Day_of_year", "BatMin", "BatMin_Min"):
		delete(path, "bad header in column 4")
		return None
	
	if len(header) > 4 and header[4] == 'BatMin_Min':
		delete(path, "bad header 'BatMin_Min' in column 4")
		return None
	
	if len(header) > 16 and header[16] == "Rain":
		header[16] = "Pluvio_Rain"
	
	if len(header) > 29 and header[29] == "Rain2":
		header[29] = "TBRG_Rain"
	
	df.columns = header[1:]
	
	df.rename(columns = {
		"TIMESTAMP": "TMSTAMP",
		"RECNBR": "RECNBR",
		"StationID": "StnID",
		"Batt_Volt_MIN": "BatMin",
		"Prog_Sig": "ProgSig",
		"AirT_1min_AVG": "AvgAir_T",
		"AirT_1min_MAX": "MaxAir_T",
		"AirT_1min_Time_MAX": "HmMaxAir_T",
		"AirT_1min_MIN": "MinAir_T",
		"AirT_1min_Time_MIN": "HmMinAir_T",
		"RH_Percnt_AVG": "AvgRH",
		"RG_Percnt_MAX": "MaxRH",
		"RH_Percnt_MAX": "MaxRH",
		"RH_Percnt_Time_MAX": "HmMaxRH",
		"RH_Percnt_MIN": "MinRH",
		"RH_Percnt_Time_MIN": "HmMinRH",
		"Rain_mm_TOT": "Pluvio_Rain",
		"WS_ms_MAX": "MaxWS",
		"WS_ms_Time_MAX": "HmMaxWS",
		"WS_ms_S_WVT": "AvgWS",
		"WindDir_D1_WVT": "AvgWD",
		"WindDir_SD1_WVT": "AvgSD",
		"SoilT_1min_AVG": "AvgSoil_T05",
		"SoilT_1min_MAX": "MaxSoil_T05",
		"SoilT_1min_MIN": "MinSoil_T05",
		"AvgRS_kw_AVG": "AvgRS_kw",
		"AvgRS_kw_MAX": "MaxRS_kw",
		"AvgRS_kw_Time_MAX": "HmMaxRS",
		"TotRS_MJ_TOT": "TotRS_MJ",
		"Rain_mm2_TOT": "TBRG_Rain",
		"missing": "AvgRS_kw",
		"missing~2": "MaxRS_kw",
		"missing~3": "HmMaxRS",
		"missing~4": "TotRS_MJ",
		"AvgSoilT_05": "AvgSoil_T05"
	}, inplace=True)
	
	if 'carberry' in path:
		df.rename(columns = {
			"AirTemp_C_TMx": "HmMaxAir_T",
			"AirTemp_C_TMn": "HmMinAir_T",
			"Rain": "TBRG_Rain",
		}, inplace=True)
	
	return df
