from time import sleep
import logging

import RPi.GPIO as GPIO
from enum import Enum


class LEDColor(Enum):
    """
    This class is used to represent the different colors of led
    """
    RED = 1,
    GREEN = 2,
    BLUE = 3,
    BLUE_RED = 4,  # Blue and Red
    YELLOW = 5,  # Red and Green which make yellow
    BLUE_GREEN = 6  # Blue and Red


""" 
This class is intended to control the RGB led module. There are only 3 pins that need to be initialized. 

The only minor thing to highlight is the type of GPIO mode that is being used is the BCM mode which is the 
actual pins on chip of the Raspberry Pi and doesnt not correspond to the header pins on the Raspberry Pi board.

Consideration - This module could be adapted to use PWM pins to control the brightness and create many different colors.
For this project there was only needed for the 3 colors and the combinations of the colors to be on. 
"""


class LED:
    """
    When controlling the LEDs setting the output to True truns on the LED and setting the output to False turns
    off the LED. Having multiple LEDS on at the same time is fine and will result in different colors. For example Red
    and Blue will create a purple like color(depending on the led module of course).

    Attributes
    ----------
    _LED_R: int
        The pin to control the red LED
    _LED_G: int
        The pin to control the green LED
    _LED_B: int
        The pin to control the blue LED
    """

    def __init__(self):
        # Initializing the GPIO Mode to Brodcom board pins which is what the T_Extension uses
        GPIO.setmode(GPIO.BCM)

        # LED control pins
        self._LED_R = 16
        self._LED_G = 20
        self._LED_B = 21
        self.color = LEDColor.RED
        self.enabled = False
        GPIO.setup(self._LED_R, GPIO.OUT)
        GPIO.setup(self._LED_G, GPIO.OUT)
        GPIO.setup(self._LED_B, GPIO.OUT)
        self.clear_led()
        self._logger = logging.getLogger('AlarmSystem.LED')
        self._logger.debug('LED object created')

    def clear_led(self, debug: bool = True):
        if debug: self._logger.debug('Clearing LED')
        self.enabled = False
        self._red_off()
        self._green_off()
        self._blue_off()

    def turn_off(self, color: LEDColor, debug: bool = True):
        """
        This method will control the LED to turn it off using the given color

        :param debug: way to force debug off or on
        :param color: Color to turn off
        :return:
        """
        if debug: self._logger.debug('Turning off LED')
        self.enabled = False
        if color == LEDColor.RED:
            self._red_off()
        elif color == LEDColor.GREEN:
            self._green_off()
        elif color == LEDColor.BLUE:
            self._blue_off()
        elif color == LEDColor.BLUE_GREEN:
            self._red_off()
            self._green_off()
        elif color == LEDColor.BLUE_RED:
            self._red_off()
            self._blue_off()
        elif color == LEDColor.YELLOW:
            self._red_off()
            self._green_off()

    def turn_on(self, color: LEDColor, debug: bool = True):
        """
        This method will control the LED to turn it on using the given color

        :param debug: way to force debug off or no
        :param color: Color to enable
        :return:
        """

        self.clear_led(debug)

        self.enabled = True
        self.color = color
        if color == LEDColor.RED:
            self._red_on()
            if debug: self._logger.debug('Setting LED to RED')
        elif color == LEDColor.GREEN:
            self._green_on()
            if debug: self._logger.debug('Setting LED to GREEN')
        elif color == LEDColor.BLUE:
            self._blue_on()
            if debug: self._logger.debug('Setting LED to BLUE')
        elif color == LEDColor.BLUE_GREEN:
            self._red_on()
            self._green_on()
            if debug: self._logger.debug('Setting LED to BLUE_GREEN')
        elif color == LEDColor.BLUE_RED:
            self._red_on()
            self._blue_on()
            if debug: self._logger.debug('Setting LED to RED_BLUE')
        elif color == LEDColor.YELLOW:
            self._red_on()
            self._green_on()
            if debug: self._logger.debug('Setting LED to RED_GREEN')

    def flash_led(self, color: LEDColor, flash_count=0, period=0.1, stay_on=False, keep_previous_state=True, debug: bool = True):
        """
        This method will have the ability to control the state of the led along with adding some animation of turning
        the led on & off to represent a flash. There might be a case where flashing is desired where the led does
        not need to remain on. The flash will have a period of .4 sec. Because of the flashing this call is blacking
        and will delay the program

        :param debug: A way to force the debug on or off
        :param keep_previous_state: If there was a led state enabled before, be sure to reset it back to that before
        :param period: duration the flash in seconds
        :param stay_on: The desire to leave the LED on in the event of a flashing animation
        :param color: The color to which is desired
        :param flash_count: The number of times the LED should flash
        :return:
        """
        last_color = self.color
        last_enable = self.enabled
        if debug: self._logger.debug('LED - Previous state= ' + last_color.name + " " + str(last_enable))
        self.clear_led()
        if debug: self._logger.debug('Flashing LED')
        for _ in range(flash_count):
            self.turn_on(color, debug)
            sleep(period)
            self.turn_off(color, debug)
            sleep(period)

        if stay_on:
            self.turn_on(color, debug)

        if keep_previous_state and last_enable:
            self.turn_on(last_color, debug)

    def _red_on(self):
        """
        Sets the red pin to True which enables the Red LED
        """
        GPIO.output(self._LED_R, True)

    def _red_off(self):
        """
        Sets the red pin to False which disables the Red LED
        """
        GPIO.output(self._LED_R, False)

    def _green_on(self):
        """
        Sets the green pin to True which enables the Green LED
        """
        GPIO.output(self._LED_G, True)

    def _green_off(self):
        """
        Sets the green pin to False which disables the Green LED
        """
        GPIO.output(self._LED_G, False)

    def _blue_on(self):
        """
        Sets the blue pin to True which enables the Blue LED
        """
        GPIO.output(self._LED_B, True)

    def _blue_off(self):
        """
        Sets the green pin to False which disables the Green LED
        """
        GPIO.output(self._LED_B, False)
