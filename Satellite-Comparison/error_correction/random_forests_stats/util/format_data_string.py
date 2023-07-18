import json


def print_data():
    with open('../random_forest_stats.json', 'r') as file:
        data = json.load(file)
        attrs_rmse = ["AvgAir_T", "RH", "Pluvio_Rain", "AvgWS", "Press_hPa", "SolarRad"]

        # print generic rmse
        for attr in attrs_rmse:
            print(str(data[attr]["merra_rmse"]) + " & " + str(data[attr]["era5_rmse"]) + " \\\\")

        # merra monthly rmse
        attrs_monthly_rmse = ["AvgAir_T", "AvgWS", "Pluvio_Rain", "Press_hPa", "RH", "SolarRad"]
        strings = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                   "November", "December"]
        for attr in attrs_monthly_rmse:
            monthly_data = data[attr]["merra"]

            for index in range(12):
                strings[index] = strings[index] + " & " + str(monthly_data[index])

        print("merra\n")
        for string in strings:
            print(string + "\\\\")

        # era5 monthly rmse
        strings = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                   "November", "December"]
        for attr in attrs_monthly_rmse:
            monthly_data = data[attr]["era5"]

            for index in range(12):
                strings[index] = strings[index] + " & " + str(monthly_data[index])

        print("era5\n")
        for string in strings:
            print(string + "\\\\")


print_data()