# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import os
import time
import ssl
import json
# import alarm
import board
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import supervisor

import terminalio
from adafruit_display_text import bitmap_label


def update_display(newText):

    # Update this to change the size of the text displayed. Must be a whole number.
    scale = 2

    text_area = bitmap_label.Label(terminalio.FONT, text=newText, scale=scale)
    text_area.x = 10
    text_area.y = 10
    board.DISPLAY.root_group = text_area


update_display("Hello, World!")

# from adafruit_onewire.bus import OneWireBus
# from adafruit_ds18x20 import DS18X20
import adafruit_dht

dht = adafruit_dht.DHT22(board.D6)

PUBLISH_DELAY = 5
MQTT_TOPIC = "state/temp-sensor"
USE_DEEP_SLEEP = False

wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("Connected to %s!" % os.getenv("CIRCUITPY_WIFI_SSID"))

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=os.getenv("MQTT_BROKER"),
    port=os.getenv("MQTT_PORT"),
    username=os.getenv("MQTT_USERNAME"),
    password=os.getenv("MQTT_PASSWORD"),
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

print("1 Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()
n = 0
while True:
    n+=1
    #try:
    temp_c = None
    humidity = None
    try:
        temp_c = dht.temperature
        humidity = dht.humidity
    except:
        print("Trouble getting temp")
    if temp_c and humidity:
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        print("Temperature: {0:0.1f}F".format(temp_f))
        update_display(
            "Temp: {0:0.1f}F\nHumidity: {1:0.1f}%\nMQTT Count: {2}".format(temp_f, humidity,n)
        )
        output = {"shop_temperature": temp_f, "shop_humidity": humidity}

        print("Publishing to %s" % MQTT_TOPIC)
        try:
            mqtt_client.publish(MQTT_TOPIC, json.dumps(output))
        except OSError as e:
            print("  MCU will soft reset in 30 seconds.")
            time.sleep(30)
            supervisor.reload()  #
            # mqtt_client.reconnect()
            # mqtt_client.publish(MQTT_TOPIC, json.dumps(output))

        last_update = time.monotonic()
        while time.monotonic() < (last_update + PUBLISH_DELAY):
            mqtt_client.loop(timeout=1)
    #except:
    #    print("There was an error")
