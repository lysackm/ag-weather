import glob
import pandas as pd

files = glob.glob("output/*.csv")

for file in files:
    df = pd.read_csv(file)
    df = df.round(5)
    df.to_csv(file)
