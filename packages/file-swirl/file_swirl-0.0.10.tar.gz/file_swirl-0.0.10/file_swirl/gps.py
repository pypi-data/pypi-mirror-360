# from geopy.distance import geodesic
# from geopy.geocoders import Nominatim


def dms_to_decimal(dms_str):
    import re
    match = re.match(r"(\d+) deg (\d+)' ([\d.]+)\" ([NSEW])", dms_str)
    if not match:
        raise ValueError("Invalid DMS format")

    deg, minutes, seconds, direction = match.groups()
    decimal = float(deg) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

lat = dms_to_decimal("18 deg 58' 12.59\" N")
lon = dms_to_decimal("72 deg 49' 7.71\" E")

print(lat, lon)  # → 18.970164, 72.818808
radius_km = 10
center = (lat, lon)
coords = (lat, lon)


# geolocator = Nominatim(user_agent="geo_sorter")
# location = geolocator.reverse(coords)
# print(location.address)


# if coords and geodesic(center, coords).km <= radius_km:
#     print("Location is within radius.")
# else:
#     print("Location is outside radius.")
