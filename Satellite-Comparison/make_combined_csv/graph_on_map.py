import plotly.express as px
import pandas as pd

df = pd.read_csv("map_graph_data/AvgAir_T_output.csv")

df = df[["Station", "time", "stn_long", "stn_lat", "stn_attr", "era5_err", "era5_sqr_err"]]
print(df)

df.dropna(
    axis=0,
    how='any',
    inplace=True
)

color_scale = [(0, 'blue'), (1, 'red')]

print(1)

fig = px.scatter_mapbox(df,
                        lat="stn_lat",
                        lon="stn_long",
                        hover_name="Station",
                        hover_data=["stn_attr", "era5_err", "era5_sqr_err"],
                        color="era5_err",
                        color_continuous_scale=color_scale,
                        animation_frame="time",
                        size=df["era5_sqr_err"] * 10,
                        size_max=50,
                        zoom=8,
                        range_color=[-3, 3],
                        opacity=0.60,)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
print("2")
fig.show()
