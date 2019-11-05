import RPi.GPIO as GPIO

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
    _LED_R: bool
        The pin to control the red LED
    _LED_G: bool
        The pin to control the green LED
    _LED_B: bool
        The pin to control the blue LED
    """
    def __init__(self):
        # Initializing the GPIO Mode to Brodcom board pins which is what the T_Extension uses
        GPIO.setmode(GPIO.BCM)

        # LED control pins
        self._LED_R = 16
        self._LED_G = 20
        self._LED_B = 21
        GPIO.setup(self._LED_R, GPIO.OUT)
        GPIO.setup(self._LED_G, GPIO.OUT)
        GPIO.setup(self._LED_B, GPIO.OUT)

    def red_on(self):
        """
        Sets the red pin to True which enables the Red LED
        """
        GPIO.output(self._LED_R, True)

    def red_off(self):
        """
        Sets the red pin to False which disables the Red LED
        """
        GPIO.output(self._LED_R, False)

    def green_on(self):
        """
        Sets the green pin to True which enables the Green LED
        """
        GPIO.output(self._LED_G, True)

    def green_off(self):
        """
        Sets the green pin to False which disables the Green LED
        """
        GPIO.output(self._LED_G, False)

    def blue_on(self):
        """
        Sets the blue pin to True which enables the Blue LED
        """
        GPIO.output(self._LED_B, True)

    def blue_off(self):
        """
        Sets the green pin to False which disables the Green LED
        """
        GPIO.output(self._LED_B, False)
