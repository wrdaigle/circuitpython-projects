

import board
tft_cs = board.D9
tft_dc = board.D18
reset = board.D17


# SPDX-FileCopyrightText: 2025 JG for Cedar Grove Maker Studios
# SPDX-License-Identifier: MIT
"""
om_weather_display_code.py
Receives Open-Meteo local weather conditions.
Designed for the Adafruit ESP32-S3 4MB/2MB Feather (#5477) and
2.4" TFT FeatherWing (#3315).
"""

import time
# import board
import os
import gc
import rtc
import displayio
import fourwire
import wifi
import ssl
from digitalio import DigitalInOut, Direction
import pwmio
# import analogio
import supervisor
# from simpleio import map_range
import neopixel
import adafruit_ntp
import adafruit_connection_manager
import adafruit_requests
import adafruit_ili9341
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.roundrect import RoundRect

from wmo_to_map_icon import wmo_to_map_icon
from om_query import DATA_SOURCE


import busio
import adafruit_focaltouch
i2c = busio.I2C(board.SCL, board.SDA)
ft = adafruit_focaltouch.Adafruit_FocalTouch(i2c, debug=False)

# Weather Display Parameters
SAMPLE_INTERVAL = 600  # Check conditions (sec): typically 600 to 1200
NTP_INTERVAL = 3600  # Update local time from NTP server (sec): typically 3600
BRIGHTNESS = 0.75  # TFT and NeoPixel brightness setting
LIGHT_SENSOR = False  # True when ALS-PT19 sensor is connected to board.A3
REQUEST_TIMEOUT = 10  # Seconds to wait for Open-Meteo before giving up

# fmt: off
# Month and weekday lookup tables
WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# fmt: on

# Default colors
BLACK = 0x000000
RED = 0xFF0000
GREEN = 0x00FF00
ORANGE = 0xFF8811
YELLOW = 0xFFFF00
VIOLET = 0x9900FF
TEAL = 0x30CAD4
WHITE = 0xFFFFFF
DK_BLUE = 0x000080

# Define a few state/mode pixel colors
STARTUP = TEAL
NORMAL = DK_BLUE
FETCH = YELLOW
ERROR = RED

# Set start-up values
old_brightness = BRIGHTNESS
clock_tick = False

# Instantiate the display and darken during startup process
#   Adafruit 2.4" TFT FeatherWing with LITE connected to TX
lite = pwmio.PWMOut(board.TX, frequency=500)
lite.duty_cycle = 0  # Reduce display brightness during startup
displayio.release_displays()  # Release display resources
# display_bus = fourwire.FourWire(
#     board.SPI(), command=board.D10, chip_select=board.D9, reset=None
# )
display_bus = fourwire.FourWire(board.SPI(), command=tft_dc, chip_select=tft_cs, reset=reset)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
display.rotation = 0

# # Instantiate the red LED
# led = DigitalInOut(board.LED)
# led.direction = Direction.OUTPUT
# led.value = False

# Instantiate the NeoPixel
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel[0] = STARTUP
pixel.brightness = BRIGHTNESS / 10  # Dim the NeoPixel by a factor of 10

# # Instantiate the ALS-PT19 light sensor
# light_sensor = analogio.AnalogIn(board.A3)

# ### Helper Methods ###


# def adjust_brightness():
#     """Acquire the ALS-PT19 light sensor value and gradually adjust display
#     brightness based on ambient light. The display brightness ranges from 0.05
#     to BRIGHTNESS when the ambient light level falls between 5 to 200 lux.
#     Full-scale raw light sensor value (65535) is approximately 1500 Lux."""
#     global old_brightness
#     if not LIGHT_SENSOR:
#         return
#     raw = 0
#     for i in range(2000):
#         raw = raw + light_sensor.value
#     target_brightness = round(
#         map_range(raw / 2000 / 65535 * 1500, 5, 200, 0.05, BRIGHTNESS), 3
#     )
#     new_brightness = round(
#         old_brightness + ((target_brightness - old_brightness) / 5), 3
#     )
#     disp_brightness(new_brightness)
#     pixel.brightness = new_brightness
#     old_brightness = new_brightness


def alert(text=""):
    """Flash text in the message area and print to REPL.
    :param str text: Message text limited to 20 characters. Default is
    an empty string (no message)."""
    if not text or text == "":
        return
    text = text[:20]
    print("ALERT: " + text)
    display_message.color = RED
    display_message.text = text
    time.sleep(0.1)
    display_message.color = YELLOW
    time.sleep(0.1)
    display_message.color = RED
    time.sleep(0.1)
    display_message.color = YELLOW
    time.sleep(0.5)
    display_message.color = None


def am_pm(hour):
    """Provide an adjusted hour and AM/PM string to create to a
    12-hour time string.
    :param int hour: The clock hour. No default."""
    if hour < 12:
        if hour == 0:
            hour = 12
        return hour, "AM"
    if hour == 12:
        return 12, "PM"
    if hour > 12:
        hour = hour - 12
    return hour, "PM"


def disp_brightness(new_brightness):
    """Set the TFT display brightness.
    :param float new_brightness: The display brightness 0.0 to 1.0. No default."""
    new_brightness = min(max(new_brightness, 0), 1.0)
    lite.duty_cycle = int(new_brightness * 0xFFFF)


def display_local_time(repl=True):
    """Show the local time on-screen and in the REPL.
    :param bool repl: Print time string in the REPL. Default is True (print
    in the REPL)."""
    hour, suffix = am_pm(time.localtime().tm_hour)
    display_time = f"{hour:2d}:{time.localtime().tm_min:02d} {suffix}"
    clock_digits.text = display_time
    if repl:
        print(f"  Local Time: {display_time}")


def get_local_time():
    """Update the local time from the NTP server."""
    pixel[0] = FETCH
    alert("UPDATE TIME")
    try:
        ntp = adafruit_ntp.NTP(pool, tz_offset=os.getenv("TIMEZONE_OFFSET"))
        rtc.RTC().datetime = ntp.datetime
    except Exception as time_err:
        print(f"  ERROR: Fetch local time: {time_err}")
        alert(f"NTP error: {time_err}")
    alert("  READY")
    pixel[0] = NORMAL


# def toggle_clock_tick():
#     """Toggle the clock tick indicator and red LED."""
#     global clock_tick
#     if clock_tick:
#         clock_tick_mask.fill = RED
#         # led.value = True
#     else:
#         clock_tick_mask.fill = None
#         # led.value = False
#     clock_tick = not clock_tick

def update_display():
    """Fetch latest weather condition values from Open-Mateo and
    update the display."""
    pixel[0] = FETCH
    alert("UPDATE CONDITIONS")

    # Update day and date
    wday = time.localtime().tm_wday
    month = time.localtime().tm_mon
    day = time.localtime().tm_mday
    year = time.localtime().tm_year
    clock_day_mon_yr.text = f"{WEEKDAY[wday]}  {MONTH[month - 1]} {day:02d}, {year:04d}"

    # Get weather conditions from Open-Meteo free API
    gc.collect()  # Prepare to use memory for query result
    # print(f"  mem_free() before fetch: {gc.mem_free() / 1000:.3f}kB")
    

    om_json = None
    try:
        print(DATA_SOURCE)
        with requests.get(DATA_SOURCE, timeout=REQUEST_TIMEOUT) as payload:
            if payload.status_code != 200:
                raise RuntimeError(f"Bad status {payload.status_code}")
            om_json = payload.json()
        gc.collect()  # Cleans up 10kB of json payload rubbish
        pixel[0] = NORMAL
    except Exception as data_source_err:
        pixel[0] = ERROR
        print(f"ERROR: Fetch data from data source: {data_source_err}")
        alert(f"Weather fetch error")
        # Instead of freezing, just return and try again next cycle
        return

    # print(f"  mem_free()  after fetch: {gc.mem_free() / 1000:.3f}kB")

    if om_json is None:
        # If fetch failed, skip update
        return

    try:
        # Calculate and update sunrise/sunset
        sset = time.localtime(om_json["daily"]["sunset"][0] + om_json["utc_offset_seconds"])
        srise = time.localtime(
            om_json["daily"]["sunrise"][0] + om_json["utc_offset_seconds"]
        )
        sunrise.text = f"rise {am_pm(srise.tm_hour)[0]:2d}:{srise.tm_min:02d} {am_pm(srise.tm_hour)[1]}"
        sunset.text = (
            f"set {am_pm(sset.tm_hour)[0]:2d}:{sset.tm_min:02d} {am_pm(sset.tm_hour)[1]}"
        )

        wind_dir = f"{wind_direction(om_json['current']['wind_direction_10m'])}"
        if om_json["current_units"]["wind_speed_10m"] == "mp/h":
            wind_units = "MPH"
        else:
            wind_units = "km/H"
        windspeed.text = (
            f"{wind_dir} {om_json['current']['wind_speed_10m']:.0f} {wind_units}"
        )
        windgust.text = f"gusts {om_json['current']['wind_gusts_10m']:.0f} {wind_units}"

        # Update weather description
        description.text = wmo_to_map_icon[f"{om_json['current']['weather_code']}"][0]
        long_desc.text = wmo_to_map_icon[f"{om_json['current']['weather_code']}"][1]

        # Create icon filename
        if om_json["current"]["is_day"]:
            icon_suffix = "d"  # Day
        else:
            icon_suffix = "n"  # Night
        icon = wmo_to_map_icon[f"{om_json['current']['weather_code']}"][2]
        icon_file = f"/icons_80x80/{icon}{icon_suffix}.bmp"

        # Update icon graphic
        image_group.pop(0)
        try:
            icon_image = displayio.OnDiskBitmap(icon_file)
            icon_bg = displayio.TileGrid(
                icon_image,
                pixel_shader=icon_image.pixel_shader,
                x=(WIDTH // 2) - 40,
                y=(HEIGHT // 2) - 40,
            )
            image_group.insert(0, icon_bg)
        except Exception as icon_err:
            print(f"Icon load error: {icon_err}")
            alert("Icon error")

        print(om_json)

        # Update temperature and humidity
        temperature.text = f"{om_json['current']['temperature_2m']:.0f}{om_json['current_units']['temperature_2m']}"
        humidity.text = f"{om_json['current']['relative_humidity_2m']}{om_json['current_units']['relative_humidity_2m']} RH"

        gc.collect()  # Clean up displayio rendering rubbish

        alert("  READY")
        pixel[0] = NORMAL
    except Exception as display_err:
        print(f"Display update error: {display_err}")
        alert("Display error")


def wind_direction(heading):
    """Provide a one or two character string representation of the compass
    heading value. Returns '--' if heading is None.
    :param int heading: The compass heading. No default."""
    if heading is None:
        return "--"
    return ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][
        int(((heading + 22.5) % 360) / 45)
    ]


# ### Primary Initialization Process ###

# Connect to the Wi-Fi AP specified in settings.toml
pixel[0] = FETCH
print("Connecting to Wi-Fi...")
while not wifi.radio.ipv4_address:
    try:
        wifi.radio.connect(
            os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
        )
    except Exception as connect_err:
        pixel[0] = ERROR
        print("ERROR: Wi-Fi Connection Error:", connect_err)
        alert("Wi-Fi error")
        print("    retrying in 10 seconds")
        time.sleep(10)
        continue
print("  Wi-Fi Connected")
pixel[0] = NORMAL

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

pixel[0] = STARTUP

# Load the text fonts from the fonts folder
SMALL_FONT = bitmap_font.load_font("/fonts/Arial-12.bdf")
MEDIUM_FONT = bitmap_font.load_font("/fonts/Arial-16.bdf")
LARGE_FONT = bitmap_font.load_font("/fonts/Arial-Bold-24.bdf")

# Define the TFT's display size
WIDTH = display.width
HEIGHT = display.height

# Define the display group for text and graphic icon
image_group = displayio.Group()
display.root_group = image_group  # Select the group
disp_brightness(BRIGHTNESS)  # Watch it build (for the fun of it)

# ### Define display graphic icon, label, and value areas ###
# Create a replaceable icon background layer as image_group[0]
try:
    icon_image = displayio.OnDiskBitmap("/icons_80x80/01d.bmp")
    icon_bg = displayio.TileGrid(
        icon_image,
        pixel_shader=icon_image.pixel_shader,
        x=(WIDTH // 2) - 40,
        y=(HEIGHT // 2) - 40,
    )
    image_group.append(icon_bg)
except:
    pass

# Define the project messaging label
display_message = Label(SMALL_FONT, text=" ", color=YELLOW)
display_message.anchor_point = (0.5, 0.5)
display_message.anchored_position = (display.width // 2, 231)
image_group.append(display_message)
alert("STARTUP")

# Define the day/date and clock labels; update and display local time
clock_day_mon_yr = Label(MEDIUM_FONT, text=" ")
clock_day_mon_yr.anchor_point = (0, 0)
clock_day_mon_yr.anchored_position = (10, 15)
clock_day_mon_yr.color = TEAL
image_group.append(clock_day_mon_yr)

clock_digits = Label(MEDIUM_FONT, text=" ")
clock_digits.anchor_point = (1.0, 0)
clock_digits.anchored_position = (display.width - 10, 15)
clock_digits.color = WHITE
image_group.append(clock_digits)

get_local_time()
display_local_time()

# Define wind speed and gust labels
windspeed = Label(MEDIUM_FONT, text=" ")
windspeed.anchor_point = (0, 0)
windspeed.anchored_position = (10, 44)
windspeed.color = WHITE
image_group.append(windspeed)

windgust = Label(SMALL_FONT, text=" ")
windgust.anchor_point = (0, 0)
windgust.anchored_position = (10, 65)
windgust.color = RED
image_group.append(windgust)

# Define sunrise and sunset labels
sunrise = Label(SMALL_FONT, text=" ")
sunrise.anchor_point = (1.0, 0.0)
sunrise.anchored_position = (display.width - 10, 44)
sunrise.color = YELLOW
image_group.append(sunrise)

sunset = Label(SMALL_FONT, text=" ")
sunset.anchor_point = (1.0, 0.0)
sunset.anchored_position = (display.width - 10, 60)
sunset.color = ORANGE
image_group.append(sunset)

# Define the short and long description labels
description = Label(MEDIUM_FONT, text=" ")
description.anchor_point = (0, 0)
description.anchored_position = (10, 178)
description.color = WHITE
image_group.append(description)

long_desc = Label(SMALL_FONT, text=" ")
long_desc.anchor_point = (0, 0)
long_desc.anchored_position = (10, 210)
long_desc.color = TEAL
image_group.append(long_desc)

# Define the temperature and humidity labels
temperature = Label(LARGE_FONT, text=" ")
temperature.anchor_point = (1.0, 0)
temperature.anchored_position = (display.width - 10, 172)
temperature.color = WHITE
image_group.append(temperature)

humidity = Label(SMALL_FONT, text=" ")
humidity.anchor_point = (1.0, 0)
humidity.anchored_position = (display.width - 10, 215)
humidity.color = TEAL
image_group.append(humidity)

# # Define the clock tick indicator shap
# clock_tick_mask = RoundRect(310, 4, 7, 8, 1, fill=VIOLET, outline=None, stroke=0)
# image_group.append(clock_tick_mask)

gc.collect()  # Clean up displayio rendering rubbish

# Initialize interval timing variables
last_weather_update = time.monotonic()
last_time_update = time.monotonic()

# Initially display the conditions
update_display()  # Fetch initial data from Open-Mateo

# ### Main Loop ###
while True:
    current_time = time.monotonic()

    # Update weather every SAMPLE_INTERVAL seconds
    if current_time - last_weather_update > SAMPLE_INTERVAL:
        update_display()
        display_local_time()
        last_weather_update = current_time

    # Update network time every NTP_INTERVAL seconds
    if current_time - last_time_update > NTP_INTERVAL:
        get_local_time()
        display_local_time()
        last_time_update = current_time

    # Update time display every second
    # toggle_clock_tick()
    display_local_time(repl=False)

    # # Watch for and adjust to ambient light changes
    # adjust_brightness()

    try:
        if ft.touched:
            print(ft.touches)
        # else:
        #     print('no touch')
    except:   
        pass  
    
    # Adjust wait time to as close to 1 sec as possible
    time.sleep(max(min(1.0 - (time.monotonic() - current_time), 0.15), 0))