import RPi.GPIO as GPIO

# This class is intended to control the RGB led
class LED:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self._LED_R = 16
        self._LED_G = 20
        self._LED_B = 21
        GPIO.setup(self._LED_R, GPIO.OUT)
        GPIO.setup(self._LED_G, GPIO.OUT)
        GPIO.setup(self._LED_B, GPIO.OUT)
        
    def red_on():
        GPIO.output(self._LED_R, True)
        
    def red_off():
        GPIO.output(self._LED_R, False)   
        
    def green_on():
        GPIO.output(self._LED_G, True)
        
    def green_off():
        GPIO.output(self._LED_G, False)   
        
    def blue_on():
        GPIO.output(self._LED_B, True)
        
    def blue_off():
        GPIO.output(self._LED_B, False)   
        

    