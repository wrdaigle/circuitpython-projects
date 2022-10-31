
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

class tempSensor(object):
    def __init__(self, pin):
        # Initialize one-wire bus on board pin D5.
        ow_bus = OneWireBus(pin)
        self.ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

    def tempF(self,tempC):
        return round((tempC *(9/5))+32,1)

    def getTemp(self):
        # for some reason the temperature value is not always available
        temperature = None
        while not temperature:
            try:
                print(1)
                temperature = self.tempF(self.ds18.temperature)
     
            except:
                pass
        return temperature

