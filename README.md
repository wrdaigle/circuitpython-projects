# circuitpython-mqtt-controller


## Viewing repl in terminal
ls /dev/tty.*
screen /dev/tty.board_name 115200

#copying files to board
rsync -avh ./examples/simpleSensorController/ /Volumes/CIRCUITPY --delete   

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


# for converting bmp images
cd /Users/bill/repos-personal/circuitpython-projects

## Setup (one-time)
Install uv if not already installed:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Convert icons
```
uv run python icons/convert_icons.py
```