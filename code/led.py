import RPi.GPIO as GPIO


# This class is intended to control the RGB led
class LED:
    def __init__(self):
        # Initilizing the GPIO Mode to Brodcom board pins which is what the T_Extention uses
        GPIO.setmode(GPIO.BCM)

        # LED control pins
        self._LED_R = 16
        self._LED_G = 20
        self._LED_B = 21
        GPIO.setup(self._LED_R, GPIO.OUT)
        GPIO.setup(self._LED_G, GPIO.OUT)
        GPIO.setup(self._LED_B, GPIO.OUT)
        
    def red_on(self):
        GPIO.output(self._LED_R, True)
        
    def red_off(self):
        GPIO.output(self._LED_R, False)   
        
    def green_on(self):
        GPIO.output(self._LED_G, True)
        
    def green_off(self):
        GPIO.output(self._LED_G, False)   
        
    def blue_on(self):
        GPIO.output(self._LED_B, True)
        
    def blue_off(self):
        GPIO.output(self._LED_B, False)   
