# simple program that finds the maximum and minimum values for lat and long values for the weather stations in
# station-metadata-headers.csv
import pandas as pd

df = pd.read_csv("station-metadata-headers.csv")

print(df["LatDD"].idxmin())

print("max lat: ", df["LatDD"].max())
print("min lat: ", df["LatDD"].min())

print("max lon: ", df["LongDD"].max())
print("min lon ", df["LongDD"].min())
