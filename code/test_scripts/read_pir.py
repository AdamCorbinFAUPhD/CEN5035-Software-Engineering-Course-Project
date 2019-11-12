import RPi.GPIO as GPIO
import time

# Install instrictions 
# pip install RPi.GPIO

GPIO.setmode(GPIO.BCM)

PIR_PIN = 19
GPIO.setup(PIR_PIN, GPIO.IN)



while 1:
    print("PIR value:", GPIO.input(PIR_PIN))
    time.sleep(0.3)
    


GPIO.cleanup()