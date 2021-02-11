import threading
import time

import RPi.GPIO as GPIO


class ECHO(threading.Thread):
    
    def __init__(self, trigger, echo):

        threading.Thread.__init__(self)
        self.daemon = True

        self.trigger = trigger
        self.echo = echo
        self.distance = 0.0

        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, False)

        self.start()

        print("Ultrasonic distance measurement system initialized")

    def run(self):

        while True:

            GPIO.output(self.trigger, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger, False)
            startTime = time.time()
            stopTime = time.time()
            # while GPIO.input(self.echo) == 0:

            #    startTime = time.time()

            while GPIO.input(self.echo) == 1:

                stopTime = time.time()

            duration = stopTime - startTime
            self.distance = (duration * 34320) / 2

            time.sleep(0.5)