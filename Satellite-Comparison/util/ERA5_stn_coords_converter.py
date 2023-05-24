# program that maps stations coordinates to coordinates that are on the ERA5-Land grid. Uses simple rounding,
# so it just snaps to the closest lat and long grid. Output is written to ERA5_stn_coord_mapping.csv.
# CSV is pandas friendly

import pandas as pd

stn_df = pd.read_csv("../../Cleaning-Data/cleaning-data/util/station-metadata.csv")

# stn_df[["LatDD", "LongDD", "StnID"]]

stn_df["LongDD"] = stn_df["LongDD"] + 0.03
stn_df[["LatDD", "LongDD"]] = stn_df[["LatDD", "LongDD"]].apply(lambda x: round(x, 1))
stn_df["LongDD"] = stn_df["LongDD"] - 0.03

print(stn_df[["LatDD", "LongDD"]])

stn_df[["LatDD", "LongDD", "StnID", "StationName"]].to_csv("./ERA5_stn_coord_mapping.csv")
