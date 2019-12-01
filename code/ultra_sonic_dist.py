#!/usr/bin/python
import math

import RPi.GPIO as GPIO
import time
import logging

from pir_event import PIREvent, PirEventType


class UltraSonicDistanceSensor:
    def __init__(self, event_queue):
        GPIO.setmode(GPIO.BCM)

        self.PIN_TRIGGER = 18
        self.PIN_ECHO = 27

        GPIO.setup(self.PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        self._logger = logging.getLogger('AlarmSystem.ultra_sonic_distance')
        self._logger.debug('UltraSonicDistanceSensor object created')
        self.event_queue = event_queue

    def measure(self):
        GPIO.output(self.PIN_TRIGGER, GPIO.HIGH)

        time.sleep(0.00001)

        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
        pulse_start_time = time.time()
        pulse_end_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance_cm = round(pulse_duration * 17150, 2)
        # self._logger.debug('distance_cm' + str(distance_cm))
        return distance_cm

    def monitor_distance(self):
        time.sleep(3)
        # Stabilize by waiting for 3 seconds and then take 10 readings to get the average threshold distance.
        readings = []
        for i in range(10):
            reading = self.measure()
            readings.append(reading)
            self._logger.debug('reading:' + str(reading))
        average_dist = sum(readings) / len(readings)
        threshold = average_dist * .15
        self._logger.debug("average dis: " + str(average_dist))
        self._logger.debug("theshold: " + str(threshold))

        # Trigger an event if measure is off by the threshold for 1 second(4 readings)

        readings_count = 0
        while True:
            current_dist = self.measure()
            if abs(current_dist - average_dist) > threshold:
                readings_count += 1
            else:
                # Check if target has gone away
                if readings_count > 4:
                    self._logger.debug('Trigger Event Falling')
                    self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.falling))
                    pass
                readings_count = 0

            # Number of readings has been met, time to trigger an event
            if readings_count == 4:
                self._logger.debug('Trigger Event Rising')
                self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.rising))

            time.sleep(.5)
