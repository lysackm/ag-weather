import xarray as xr

ds = xr.open_dataset("../../../../data/merra/constants/constants.nc4")

print(ds)

print(ds.dzrz)
print(ds.dzrz.values)
print(ds.dzrz.values.min())
print(ds.dzrz.values.max())