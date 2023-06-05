import xarray as xr

ds = xr.open_dataset("../../../../data/merra/constants/constants.nc4")

print(ds)

print(ds.dzrz)
print(ds.dzgt5.values)
print(ds.dzgt5.values.min())
print(ds.dzgt5.values.max())