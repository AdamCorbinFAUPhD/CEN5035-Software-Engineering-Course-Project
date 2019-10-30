import RPi.GPIO as GPIO

class PIR_Sensor:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.PIR_PIN = 19
        GPIO.setup(self.PIR_PIN, GPIO.OUT)
    
    # This will return True if the PIR has been triggered and False when no motion
    def read(self):
        return GPIO.input(self.PIR_PIN)
        
    # TODO_AC - Consider looking into GPIO.add_event_detect callback instead of polling