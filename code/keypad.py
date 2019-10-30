import RPi.GPIO as GPIO

# This class is used to intercept the keypad entries
# Here are the following steps in order to acheive our matrix 4x4 for all 16 keys
# 1. Set the columns as outputs to High
# 2. Set the rows pints as inputs with pull-up resistors
# 3. While checking for an individual key has been pressed, 1 at a time the output will be set to Low.
# 4. While the 1 output is set to low, we will check if any of the inputs as set to Low, this will indicate that a button as been pressed
# 5. In order to avoid sending multiple keypress events while the button is held down, the system will wait till that Low becomes high again
class Keypad:
    def __init__(self):
        # Initilizing the GPIO Mode to Brodcom board pins which is what the T_Extention uses
        GPIO.setmode(GPIO.BCM)
        
        
        self._row_pins = [22,23,24,25]
        self._column_pins = [4,5,6,13]
        self._matrix = [ ['1','2','3','A'],
                         ['4','5','6','B'],
                         ['7','8','9','C'],
                         ['*','0','#','D'] ]
        
        
        for col in self._column_pins:
            print("col:", col)
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, 1)
        
        for row in self._row_pins:
            print("row:", row)
            GPIO.setup(row, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            
    #TODO_AC - Right now this does not return. Maybe we need to create a seperate thread and a queue to capture the keypresses. 
    # Something to look into once we have the system all set up.
    def start(self):
        while True:
            for j in range(4):
                GPIO.output(self._column_pins[j],0)
                for i in range(4):
                    if GPIO.input(self._row_pins[i]) == 0:
                        print(self._matrix[i][j])
                        # Wait till button becomes unpressed
                        while GPIO.input(self._row_pins[i]) == 0:
                            pass
                GPIO.output(self._column_pins[j],1)
