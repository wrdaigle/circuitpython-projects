
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT


class mqtt(object):
    def __init__(self, wifi_ssid, wifi_password, mqtt_broker, mqtt_port, mqtt_username, mqtt_password):
        
        self.mqtt_broker = mqtt_broker
        self.mqtt_port =  mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password

        # connect to wifi
        print("Connecting to {}".format(wifi_ssid))
        wifi.radio.connect(wifi_ssid, wifi_password)
        print("Connected to {}".format(wifi_ssid))

    def connect(self):

        # connect to wifi
        print("Connecting to {}".format(self.wifi_ssid))
        wifi.radio.connect(self.wifi_ssid, self.wifi_password)
        print("Connected to {}".format(self.wifi_ssid))
        
        pool = socketpool.SocketPool(wifi.radio)

        ### MQTT callback functions ###
        # Define callback methods which are called when events occur
        # pylint: disable=unused-argument, redefined-outer-name
        def _connect(mqtt_client, userdata, flags, rc):
            # This function will be called when the mqtt_client is connected
            # successfully to the broker.
            print("Connected to MQTT Broker!")
            print("Flags: {0}\n RC: {1}".format(flags, rc))
        def disconnect(mqtt_client, userdata, rc):
            # This method is called when the mqtt_client disconnects
            # from the broker.
            print("Disconnected from MQTT Broker!")
        def subscribe(mqtt_client, userdata, topic, granted_qos):
            # This method is called when the mqtt_client subscribes to a new feed.
            print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))
        def unsubscribe(mqtt_client, userdata, topic, pid):
            # This method is called when the mqtt_client unsubscribes from a feed.
            print("Unsubscribed from {0} with PID {1}".format(topic, pid))
        def publish(mqtt_client, userdata, topic, pid):
            # This method is called when the mqtt_client publishes data to a feed.
            print("Published to {0} with PID {1}".format(topic, pid))
        def message(client, topic, message):
            # Method called when a client's subscribed feed has a new value.
            print("New message on topic {0}: {1}".format(topic, message))


        # Set up a MiniMQTT Client
        mqtt_client = MQTT.MQTT(
            broker=self.mqtt_broker,
            port=self.mqtt_port,
            username=self.mqtt_username,
            password=self.mqtt_password,
            socket_pool=pool,
            ssl_context=ssl.create_default_context(),
        )

        # Connect callback handlers to mqtt_client
        mqtt_client.on_connect = _connect
        mqtt_client.on_disconnect = disconnect
        mqtt_client.on_subscribe = subscribe
        mqtt_client.on_unsubscribe = unsubscribe
        mqtt_client.on_publish = publish
        mqtt_client.on_message = message

        print("Attempting to connect to {}".format(mqtt_client.broker))
        mqtt_client.connect()
        self.mqtt_client = mqtt_client

    def publish(self,topic,value):
        self.mqtt_client.publish(topic, value)
        
    def subscribe(self, topic):
        print("Subscribing to {}".format(topic))
        self.mqtt_client.subscribe(topic)

    def unsubscribe(self, topic):
        print("Unsubscribing from {}".format(topic))
        self.mqtt_client.unsubscribe(topic)

    def disconnect(self):
        print("Disconnecting from {}".format(self.mqtt_client.broker))
        self.mqtt_client.disconnect()
    
    def loop(self):
        self.mqtt_client.loop()