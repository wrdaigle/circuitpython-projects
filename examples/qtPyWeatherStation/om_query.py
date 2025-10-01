# SPDX-FileCopyrightText: 2025 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
"""
om_query.py
Query builder for Open_Meteo weather conditions Web API.
Location information is extracted from the settings.toml file.
Inspired by DJDevon3's Open-Meteo query builder.
"""
import os

LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
TIMEZONE = os.getenv("TIMEZONE")
TIMEZONE_OFFSET = os.getenv("TIMEZONE_OFFSET")
MEASUREMENT_UNITS = os.getenv("MEASUREMENT_UNITS")

if MEASUREMENT_UNITS == "METRIC":
    UNITS = ["mm", "celsius", "kmh"]
else:
    UNITS = ["inch", "fahrenheit", "mph"]

# Open-Meteo Free API
DATA_SOURCE = "https://api.open-meteo.com/v1/forecast?"
DATA_SOURCE += "latitude=" + LATITUDE
DATA_SOURCE += "&longitude=" + LONGITUDE
DATA_SOURCE += "&current=temperature_2m,"
DATA_SOURCE += "relative_humidity_2m,"
# DATA_SOURCE += "apparent_temperature,"
# DATA_SOURCE += "dew_point_2m,"
DATA_SOURCE += "is_day,"
# DATA_SOURCE += "precipitation,"
# DATA_SOURCE += "rain,"
# DATA_SOURCE += "showers,"
# DATA_SOURCE += "snowfall,"
DATA_SOURCE += "weather_code,"
# DATA_SOURCE += "cloud_cover,"
# DATA_SOURCE += "pressure_msl,"
# DATA_SOURCE += "surface_pressure,"
DATA_SOURCE += "wind_speed_10m,"
DATA_SOURCE += "wind_direction_10m,"
DATA_SOURCE += "wind_gusts_10m"
DATA_SOURCE += "&daily=sunrise,sunset"
DATA_SOURCE += "&temperature_unit=" + UNITS[1]
DATA_SOURCE += "&wind_speed_unit=" + UNITS[2]
# DATA_SOURCE += "&precipitation_unit=" + UNITS[0]
DATA_SOURCE += "&timeformat=unixtime"
DATA_SOURCE += "&timezone=" + TIMEZONE