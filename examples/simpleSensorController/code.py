
import time
import board

# temp sensor module
from tempSensor import tempSensor 

tempSensor1 = tempSensor(board.D6)

# fetch secrets
try:
    from secrets import secrets
except ImportError:
    print("WiFi and MQTT secrets are kept in secrets.py, please add them there!")
    raise

# connect to wifi and the mqtt broker
from mqtt import mqtt
mqtt_client = mqtt(**secrets)
mqtt_client.connect()

mqtt_topic = "home/library/temp"


print("Subscribing to %s" % mqtt_topic)
mqtt_client.subscribe(mqtt_topic)

n=0
while n<1000:
    temperature = tempSensor1.getTemp()
    print("Publishing to %s" % mqtt_topic)
    mqtt_client.publish(mqtt_topic, temperature)
    n+=1
    time.sleep(5)

mqtt_client.unsubscribe(mqtt_topic)
mqtt_client.disconnect()

