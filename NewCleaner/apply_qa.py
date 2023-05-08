import pandas

def qa_15(df_15):
    date_col = "Datetime"

    # StnID       BETWEEN 200   AND 800
    # delete rows outside of this range
    df_15 = df_15[(df_15.StnID >= 200) & (df_15.StnID <= 800)]

    # Air_T       DEPENDS ON MONTH
    # range based on monthly ranges for MinAir_T (data_24) and MaxAir_T (data_24): min of MinAir_T range and max of MaxAir_T range
    # january: [-50,15]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 1) & (df_15["Air_T"] < -50), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 1) & (df_15["Air_T"] > 15), None)

    # february: [-50,20]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 2) & (df_15["Air_T"] < -50), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 2) & (df_15["Air_T"] > 20), None)

    # march: [-35,25]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 3) & (df_15["Air_T"] < -35), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 3) & (df_15["Air_T"] > 25), None)

    # april: [-25,35]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 4) & (df_15["Air_T"] < -25), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 4) & (df_15["Air_T"] > 35), None)

    # may: [-20,40]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 5) & (df_15["Air_T"] < -20), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 5) & (df_15["Air_T"] > 40), None)

    # june: [-10,50]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 6) & (df_15["Air_T"] < -10), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 6) & (df_15["Air_T"] > 50), None)

    # july: [0,50]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 7) & (df_15["Air_T"] < 0), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 7) & (df_15["Air_T"] > 50), None)

    # august: [-10,50]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 8) & (df_15["Air_T"] < -10), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 8) & (df_15["Air_T"] > 50), None)

    # september: [-20,40]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 9) & (df_15["Air_T"] < -20), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 9) & (df_15["Air_T"] > 40), None)

    # october: [-25,35]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 10) & (df_15["Air_T"] < -25), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 10) & (df_15["Air_T"] > 35), None)

    # november: [-35,30]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 11) & (df_15["Air_T"] < -35), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 11) & (df_15["Air_T"] > 30), None)

    # december: [-50,20]
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 12) & (df_15["Air_T"] < -50), None)
    df_15["Air_T"] = df_15["Air_T"].mask((df_15[date_col].dt.month == 12) & (df_15["Air_T"] > 20), None)

    # end of Air_T

    # RH          BETWEEN 10  AND 100
    df_15["RH"] = df_15["RH"].mask(df_15["RH"] < 10, None)
    df_15["RH"] = df_15["RH"].mask(df_15["RH"] > 100, None)

    # Pluvio_Rain BETWEEN 0   AND 100
    df_15["Pluvio_Rain"] = df_15["Pluvio_Rain"].mask(df_15["Pluvio_Rain"] < 0, None)
    df_15["Pluvio_Rain"] = df_15["Pluvio_Rain"].mask(df_15["Pluvio_Rain"] > 100, None)

    # AvgWS       BETWEEN 0   AND 50
    df_15["AvgWS"] = df_15["AvgWS"].mask(df_15["AvgWS"] < 0, None)
    df_15["AvgWS"] = df_15["AvgWS"].mask(df_15["AvgWS"] > 50, None)

    # AvgWD       BETWEEN 0   AND 360
    df_15["AvgWD"] = df_15["AvgWD"].mask(df_15["AvgWD"] < 0, None)
    df_15["AvgWD"] = df_15["AvgWD"].mask(df_15["AvgWD"] > 360, None)

    # AvgSD       BETWEEN 0   AND 360
    df_15["AvgSD"] = df_15["AvgSD"].mask(df_15["AvgSD"] < 0, None)
    df_15["AvgSD"] = df_15["AvgSD"].mask(df_15["AvgSD"] > 360, None)

    # TBRG_Rain   BETWEEN 0   AND 100
    df_15["TBRG_Rain"] = df_15["TBRG_Rain"].mask(df_15["TBRG_Rain"] < 0, None)
    df_15["TBRG_Rain"] = df_15["TBRG_Rain"].mask(df_15["TBRG_Rain"] > 100, None)

    # MaxWS       BETWEEN 0   AND 50
    df_15["MaxWS"] = df_15["MaxWS"].mask(df_15["MaxWS"] < 0, None)
    df_15["MaxWS"] = df_15["MaxWS"].mask(df_15["MaxWS"] > 50, None)

    # Press_hPa   BETWEEN 950 AND 1050
    df_15["Press_hPa"] = df_15["Press_hPa"].mask(df_15["Press_hPa"] < 950, None)
    df_15["Press_hPa"] = df_15["Press_hPa"].mask(df_15["Press_hPa"] > 1050, None)

    return df_15

def qa_60(df_60):
    date_col = "Datetime"

    # StnID       BETWEEN 200   AND 800
    # delete rows outside of this range
    df_60 = df_60[(df_60.StnID >= 200) & (df_60.StnID <= 800)]

    # Air_T            DEPENDS ON MONTH
    # AvgAir_T         DEPENDS ON MONTH
    # MaxAir_T         DEPENDS ON MONTH
    # MinAir_T         DEPENDS ON MONTH

    # clean air temperature based on month
    # range based on monthly ranges for MinAir_T (data_24) and MaxAir_T (data_24): min of MinAir_T range and max of MaxAir_T range
    air_temp_columns_60 = [
        "Air_T",
        "AvgAir_T",
        "MaxAir_T",
        "MinAir_T"
    ]

    for column in air_temp_columns_60:
        # january: [-50,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] < -50), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] > 15), None)

        # february: [-50,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] < -50), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] > 20), None)

        # march: [-35,25]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] < -35), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] > 25), None)

        # april: [-25,35]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] < -25), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] > 35), None)

        # may: [-20,40]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] < -20), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] > 40), None)

        # june: [-10,50]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] > 50), None)

        # july: [0,50]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] < 0), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] > 50), None)

        # august: [-10,50]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] > 50), None)

        # september: [-20,40]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] < -20), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] > 40), None)

        # october: [-25,35]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] < -25), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] > 35), None)

        # november: [-35,30]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] < -35), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] > 30), None)

        # december: [-50,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] < -50), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] > 20), None)
        # end for loop air temperature columns

    # clean soil temperatures based on month and depth
    # Soil_T05          DEPENDS ON MONTH
    # Soil_TP5_TempC    DEPENDS ON MONTH
    # Soil_TP20_TempC   DEPENDS ON MONTH

    shallow_depth_column_list = [
        "Soil_T05",
        "Soil_TP5_TempC",
        "Soil_TP20_TempC"
    ]

    for column in shallow_depth_column_list:
        # january: [-30,5]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] < -30), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] > 5), None)

        # february: [-30,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] < -30), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] > 10), None)

        # march: [-25,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] < -25), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] > 15), None)

        # april: [-25,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] < -25), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] > 15), None)

        # may: [-15,25]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] < -15), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] > 25), None)

        # june: [-10,35]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] > 35), None)

        # july: [5,35]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] < 5), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] > 35), None)

        # august: [-5,30]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] < -5), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] > 30), None)

        # september: [-10,25]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] > 25), None)

        # october: [-15,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] < -15), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] > 20), None)

        # november: [-20,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] < -20), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] > 15), None)

        # december: [-25,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] < -25), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] > 10), None)
    # end for loop (data_60 shallow soil temp)

    # Soil_TP50_TempC   DEPENDS ON MONTH
    # Soil_TP100_TempC  DEPENDS ON MONTH

    deep_depth_column_list = [
        "Soil_TP50_TempC",
        "Soil_TP100_TempC"
    ]

    for column in deep_depth_column_list:
        # january: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 1) & (df_60[column] > 10), None)

        # february: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 2) & (df_60[column] > 10), None)

        # march: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 3) & (df_60[column] > 10), None)

        # april: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 4) & (df_60[column] > 10), None)

        # may: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 5) & (df_60[column] > 10), None)

        # june: [-5,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] < -5), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 6) & (df_60[column] > 15), None)

        # july: [0,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] < 0), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 7) & (df_60[column] > 20), None)

        # august: [0,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] < 0), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 8) & (df_60[column] > 20), None)

        # september: [0,20]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] < 0), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 9) & (df_60[column] > 20), None)

        # october: [-5,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] < -5), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 10) & (df_60[column] > 15), None)

        # november: [-5,15]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] < -5), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 11) & (df_60[column] > 15), None)

        # december: [-10,10]
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] < -10), None)
        df_60[column] = df_60[column].mask((df_60[date_col].dt.month == 12) & (df_60[column] > 10), None)
    # end for loop (data 60 deep soil temp)

    # BatMin           BETWEEN 8    AND 16
    df_60["BatMin"] = df_60["BatMin"].mask(df_60["BatMin"] < 8, None)
    df_60["BatMin"] = df_60["BatMin"].mask(df_60["BatMin"] > 16, None)

    # RH               BETWEEN 10   AND 100
    df_60["RH"] = df_60["RH"].mask(df_60["RH"] < 10, None)
    df_60["RH"] = df_60["RH"].mask(df_60["RH"] > 100, None)

    # AvgRH            BETWEEN 10   AND 100
    df_60["AvgRH"] = df_60["AvgRH"].mask(df_60["AvgRH"] < 10, None)
    df_60["AvgRH"] = df_60["AvgRH"].mask(df_60["AvgRH"] > 100, None)

    # Pluvio_Rain      BETWEEN 0    AND 100
    df_60["Pluvio_Rain"] = df_60["Pluvio_Rain"].mask(df_60["Pluvio_Rain"] < 0, None)
    df_60["Pluvio_Rain"] = df_60["Pluvio_Rain"].mask(df_60["Pluvio_Rain"] > 100, None)

    # Pluvio_Rain24RT  BETWEEN 0    AND 250
    df_60["Pluvio_Rain24RT"] = df_60["Pluvio_Rain24RT"].mask(df_60["Pluvio_Rain24RT"] < 0, None)
    df_60["Pluvio_Rain24RT"] = df_60["Pluvio_Rain24RT"].mask(df_60["Pluvio_Rain24RT"] > 250, None)

    # WS_10Min         BETWEEN 0    AND 50
    df_60["WS_10Min"] = df_60["WS_10Min"].mask(df_60["WS_10Min"] < 0, None)
    df_60["WS_10Min"] = df_60["WS_10Min"].mask(df_60["WS_10Min"] > 50, None)

    # WD_10Min         BETWEEN 0    AND 360
    df_60["WD_10Min"] = df_60["WD_10Min"].mask(df_60["WD_10Min"] < 0, None)
    df_60["WD_10Min"] = df_60["WD_10Min"].mask(df_60["WD_10Min"] > 360, None)

    # AvgWS            BETWEEN 0    AND 50
    df_60["AvgWS"] = df_60["AvgWS"].mask(df_60["AvgWS"] < 0, None)
    df_60["AvgWS"] = df_60["AvgWS"].mask(df_60["AvgWS"] > 50, None)

    # AvgWD            BETWEEN 0    AND 360
    df_60["AvgWD"] = df_60["AvgWD"].mask(df_60["AvgWD"] < 0, None)
    df_60["AvgWD"] = df_60["AvgWD"].mask(df_60["AvgWD"] > 360, None)

    # AvgSD            BETWEEN 0    AND 360
    df_60["AvgSD"] = df_60["AvgSD"].mask(df_60["AvgSD"] < 0, None)
    df_60["AvgSD"] = df_60["AvgSD"].mask(df_60["AvgSD"] > 360, None)

    # MaxWS_10         BETWEEN 0    AND 50
    df_60["MaxWS_10"] = df_60["MaxWS_10"].mask(df_60["MaxWS_10"] < 0, None)
    df_60["MaxWS_10"] = df_60["MaxWS_10"].mask(df_60["MaxWS_10"] > 50, None)

    # MaxWD_10         BETWEEN 0    AND 360
    df_60["MaxWD_10"] = df_60["MaxWD_10"].mask(df_60["MaxWD_10"] < 0, None)
    df_60["MaxWD_10"] = df_60["MaxWD_10"].mask(df_60["MaxWD_10"] > 360, None)

    # MaxWS            BETWEEN 0    AND 50
    df_60["MaxWS"] = df_60["MaxWS"].mask(df_60["MaxWS"] < 0, None)
    df_60["MaxWS"] = df_60["MaxWS"].mask(df_60["MaxWS"] > 50, None)

    # MaxWD            BETWEEN 0    AND 360
    df_60["MaxWD"] = df_60["MaxWD"].mask(df_60["MaxWD"] < 0, None)
    df_60["MaxWD"] = df_60["MaxWD"].mask(df_60["MaxWD"] > 360, None)

    # Max5WS_10        BETWEEN 0    AND 50
    df_60["Max5WS_10"] = df_60["Max5WS_10"].mask(df_60["Max5WS_10"] < 0, None)
    df_60["Max5WS_10"] = df_60["Max5WS_10"].mask(df_60["Max5WS_10"] > 50, None)

    # Max5WD_10        BETWEEN 0    AND 360
    df_60["Max5WD_10"] = df_60["Max5WD_10"].mask(df_60["Max5WD_10"] < 0, None)
    df_60["Max5WD_10"] = df_60["Max5WD_10"].mask(df_60["Max5WD_10"] > 360, None)

    # WS_2Min          BETWEEN 0    AND 50
    df_60["WS_2Min"] = df_60["WS_2Min"].mask(df_60["WS_2Min"] < 0, None)
    df_60["WS_2Min"] = df_60["WS_2Min"].mask(df_60["WS_2Min"] > 50, None)

    # WD_2Min          BETWEEN 0    AND 360
    df_60["WD_2Min"] = df_60["WD_2Min"].mask(df_60["WD_2Min"] < 0, None)
    df_60["WD_2Min"] = df_60["WD_2Min"].mask(df_60["WD_2Min"] > 360, None)

    # AvgRS_kw         BETWEEN 0    AND 1
    df_60["AvgRS_kw"] = df_60["AvgRS_kw"].mask(df_60["AvgRS_kw"] < 0, None)
    df_60["AvgRS_kw"] = df_60["AvgRS_kw"].mask(df_60["AvgRS_kw"] > 1, None)

    # TotRS_MJ         BETWEEN 0  AND 15
    df_60["TotRS_MJ"] = df_60["TotRS_MJ"].mask(df_60["TotRS_MJ"] < 0, None)
    df_60["TotRS_MJ"] = df_60["TotRS_MJ"].mask(df_60["TotRS_MJ"] > 15, None)

    # TBRG_Rain        BETWEEN 0    AND 100
    df_60["TBRG_Rain"] = df_60["TBRG_Rain"].mask(df_60["TBRG_Rain"] < 0, None)
    df_60["TBRG_Rain"] = df_60["TBRG_Rain"].mask(df_60["TBRG_Rain"] > 100, None)

    # TBRG_Rain24RT2   BETWEEN 0    AND 250
    df_60["TBRG_Rain24RT2"] = df_60["TBRG_Rain24RT2"].mask(df_60["TBRG_Rain24RT2"] < 0, None)
    df_60["TBRG_Rain24RT2"] = df_60["TBRG_Rain24RT2"].mask(df_60["TBRG_Rain24RT2"] > 250, None)

    # Soil_TP5_VMC     BETWEEN 1    AND 65
    df_60["Soil_TP5_VMC"] = df_60["Soil_TP5_VMC"].mask(df_60["Soil_TP5_VMC"] < 1, None)
    df_60["Soil_TP5_VMC"] = df_60["Soil_TP5_VMC"].mask(df_60["Soil_TP5_VMC"] > 65, None)

    # Soil_TP20_VMC    BETWEEN 1    AND 65
    df_60["Soil_TP20_VMC"] = df_60["Soil_TP20_VMC"].mask(df_60["Soil_TP20_VMC"] < 1, None)
    df_60["Soil_TP20_VMC"] = df_60["Soil_TP20_VMC"].mask(df_60["Soil_TP20_VMC"] > 65, None)

    # Soil_TP50_VMC    BETWEEN 1    AND 65
    df_60["Soil_TP50_VMC"] = df_60["Soil_TP50_VMC"].mask(df_60["Soil_TP50_VMC"] < 1, None)
    df_60["Soil_TP50_VMC"] = df_60["Soil_TP50_VMC"].mask(df_60["Soil_TP50_VMC"] > 65, None)

    # Soil_TP100_VMC   BETWEEN 1    AND 65
    df_60["Soil_TP100_VMC"] = df_60["Soil_TP100_VMC"].mask(df_60["Soil_TP100_VMC"] < 1, None)
    df_60["Soil_TP100_VMC"] = df_60["Soil_TP100_VMC"].mask(df_60["Soil_TP100_VMC"] > 65, None)

    # Evap60           BETWEEN -0.5 AND 3
    df_60["Evap60"] = df_60["Evap60"].mask(df_60["Evap60"] < -0.5, None)
    df_60["Evap60"] = df_60["Evap60"].mask(df_60["Evap60"] > 3, None)

    # SolarRad         BETWEEN 0    AND 5
    df_60["SolarRad"] = df_60["SolarRad"].mask(df_60["SolarRad"] < 0, None)
    df_60["SolarRad"] = df_60["SolarRad"].mask(df_60["SolarRad"] > 5, None)

    # Press_hPa        BETWEEN 950  AND 1050
    df_60["Press_hPa"] = df_60["Press_hPa"].mask(df_60["Press_hPa"] < 950, None)
    df_60["Press_hPa"] = df_60["Press_hPa"].mask(df_60["Press_hPa"] > 1050, None)

    return df_60

def qa_24(df_24):
    date_col = "Date"

    # TMSTAMP     GREATER THAN 2007-01-01 00:00:00
    # delete rows outside of this range
    min_date = pandas.to_datetime("2007-01-01 00:00:00")
    df_24 = df_24[df_24.TMSTAMP > min_date]

    # StnID       BETWEEN 200   AND 800
    # delete rows outside of this range
    df_24 = df_24[(df_24.StnID >= 200) & (df_24.StnID <= 800)]

    # clean air temperature columns based on month

    # AvgAir_T             DEPENDS ON MONTH
    # range based on monthly ranges for MinAir_T (data_24) and MaxAir_T (data_24): min of MinAir_T range and max of MaxAir_T range
    # january: [-50,15]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["AvgAir_T"] < -50), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["AvgAir_T"] > 15), None)

    # february: [-50,20]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["AvgAir_T"] < -50), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["AvgAir_T"] > 20), None)

    # march: [-35,25]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["AvgAir_T"] < -35), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["AvgAir_T"] > 25), None)

    # april: [-25,35]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["AvgAir_T"] < -25), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["AvgAir_T"] > 35), None)

    # may: [-20,40]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["AvgAir_T"] < -20), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["AvgAir_T"] > 40), None)

    # june: [-10,50]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["AvgAir_T"] < -10), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["AvgAir_T"] > 50), None)

    # july: [0,50]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["AvgAir_T"] < 0), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["AvgAir_T"] > 50), None)

    # august: [-10,50]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["AvgAir_T"] < -10), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["AvgAir_T"] > 50), None)

    # september: [-20,40]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["AvgAir_T"] < -20), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["AvgAir_T"] > 40), None)

    # october: [-25,35]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["AvgAir_T"] < -25), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["AvgAir_T"] > 35), None)

    # november: [-35,30]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["AvgAir_T"] < -35), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["AvgAir_T"] > 30), None)

    # december: [-50,20]
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["AvgAir_T"] < -50), None)
    df_24["AvgAir_T"] = df_24["AvgAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["AvgAir_T"] > 20), None)
    # end of AvgAir_T

    # MaxAir_T             DEPENDS ON MONTH
    # january: [-35,15]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["MaxAir_T"] < -35), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["MaxAir_T"] > 15), None)

    # february: [-35,20]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["MaxAir_T"] < -35), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["MaxAir_T"] > 20), None)

    # march: [-30,25]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["MaxAir_T"] < -30), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["MaxAir_T"] > 25), None)

    # april: [-25,35]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["MaxAir_T"] < -25), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["MaxAir_T"] > 35), None)

    # may: [-15,40]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["MaxAir_T"] < -15), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["MaxAir_T"] > 40), None)

    # june: [0,50]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["MaxAir_T"] < 0), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["MaxAir_T"] > 50), None)

    # july: [10,50]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["MaxAir_T"] < 10), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["MaxAir_T"] > 50), None)

    # august: [5,50]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["MaxAir_T"] < 5), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["MaxAir_T"] > 50), None)

    # september: [-5,40]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["MaxAir_T"] < -5), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["MaxAir_T"] > 40), None)

    # october: [-15,35]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["MaxAir_T"] < -15), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["MaxAir_T"] > 35), None)

    # november: [-20,30]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["MaxAir_T"] < -20), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["MaxAir_T"] > 30), None)

    # december: [-30,20]
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["MaxAir_T"] < -30), None)
    df_24["MaxAir_T"] = df_24["MaxAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["MaxAir_T"] > 20), None)

    # end of MaxAir_T

    # MinAir_T             DEPENDS ON MONTH
    # january: [-50,5]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["MinAir_T"] < -50), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 1) & (df_24["MinAir_T"] > 5), None)

    # february: [-50,5]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["MinAir_T"] < -50), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 2) & (df_24["MinAir_T"] > 5), None)

    # march: [-35,10]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["MinAir_T"] < -35), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 3) & (df_24["MinAir_T"] > 10), None)

    # april: [-25,15]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["MinAir_T"] < -25), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 4) & (df_24["MinAir_T"] > 15), None)

    # may: [-20,20]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["MinAir_T"] < -20), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 5) & (df_24["MinAir_T"] > 20), None)

    # june: [-10,20]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["MinAir_T"] < -10), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 6) & (df_24["MinAir_T"] > 20), None)

    # july: [0,25]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["MinAir_T"] < 0), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 7) & (df_24["MinAir_T"] > 25), None)

    # august: [-10,20]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["MinAir_T"] < -10), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 8) & (df_24["MinAir_T"] > 20), None)

    # september: [-20,20]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["MinAir_T"] < -20), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 9) & (df_24["MinAir_T"] > 20), None)

    # october: [-25,15]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["MinAir_T"] < -25), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 10) & (df_24["MinAir_T"] > 15), None)

    # november: [-35,15]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["MinAir_T"] < -35), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 11) & (df_24["MinAir_T"] > 15), None)

    # december: [-50,10]
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["MinAir_T"] < -50), None)
    df_24["MinAir_T"] = df_24["MinAir_T"].mask((df_24[date_col].dt.month == 12) & (df_24["MinAir_T"] > 10), None)

    # end of MinAir_T

    # clean soil temperatures based on month
    # 5/20 cm soil columns

    # AvgSoil_T05          DEPENDS ON MONTH
    # MaxSoil_T05          DEPENDS ON MONTH
    # MinSoil_T05          DEPENDS ON MONTH
    # Avg_Soil_TP5_TempC   DEPENDS ON MONTH
    # Max_Soil_TP5_TempC   DEPENDS ON MONTH
    # Min_Soil_TP5_TempC   DEPENDS ON MONTH
    # Avg_Soil_TP20_TempC  DEPENDS ON MONTH
    # Max_Soil_TP20_TempC  DEPENDS ON MONTH
    # Min_Soil_TP20_TempC  DEPENDS ON MONTH
    shallow_depth_column_list = [
        "AvgSoil_T05",
        "MaxSoil_T05",
        "MinSoil_T05",
        "Avg_Soil_TP5_TempC",
        "Max_Soil_TP5_TempC",
        "Min_Soil_TP5_TempC",
        "Avg_Soil_TP20_TempC",
        "Max_Soil_TP20_TempC",
        "Min_Soil_TP20_TempC"
    ]

    for column in shallow_depth_column_list:
        # january: [-30,5]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 1) & (df_24[column] < -30), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 1) & (df_24[column] > 5), None)

        # february: [-30,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 2) & (df_24[column] < -30), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 2) & (df_24[column] > 10), None)

        # march: [-25,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 3) & (df_24[column] < -25), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 3) & (df_24[column] > 15), None)

        # april: [-25,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 4) & (df_24[column] < -25), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 4) & (df_24[column] > 15), None)

        # may: [-15,25]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 5) & (df_24[column] < -15), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 5) & (df_24[column] > 25), None)

        # june: [-10,35]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 6) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 6) & (df_24[column] > 35), None)

        # july: [5,35]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 7) & (df_24[column] < 5), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 7) & (df_24[column] > 35), None)

        # august: [-5,30]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 8) & (df_24[column] < -5), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 8) & (df_24[column] > 30), None)

        # september: [-10,25]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 9) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 9) & (df_24[column] > 25), None)

        # october: [-15,20]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 10) & (df_24[column] < -15), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 10) & (df_24[column] > 20), None)

        # november: [-20,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 11) & (df_24[column] < -20), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 11) & (df_24[column] > 15), None)

        # december: [-25,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 12) & (df_24[column] < -25), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 12) & (df_24[column] > 10), None)
    # end for loop (data_24 shallow soil temp)

    # Avg_Soil_TP50_TempC  DEPENDS ON MONTH
    # Max_Soil_TP50_TempC  DEPENDS ON MONTH
    # Min_Soil_TP50_TempC  DEPENDS ON MONTH
    # Avg_Soil_TP100_TempC DEPENDS ON MONTH
    # Max_Soil_TP100_TempC DEPENDS ON MONTH
    # Min_Soil_TP100_TempC DEPENDS ON MONTH
    deep_depth_column_list = [
        "Avg_Soil_TP50_TempC",
        "Max_Soil_TP50_TempC",
        "Min_Soil_TP50_TempC",
        "Avg_Soil_TP100_TempC",
        "Max_Soil_TP100_TempC",
        "Min_Soil_TP100_TempC"
    ]

    for column in deep_depth_column_list:
        # january: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 1) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 1) & (df_24[column] > 10), None)

        # february: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 2) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 2) & (df_24[column] > 10), None)

        # march: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 3) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 3) & (df_24[column] > 10), None)

        # april: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 4) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 4) & (df_24[column] > 10), None)

        # may: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 5) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 5) & (df_24[column] > 10), None)

        # june: [-5,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 6) & (df_24[column] < -5), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 6) & (df_24[column] > 15), None)

        # july: [0,20]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 7) & (df_24[column] < 0), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 7) & (df_24[column] > 20), None)

        # august: [0,20]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 8) & (df_24[column] < 0), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 8) & (df_24[column] > 20), None)

        # september: [0,20]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 9) & (df_24[column] < 0), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 9) & (df_24[column] > 20), None)

        # october: [-5,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 10) & (df_24[column] < -5), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 10) & (df_24[column] > 15), None)

        # november: [-5,15]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 11) & (df_24[column] < -5), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 11) & (df_24[column] > 15), None)

        # december: [-10,10]
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 12) & (df_24[column] < -10), None)
        df_24[column] = df_24[column].mask((df_24[date_col].dt.month == 12) & (df_24[column] > 10), None)
        # end for loop (data 24 deep soil temp)

    # BatMin               BETWEEN 8   AND 16
    df_24["BatMin"] = df_24["BatMin"].mask(df_24["BatMin"] < 8, None)
    df_24["BatMin"] = df_24["BatMin"].mask(df_24["BatMin"] > 16, None)

    # AvgRH                BETWEEN 10  AND 100
    df_24["AvgRH"] = df_24["AvgRH"].mask(df_24["AvgRH"] < 10, None)
    df_24["AvgRH"] = df_24["AvgRH"].mask(df_24["AvgRH"] > 100, None)

    # MaxRH                BETWEEN 10  AND 100
    df_24["MaxRH"] = df_24["MaxRH"].mask(df_24["MaxRH"] < 10, None)
    df_24["MaxRH"] = df_24["MaxRH"].mask(df_24["MaxRH"] > 100, None)

    # MinRH                BETWEEN 10  AND 100
    df_24["MinRH"] = df_24["MinRH"].mask(df_24["MinRH"] < 10, None)
    df_24["MinRH"] = df_24["MinRH"].mask(df_24["MinRH"] > 100, None)

    # Pluvio_Rain          BETWEEN 0   AND 250
    df_24["Pluvio_Rain"] = df_24["Pluvio_Rain"].mask(df_24["Pluvio_Rain"] < 0, None)
    df_24["Pluvio_Rain"] = df_24["Pluvio_Rain"].mask(df_24["Pluvio_Rain"] > 250, None)

    # MaxWS                BETWEEN 0   AND 50
    df_24["MaxWS"] = df_24["MaxWS"].mask(df_24["MaxWS"] < 0, None)
    df_24["MaxWS"] = df_24["MaxWS"].mask(df_24["MaxWS"] > 50, None)

    # AvgWS                BETWEEN 0   AND 50
    df_24["AvgWS"] = df_24["AvgWS"].mask(df_24["AvgWS"] < 0, None)
    df_24["AvgWS"] = df_24["AvgWS"].mask(df_24["AvgWS"] > 50, None)

    # AvgWD                BETWEEN 0   AND 360
    df_24["AvgWD"] = df_24["AvgWD"].mask(df_24["AvgWD"] < 0, None)
    df_24["AvgWD"] = df_24["AvgWD"].mask(df_24["AvgWD"] > 360, None)

    # AvgSD                BETWEEN 0   AND 360
    df_24["AvgSD"] = df_24["AvgSD"].mask(df_24["AvgSD"] < 0, None)
    df_24["AvgSD"] = df_24["AvgSD"].mask(df_24["AvgSD"] > 360, None)

    # AvgRS_kw             BETWEEN 0   AND 1
    df_24["AvgRS_kw"] = df_24["AvgRS_kw"].mask(df_24["AvgRS_kw"] < 0, None)
    df_24["AvgRS_kw"] = df_24["AvgRS_kw"].mask(df_24["AvgRS_kw"] > 1, None)

    # MaxRS_kw             BETWEEN 0   AND 3
    df_24["MaxRS_kw"] = df_24["MaxRS_kw"].mask(df_24["MaxRS_kw"] < 0, None)
    df_24["MaxRS_kw"] = df_24["MaxRS_kw"].mask(df_24["MaxRS_kw"] > 3, None)

    # TotRS_MJ             BETWEEN 0.5 AND 40
    df_24["TotRS_MJ"] = df_24["TotRS_MJ"].mask(df_24["TotRS_MJ"] < 0.5, None)
    df_24["TotRS_MJ"] = df_24["TotRS_MJ"].mask(df_24["TotRS_MJ"] > 40, None)

    # TBRG_Rain            BETWEEN 0   AND 250
    df_24["TBRG_Rain"] = df_24["TBRG_Rain"].mask(df_24["TBRG_Rain"] < 0, None)
    df_24["TBRG_Rain"] = df_24["TBRG_Rain"].mask(df_24["TBRG_Rain"] > 250, None)

    # Avg_Soil_TP5_VMC     BETWEEN 1   AND 65
    df_24["Avg_Soil_TP5_VMC"] = df_24["Avg_Soil_TP5_VMC"].mask(df_24["Avg_Soil_TP5_VMC"] < 1, None)
    df_24["Avg_Soil_TP5_VMC"] = df_24["Avg_Soil_TP5_VMC"].mask(df_24["Avg_Soil_TP5_VMC"] > 65, None)

    # Max_Soil_TP5_VMC     BETWEEN 1   AND 65
    df_24["Max_Soil_TP5_VMC"] = df_24["Max_Soil_TP5_VMC"].mask(df_24["Max_Soil_TP5_VMC"] < 1, None)
    df_24["Max_Soil_TP5_VMC"] = df_24["Max_Soil_TP5_VMC"].mask(df_24["Max_Soil_TP5_VMC"] > 65, None)

    # Min_Soil_TP5_VMC     BETWEEN 1   AND 65
    df_24["Min_Soil_TP5_VMC"] = df_24["Min_Soil_TP5_VMC"].mask(df_24["Min_Soil_TP5_VMC"] < 1, None)
    df_24["Min_Soil_TP5_VMC"] = df_24["Min_Soil_TP5_VMC"].mask(df_24["Min_Soil_TP5_VMC"] > 65, None)

    # Avg_Soil_TP20_VMC    BETWEEN 1   AND 65
    df_24["Avg_Soil_TP20_VMC"] = df_24["Avg_Soil_TP20_VMC"].mask(df_24["Avg_Soil_TP20_VMC"] < 1, None)
    df_24["Avg_Soil_TP20_VMC"] = df_24["Avg_Soil_TP20_VMC"].mask(df_24["Avg_Soil_TP20_VMC"] > 65, None)

    # Max_Soil_TP20_VMC    BETWEEN 1   AND 65
    df_24["Max_Soil_TP20_VMC"] = df_24["Max_Soil_TP20_VMC"].mask(df_24["Max_Soil_TP20_VMC"] < 1, None)
    df_24["Max_Soil_TP20_VMC"] = df_24["Max_Soil_TP20_VMC"].mask(df_24["Max_Soil_TP20_VMC"] > 65, None)

    # Min_Soil_TP20_VMC    BETWEEN 1   AND 65
    df_24["Min_Soil_TP20_VMC"] = df_24["Min_Soil_TP20_VMC"].mask(df_24["Min_Soil_TP20_VMC"] < 1, None)
    df_24["Min_Soil_TP20_VMC"] = df_24["Min_Soil_TP20_VMC"].mask(df_24["Min_Soil_TP20_VMC"] > 65, None)

    # Avg_Soil_TP50_VMC    BETWEEN 1   AND 65
    df_24["Avg_Soil_TP50_VMC"] = df_24["Avg_Soil_TP50_VMC"].mask(df_24["Avg_Soil_TP50_VMC"] < 1, None)
    df_24["Avg_Soil_TP50_VMC"] = df_24["Avg_Soil_TP50_VMC"].mask(df_24["Avg_Soil_TP50_VMC"] > 65, None)

    # Max_Soil_TP50_VMC    BETWEEN 1   AND 65
    df_24["Max_Soil_TP50_VMC"] = df_24["Max_Soil_TP50_VMC"].mask(df_24["Max_Soil_TP50_VMC"] < 1, None)
    df_24["Max_Soil_TP50_VMC"] = df_24["Max_Soil_TP50_VMC"].mask(df_24["Max_Soil_TP50_VMC"] > 65, None)

    # Min_Soil_TP50_VMC    BETWEEN 1   AND 65
    df_24["Min_Soil_TP50_VMC"] = df_24["Min_Soil_TP50_VMC"].mask(df_24["Min_Soil_TP50_VMC"] < 1, None)
    df_24["Min_Soil_TP50_VMC"] = df_24["Min_Soil_TP50_VMC"].mask(df_24["Min_Soil_TP50_VMC"] > 65, None)

    # Avg_Soil_TP100_VMC   BETWEEN 1   AND 65
    df_24["Avg_Soil_TP100_VMC"] = df_24["Avg_Soil_TP100_VMC"].mask(df_24["Avg_Soil_TP100_VMC"] < 1, None)
    df_24["Avg_Soil_TP100_VMC"] = df_24["Avg_Soil_TP100_VMC"].mask(df_24["Avg_Soil_TP100_VMC"] > 65, None)

    # Max_Soil_TP100_VMC   BETWEEN 1   AND 65
    df_24["Max_Soil_TP100_VMC"] = df_24["Max_Soil_TP100_VMC"].mask(df_24["Max_Soil_TP100_VMC"] < 1, None)
    df_24["Max_Soil_TP100_VMC"] = df_24["Max_Soil_TP100_VMC"].mask(df_24["Max_Soil_TP100_VMC"] > 65, None)

    # Min_Soil_TP100_VMC   BETWEEN 1   AND 65
    df_24["Min_Soil_TP100_VMC"] = df_24["Min_Soil_TP100_VMC"].mask(df_24["Min_Soil_TP100_VMC"] < 1, None)
    df_24["Min_Soil_TP100_VMC"] = df_24["Min_Soil_TP100_VMC"].mask(df_24["Min_Soil_TP100_VMC"] > 65, None)

    # EvapTot24            BETWEEN 0   AND 16
    df_24["EvapTot24"] = df_24["EvapTot24"].mask(df_24["EvapTot24"] < 0, None)
    df_24["EvapTot24"] = df_24["EvapTot24"].mask(df_24["EvapTot24"] > 16, None)

    return df_24