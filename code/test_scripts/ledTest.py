import RPi.GPIO as GPIO
import time

# Install instrictions 
# pip install RPi.GPIO

GPIO.setmode(GPIO.BCM)

LED_R = 16
LED_G = 20
LED_B = 21
GPIO.setup(LED_R, GPIO.OUT)
GPIO.setup(LED_G, GPIO.OUT)
GPIO.setup(LED_B, GPIO.OUT)


while 1:    
    GPIO.output(LED_R, True)
    time.sleep(1)
    GPIO.output(LED_R, False)
    
    GPIO.output(LED_G, True)
    time.sleep(1)
    GPIO.output(LED_G, False)
    
    GPIO.output(LED_B, True)
    time.sleep(1)
    GPIO.output(LED_B, False)

GPIO.cleanup()