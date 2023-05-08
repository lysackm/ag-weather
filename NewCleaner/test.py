import pandas
from columns import *

df = pandas.read_csv("data/carberry24.txt")

aa = df.iloc[:,15]

df.columns = ideal_columns_24_42

column = "Pluvio_Rain"

df[column] = pandas.to_numeric(df[column], errors="coerce")
df[column] = df[column].astype("float64", copy=False)

df.dropna(subset=["TMSTAMP"],inplace=True)

for val in df["TMSTAMP"]:
    print(val)




