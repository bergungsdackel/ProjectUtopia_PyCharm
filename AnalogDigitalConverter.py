from ADS1x15 import ADS1015
import threading
import time

batteryEmpty = 11
batteryFull = 13.5


def scale(old_value, old_min, old_max, new_min, new_max):
    new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
    return new_value


def clamp(value, minOut, maxOut):
    if value > maxOut:
        return maxOut
    elif value < minOut:
        return minOut

    return value


class ANALOG_DIGITAL_CONVERTER(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.adc = ADS1015()
        self.channel = 0
        self.percentage = 0
        self.start()

    def run(self):
        while True:
            data = self.adc.read_adc(self.channel)
            # 1Bit=3mV
            voltage = data / 136.452095
            voltageScaled = scale(voltage, batteryEmpty, batteryFull, 0, 100)
            self.percentage = int(round(clamp(voltageScaled, 0, 100)))
            time.sleep(0.1)
