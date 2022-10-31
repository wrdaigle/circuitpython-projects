# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython status NeoPixel red, green, blue example."""
import time
import board
import neopixel

import time
import board

import neopixel


# fetch secrets
try:
    from secrets import secrets
except ImportError:
    print("WiFi and MQTT secrets are kept in secrets.py, please add them there!")
    raise

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.05

# connect to wifi and the mqtt broker
from msgHelper import msgHelper
messenger = msgHelper(**secrets)
messenger.connect()

mqtt_topic = "home/library/switch"
messenger.subscribe(mqtt_topic)


def on_message(_mqtt_client,_mqtt_topic, msg):
    if _mqtt_topic == mqtt_topic:
        if msg == 'ON':
            pixel.fill((0, 255, 0))
        if msg == 'OFF':
            pixel.fill((255, 0, 0))
messenger.mqtt_client.on_message = on_message

# while True:
#     messenger.loop()

while True:
    try:
        messenger.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        messenger.wifi.reset()
        messenger.mqtt_client.reconnect()
        continue
    time.sleep(1)

# n=0
# while n<1000:

#     # Poll the message queue
#     messenger.loop()

#     n+=1
#     time.sleep(1)

# messenger.unsubscribe(mqtt_topic)
# messenger.disconnect()

