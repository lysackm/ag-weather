import pandas as pd
import geopy.distance


def closest_coordinate_mapping(df_1, df_2, primary_key_1, lat_1, long_1, primary_key_2, lat_2, long_2, dest_file):
    mapping = []

    for index_1, row_1 in df_1.iterrows():
        # arbitrarily large number
        min_distance = 10000
        identifier_2 = ""

        coords_1 = (row_1[lat_1], row_1[long_1])

        for index_2, row_2 in df_2.iterrows():
            coords_2 = (row_2[lat_2], row_2[long_2])

            dist = geopy.distance.geodesic(coords_1, coords_2)
            if dist < min_distance:
                min_distance = dist
                identifier_2 = row_2[primary_key_2]

        mapping.append(
            {primary_key_1: row_1[primary_key_1], primary_key_2: identifier_2, "distance": round(min_distance.km, 2)})

    df = pd.DataFrame(mapping)
    df = df.merge(df_1, how="left", on=primary_key_1)
    df = df.merge(df_2, how="left", on=primary_key_2)
    df.to_csv("metadata/" + dest_file, index=False)
    return df


def manitoba_eccc_mapped_to_mbag():
    df_eccc = pd.read_csv("./metadata/Manitoba_ECCC_metadata.csv")
    df_mbag = pd.read_csv("./metadata/station_metadata.csv")

    eccc_primary_key = "Climate ID"
    mbag_primary_key = "StnID"

    eccc_lat = "Latitude (Decimal Degrees)"
    eccc_lon = "Longitude (Decimal Degrees)"
    mbag_lat = "stn_lat"
    mbag_lon = "stn_long"

    closest_coordinate_mapping(df_eccc, df_mbag,
                               eccc_primary_key, eccc_lat, eccc_lon,
                               mbag_primary_key, mbag_lat, mbag_lon,
                               "ECCC_mbag_station_map.csv")


def main():
    manitoba_eccc_mapped_to_mbag()


if __name__ == "__main__":
    main()
