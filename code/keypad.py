from queue import Queue
from threading import Thread

import RPi.GPIO as GPIO

"""
This class is used to intercept the keypad entries
Here are the following steps in order to achieve our matrix 4x4 for all 16 keys
1. Set the columns as outputs to High
2. Set the rows pints as inputs with pull-up resistors
3. While checking for an individual key has been pressed, 1 at a time the output will be set to Low.
4. While the 1 output is set to low, we will check if any of the inputs as set to Low, this will indicate that a button 
    as been pressed
5. In order to avoid sending multiple keypress events while the button is held down, the system will wait till that 
    Low becomes High again
    
System design on how to use the keypad class: 
https://drive.google.com/file/d/1uPLhlLkEPWDTnYCvWuJ4w6HXwep1SSEe/view?usp=sharing

The Keypad creates its own thread to capture all the key presses and then sends each key press into the queue.
The intention would be there is a separate thread that would process the keys using the queue
"""


# Reference: Used this YouTube video on how to connect up the keypad: https://www.youtube.com/watch?v=yYnX5QodqQ4
class Keypad:
    """
    A class used to capture inputs from 4x4 membrane switch

    Attributes
    ----------

    _row_pins: list[ints]
        A list of the pin used for inputs for the membrane switch
    _column_pins: list[ints]
        A list of the pins used for output columns
    _matrix: list[list[chars]]
        A representation of which each button represents on the membrane switch
    thread: Thread
        thread in which the parsing of the keypresses will occur and captured
    keypress_queue: Queue
        Pass in the key that was pressed in the queue to be processed by a separate thread
    """

    def __init__(self, logger):
        """
        Initialization of the Keypad object. The only consideration is to make sure the thread is not started before
            the gpio pins are initialized.
        """

        # Initializing the GPIO Mode to Brodcom board pins which is what the T_Extension uses
        GPIO.setmode(GPIO.BCM)

        self.keypress_queue = Queue()
        self.thread = Thread(target=self.capture_keypress)

        self._row_pins = [22, 23, 24, 25]
        self._column_pins = [4, 5, 6, 13]
        self._matrix = [['1', '2', '3', 'A'],
                        ['4', '5', '6', 'B'],
                        ['7', '8', '9', 'C'],
                        ['*', '0', '#', 'D']]
        self._logger = logger

        for col in self._column_pins:
            GPIO.setup(col, GPIO.OUT)
            GPIO.output(col, 1)

        for row in self._row_pins:
            GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._logger.debug('Keypad object created')
        # Start monitoring for key presses
        self.thread.start()

    def capture_keypress(self):
        """
        Main processing to capture the keypress and put it into the queue

        """
        while True:
            for j in range(4):
                GPIO.output(self._column_pins[j], 0)
                for i in range(4):
                    if GPIO.input(self._row_pins[i]) == 0:
                        print(self._matrix[i][j])
                        # Wait till button becomes unpressed
                        while GPIO.input(self._row_pins[i]) == 0:
                            pass
                        # add the key that was pressed into the queue
                        self._logger.debug('Key entered:' + self._matrix[i][j])
                        self.keypress_queue.put(self._matrix[i][j])
                GPIO.output(self._column_pins[j], 1)
