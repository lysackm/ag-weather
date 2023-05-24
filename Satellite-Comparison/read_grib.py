# Experimentation with using xarray to load grib files
import xarray as xr
import matplotlib.pyplot as plt
import pygrib

# gribs = pygrib.open("../../../data/conpernicus/adaptor.mars.internal-2022.grib")
ds = xr.open_dataset("../../../data/conpernicus/ERA5-Land-1attr-grib/2m-temp-jan-2022.grib", engine="cfgrib")

# for grib in gribs:
#     print(grib.keys())
#     print(grib)

ds = ds - 273.15

print(ds.dims)

figure, ax = plt.subplots()

for i in range(15, 31):
    for j in range(0, 24, 8):
        print(j)
        ds.t2m[i, j].plot(cmap=plt.cm.coolwarm)
        plt.show()


