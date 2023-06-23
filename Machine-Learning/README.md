# Neural Network Correction Model

- input would be the day and the model (merra/era5) value
- output would be the "expected" (station value) attribute value
- pytorch seems like a good fit


# Random Forest Proof of Concept

Initial Breakdown:
 1. Get data with several attributes
    - Probably hourly data, attributes being air temp, wind speed, 
      wind direction, rain, relative humidity, solar radiation.
    - in dataframe first
      - convert station data to netcdf?
 2. Do a variable importance test to find the correlation between 
    each variable and the output.
    - https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html
 3. Make a random forest, check results compared to actual
 4. Will need to compare it to some baseline (yearly average temp  
    plus minus some random temp, taken from Comparison of Multiple 
    Linear Regression, Cubist Regression, and Random Forest 
    Algorithms to Estimate Daily Air Surface Temperature from 
    Dynamic Combinations of MODIS LST Data)