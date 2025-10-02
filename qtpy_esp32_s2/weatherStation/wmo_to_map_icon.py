# SPDX-FileCopyrightText: 2025 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
"""
wmo_to_map_icon.py
Decoder for WMO Weather interpretation codes (WW) commonly used by OpenMateo.
Provides a short description, long description, and the openweathermap.org
("map") icon designation.
"""

# WMO code: [description, long_description, map_icon_designation]
wmo_to_map_icon = {
    "0": ["Clear", "Clear sky.", "01"],
    "1": ["MainlyClear", "Mainly clear sky.", "02"],
    "2": ["PartlyCloudy", "Partly cloudy sky.", "02"],
    "3": ["Overcast", "Overcast sky.", "03"],
    "45": ["Fog", "Foggy.", "50"],
    "48": ["Fog", "Depositing rime fog.", "50"],
    "51": ["Drizzle", "Light drizzle.", "10"],
    "53": ["Drizzle", "Moderate drizzle.", "09"],
    "55": ["Drizzle", "Dense drizzle.", "09"],
    "56": ["FreezingDrizzle", "Light freezing drizzle.", "09"],
    "57": ["FreezingDrizzle", "Dense freezing drizzle.", "09"],
    "61": ["Rain", "Slight rain.", "10"],
    "63": ["Rain", "Moderate rain.", "09"],
    "65": ["Rain", "Heavy rain.", "09"],
    "66": ["FreezingRain", "Light freezing rain.", "09"],
    "67": ["FreezingRain", "Heavy freezing rain.", "09"],
    "71": ["Snow", "Slight snow fall.", "13"],
    "73": ["Snow", "Moderate snow fall.", "13"],
    "75": ["Snow", "Heavy snow fall.", "13"],
    "77": ["Snow", "Snow grains falling.", "13"],
    "80": ["Rain", "Slight rain showers.", "10"],
    "81": ["Rain", "Moderate rain showers.", "09"],
    "82": ["Rain", "Violent rain showers.", "09"],
    "85": ["Snow", "Slight snow showers.", "13"],
    "86": ["Snow", "Heavy snow showers.", "13"],
    "95": ["Thunderstorm", "Thunderstorm.", "07"],
    "96": ["Thunderstorm", "Thunderstorm with slight hail.", "07"],
    "99": ["Thunderstorm", "Thunderstorm with heavy hail.", "07"],
}