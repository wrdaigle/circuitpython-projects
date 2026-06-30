# circuitpython-mqtt-controller


## Viewing repl in terminal
```
ls /dev/tty.*
screen /dev/tty.board_name 115200
```

## Copying files to board
```
rsync -rltvh --whole-file --modify-window=2 ./qtpy_esp32_s2/weatherStation/ /Volumes/CIRCUITPY --delete --exclude='.DS_Store' --exclude='._*'
```

## secrets file
```
secrets = {
    'ssid' : 'YOUR_WIFI_NETWORK',
    'password' : 'YOUR_WIFI_PASSWORD',
    'mqtt_username' : 'YOUR_MQTT_USERNAME',
    'mqtt_password' : 'YOUR_MQTT_PASSWORD',
    'mqtt_broker' : 'YOUR_MQTT_BROKER_URL',
    'mqtt_port' : 1883                          # adjust if necessary
    }
```


## Converting icons
Run from project root:
```
uv run python icons/convert_icons.py
```

Downloads Adafruit mpy-cross for CircuitPython 9.1.4 (arm64) on first run, caches it in `icons/tools/`.
