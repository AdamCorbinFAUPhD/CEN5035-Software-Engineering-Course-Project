from queue import Queue
from pir_event import PIREvent
from pir_event import PirEventType
import time
import RPi.GPIO as GPIO
import logging

"""
# PIR Sensor
The PIR Sensor will be use to detect movement within a room. For this project we will be using the HC-SR501 PIR Motion
Sensor. PIR stands for Passive Infrared which means it doesnt use any energy to detect signals
The PIR sensor consist of a main compost of the pyroelectric sensor which when exposed to heat generates an 
electric signal. A warm body emits infrared radiation(IR) and this pyroelectric sensor picks up this IR signals. On top 
of the pyroelectric sensor there is a fresnel lens bounces the IR signals onto the pyroelectric sensor.

## PIR Sensor pin description 
This PIR Sensor has 3 different pins: power, ground, and the output. The output pin will give a 5v or a 0v signal 
representing if the sensor has detected anything. 5v being that the sensor has detected IR signals and 0v for lack of 
IR signals. The power is expected to use 5v-20v input with 65mA current consumption.  

## Adjusting the PIR Sensor
The PIR Sensor module has 2 potentiometers.
1. Adjusting the sensitivity of the sensor to reach up tp 7 meters 
2. Adjusting the time the output signal stays high when IR signals have been detected The time can be adjusted between
0.3 seconds to 5 minutes.

## Trigger modes
The PIR Sensor module has a set of 3 pins to select the different types of trigger modes. 
1. Non-repeatable trigger mode : This is when the PIR Sensor has been triggered and the output time has lapsed, the 
output signal will automatically go back to zero 
2. Repeatable trigger mode : Similar to mode 1 but once the output time has lapsed and the IR signals still are detected
the output would remain high.
In a security system the Repeatable trigger mode is what we are looking for. For different applications like backyard 
light for night where you might only want to have it on for a short period of time.

## PIR Sensor stabilization 
The PIR Sensor when powering up need to have about a minute to stabilize to adjust to the area before any valid outputs 
will occur. The average IR gets computed during this time and when a warm body comes into range, thats where the spike 
of IR signal will occur causing the PIR Sensor to signal activity has occurred. 

## PIR Sensor add ons
The HC-SR501 PIR Motion Sensor has the ability to connect up to a few other modules right on this board for different
applications. You can add alight sensitive resistor or a photo resistor. This can be used with the PIR Sensor so that it
will make it only active in the dark. There is another place to add a thermal sensor which can factor readings into the
PIR Motion Sensor.

## Initial testing
Before connecting up the Raspberry Pi this PIR Sensor can be tested without reading the output values pin. To do this
experiment there needs to be an LED connected from the output pin to he ground pin. After the PIR Sensor has stabilized
the LED will then turn on when IR signals have triggered the PIR Sensor. This was a good way to test out the PIR Sensor
before adding any of the complexity of the Raspberry Pi.

Source for some of this data: https://www.youtube.com/watch?v=ZC_sEW3_694
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
        self._logger = logging.getLogger('AlarmSystem.pir_sensor')
        self._PIR_PIN = 19
        self.event_queue = Queue()  # Uses the PirEvent class to pass the messages

        GPIO.setup(self._PIR_PIN, GPIO.IN)
        # Adding a debounce time of 100ms just to insure we dont have a double trigger of a detection
        GPIO.add_event_detect(self._PIR_PIN, GPIO.BOTH, callback=lambda x: self.pid_callback())
        self._logger.debug('PIR object created')

    def read(self):
        # This will return True if the PIR has been triggered and False when no motion
        return GPIO.input(self._PIR_PIN)

    def pid_callback(self):
        """
        Callback to send the rising or falling PIREvent to the event_queue
        To determine if its falling or rising we check the value of the input put. If its low, then it was a falling
        event. If it was high, then it was a rising event
        """
        if GPIO.input(self._PIR_PIN) == 0:
            self._logger.debug('PIR Event Falling')
            self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.falling))
        else:
            self._logger.debug('PIR Event Rising')
            self.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.rising))
