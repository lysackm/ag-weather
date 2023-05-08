# correct 15-minute columns
ideal_columns_15 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"Air_T",
	"RH",
	"Pluvio_Rain",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"TBRG_Rain",
	"MaxWS",
	"Press_hPa",
]

# correct 60-minute columns
ideal_columns_60 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"BatMin",
	"Air_T",
	"AvgAir_T",
	"MaxAir_T",
	"MinAir_T",
	"RH",
	"AvgRH",
	"Pluvio_Rain",
	"Pluvio_Rain24RT",
	"WS_10Min",
	"WD_10Min",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"MaxWS_10",
	"MaxWD_10",
	"MaxWS",
	"HmMaxWS",
	"MaxWD",
	"Max5WS_10",
	"Max5WD_10",
	"WS_2Min",
	"WD_2Min",
	"Soil_T05",
	"AvgRS_kw",
	"TotRS_MJ",
	"TBRG_Rain",
	"TBRG_Rain24RT2",
	"Soil_TP5_TempC",
	"Soil_TP5_VMC",
	"Soil_TP20_TempC",
	"Soil_TP20_VMC",
	"Soil_TP50_TempC",
	"Soil_TP50_VMC",
	"Soil_TP100_TempC",
	"Soil_TP100_VMC",
	"Evap60",
	"SolarRad",
	"Press_hPa",
]
# columns for a 60-minute file with 27-37 columns and no header
ideal_columns_60_27_to_37 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"BatMin",
	"Air_T",
	"AvgAir_T",
	"MaxAir_T",
	"MinAir_T",
	"RH",
	"AvgRH",
	"Pluvio_Rain",
	"Pluvio_Rain24RT",
	"WS_10Min",
	"WD_10Min",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"MaxWS_10",
	"MaxWD_10",
	"MaxWS",
	"HmMaxWS",
	"MaxWD",
	"Max5WS_10",
	"Max5WD_10",
	"WS_2Min",
	"WD_2Min",
	"Soil_T05",
	"AvgRS_kw",
	"TotRS_MJ",
	"TBRG_Rain",
	"TBRG_Rain24RT2",
	"Soil_TP5_TempC",
	"Soil_TP5_VMC",
	"Soil_TP20_TempC",
	"Soil_TP20_VMC",
	"Evap60",
	"SolarRad",
]

# correct 24-hour columns
ideal_columns_24 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"BatMin",
	"ProgSig",
	"AvgAir_T",
	"MaxAir_T",
	"HmMaxAir_T",
	"MinAir_T",
	"HmMinAir_T",
	"AvgRH",
	"MaxRH",
	"HmMaxRH",
	"MinRH",
	"HmMinRH",
	"Pluvio_Rain",
	"MaxWS",
	"HmMaxWS",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"AvgSoil_T05",
	"MaxSoil_T05",
	"MinSoil_T05",
	"AvgRS_kw",
	"MaxRS_kw",
	"HmMaxRS",
	"TotRS_MJ",
	"TBRG_Rain",
	"Avg_Soil_TP5_TempC",
	"Max_Soil_TP5_TempC",
	"Min_Soil_TP5_TempC",
	"Avg_Soil_TP5_VMC",
	"Max_Soil_TP5_VMC",
	"Min_Soil_TP5_VMC",
	"Avg_Soil_TP20_TempC",
	"Max_Soil_TP20_TempC",
	"Min_Soil_TP20_TempC",
	"Avg_Soil_TP20_VMC",
	"Max_Soil_TP20_VMC",
	"Min_Soil_TP20_VMC",
	"Avg_Soil_TP50_TempC",
	"Max_Soil_TP50_TempC",
	"Min_Soil_TP50_TempC",
	"Avg_Soil_TP50_VMC",
	"Max_Soil_TP50_VMC",
	"Min_Soil_TP50_VMC",
	"Avg_Soil_TP100_TempC",
	"Max_Soil_TP100_TempC",
	"Min_Soil_TP100_TempC",
	"Avg_Soil_TP100_VMC",
	"Max_Soil_TP100_VMC",
	"Min_Soil_TP100_VMC",
	"EvapTot24",
]
# columns for a 24-hour file with 28-29 columns and no header
ideal_columns_24_28_to_29 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"BatMin",
	"ProgSig",
	"AvgAir_T",
	"MaxAir_T",
	"HmMaxAir_T",
	"MinAir_T",
	"HmMinAir_T",
	"AvgRH",
	"MaxRH",
	"HmMaxRH",
	"MinRH",
	"HmMinRH",
	"Pluvio_Rain",
	"MaxWS",
	"HmMaxWS",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"AvgSoil_T05",
	"MaxSoil_T05",
	"MinSoil_T05",
	"AvgRS_kw",
	"MaxRS_kw",
	"HmMaxRS",
	"TotRS_MJ",
	"TBRG_Rain",
	"EvapTot24",
]

# columns for a 24-hour file with 42 columns and no header
ideal_columns_24_42 = [
	"TMSTAMP",
	"RECNBR",
	"StnID",
	"BatMin",
	"ProgSig",
	"AvgAir_T",
	"MaxAir_T",
	"HmMaxAir_T",
	"MinAir_T",
	"HmMinAir_T",
	"AvgRH",
	"MaxRH",
	"HmMaxRH",
	"MinRH",
	"HmMinRH",
	"Pluvio_Rain",
	"MaxWS",
	"HmMaxWS",
	"AvgWS",
	"AvgWD",
	"AvgSD",
	"AvgSoil_T05",
	"MaxSoil_T05",
	"MinSoil_T05",
	"AvgRS_kw",
	"MaxRS_kw",
	"HmMaxRS",
	"TotRS_MJ",
	"TBRG_Rain",
	"Avg_Soil_TP5_TempC",
	"Max_Soil_TP5_TempC",
	"Min_Soil_TP5_TempC",
	"Avg_Soil_TP5_VMC",
	"Max_Soil_TP5_VMC",
	"Min_Soil_TP5_VMC",
	"Avg_Soil_TP20_TempC",
	"Max_Soil_TP20_TempC",
	"Min_Soil_TP20_TempC",
	"Avg_Soil_TP20_VMC",
	"Max_Soil_TP20_VMC",
	"Min_Soil_TP20_VMC",
	"EvapTot24"
]

# correct WG columns, any rate
ideal_columns_wg = [
	'TMSTAMP',
	'RECNBR',
	'BatMin_Min',
	'IntRT',
	'AccRT_NRT',
	'AccNRT',
	'AccTotNRT',
	'BucketRT',
	'BucketNRT',
	'LCTemp',
	'HS',
	'Stat'
]
# columns for a WG file with 11 columns and no header
columns_wg_11 = [
	'TMSTAMP',
	'RECNBR',
	'IntRT',
	'AccRT_NRT',
	'AccNRT',
	'AccTotNRT',
	'BucketRT',
	'BucketNRT',
	'LCTemp',
	'HS',
	'Stat'
]
# columns for a WG file with 3 columns and no header
columns_wg_3 = [
	'TMSTAMP',
	'RECNBR',
	'AccRT_NRT',
]
