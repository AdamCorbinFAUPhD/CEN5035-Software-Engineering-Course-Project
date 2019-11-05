from queue import Queue
from pir_event import PIREvent
from pir_event import PirEventType
import time
import RPi.GPIO as GPIO

"""
The PIR Sensor will be use to detect movement within a room. For this project we will be using the HC-SR501 PIR Motion
Sensor. This sensor has 2 a few different options.  
TODO - go into the tech details on what a PIR sensor is and how it works. 
TODO - talk about how the sensor takes ~1min to stabilize before a trigger can happen
TODO - Talk about re-triggering
TODO - talk about initial testing of the PIR
TODO - Talk about the different modules that be be added to this module( temp sensor and ambient sensor) and how they can be used
"""


class PirSensor:
    """
    This PIR Sensor class will be used to capture any time the PIR has been triggered. Once the PIR sensor has been
    connected to the board, all that needs to be done is reading the input pin to capture the value. When the input
    value reads True(high) that means the sensor is detecting motion. When the input value reads False(low) that means
    no input detected. There will be 2 different events that will be sent to the event queue. 1. when the sensor first
    starts detecting motion. 2. when the sensor stops detecting motion. Look at the design as to why this was chosen.

    Assumptions
    ----------
    This class assumes that the PIR Sensor module has the re-triggering option enabled. This means that output will
    continuously report motion activation until the motion is no longer detected.

    Design
    ----------
    There were a few different options that were explored to capture input from the PIR Sensor.

    1. Having simple read the sensor to see if motion was detected. This works for simple applications but if the system
    is complex and needs to support many different sensors its possible to run into timing issues. For example the system
    could be checking something else out while sensor detects motion and by the time the system goes back to check the
    PIR Sensor, it could possibly not show detections.

    2. Having a callback event when an input was detected. The GPIO library has a software defined interrupt which
    handles the timing to ensure that no event of detection is missed. For our use case there will be 2 different
    callbacks. 1 for when the value goes from False -> True which is called rising. 2. for when the value goes from
    True -> False which is called falling. With the combination of these two events we can get finer control of what
    the sensor is detecting.

    Depending on the design of the full system either one would work. This class will use the 2nd option.

    Attributes
    ----------
    _PIR_PIN: int
        The pin source to see if PIR was triggered
    event_queue: Queue
        Pass in the timestamp and whether it was a Rising or Falling detection
    """
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self._PIR_PIN = 19
        self.event_queue = Queue()  # Uses the PirEvent class to pass the messages

        GPIO.setup(self._PIR_PIN, GPIO.IN)
        # Adding a debounce time of 100ms just to insure we dont have a double trigger of a detection
        GPIO.add_event_detect(self._PIR_PIN, GPIO.RISING, callback=self.pid_rising_callback, bouncetime=100)
        GPIO.add_event_detect(self._PIR_PIN, GPIO.FALLING, callback=self.pid_falling_callback, bouncetime=100)

    # This will return True if the PIR has been triggered and False when no motion
    def read(self):
        return GPIO.input(self._PIR_PIN)

    # TODO_AC - Consider looking into GPIO.add_event_detect callback instead of polling

    def pid_rising_callback(self):
        """
        Callback to send the rising PIREvent to the event_queue
        """
        self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.rising))

    def pid_falling_callback(self):
        """
        Callback to send the falling PIREvent to the event_queue
        """
        self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.falling))