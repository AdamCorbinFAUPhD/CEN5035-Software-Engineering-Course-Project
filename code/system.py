import logging
from threading import Thread


class System:
    # __init__ is the class constructor and is also where you must define your instance variables
    def __init__(self, pin: str = '123456'):
        # system starts disarmed, the '_' in front on the name indicates that this variable is supposed to be private
        # python does not have any other way to differentiate between public and private. This same annotation is also
        # used for private functions
        # The 'self' indicates that this variable is an instance variable much like 'this' is used in other languages.
        self._armed = False
        # setting to a default pin
        self._pin = pin
        # System needs to be running
        self._running = False
        # list to keep track of worker threads
        self._threads = []
        # Setup logging for this module.
        self._logger = logging.getLogger('AlarmSystem')
        fh = logging.FileHandler('as.log')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self._logger.addHandler(fh)
        self._logger.addHandler(ch)
        self._logger.setLevel(logging.DEBUG)
        # TODO: initialize sensor classes

    def run(self):
        """
        System checks sensors if armed and looks for inputs.
        :return:
        """
        if not self._running:
            self._running = True
            sensor_t = Thread(target=self._sensor_thread, args=())
            self._threads.append(sensor_t)
            sensor_t.start()
            self._main_thread()

    def _sensor_thread(self):
        """
        Thread for checking the sensor inputs
        """
        self._logger.debug('starting sensor thread')
        while self._running:
            # TODO: check sensors if required
            pass

    def _main_thread(self):
        """
        Main thread that checks for inputs from user devices and WebGUI
        :return:
        """
        self._logger.debug('starting main thread')
        try:
            while self._running:
                # TODO: check for input
                pass
        except KeyboardInterrupt as e:
            self._logger.info('{}'.format(e))
        finally:
            self._running = False
            self._join_threads()

    def _join_threads(self):
        self._logger.debug('joining threads...')
        for t in self._threads:
            t.join()
        self._logger.debug('threads joined')

    def _arm(self, pin: str):
        # to create function documentation in pycharm simple type '"' three times and hit enter.
        """
        Arms the system if the system is not armed and the pin is correct.
        :param pin: the system pin
        """
        if not self._armed and self._check_pin(pin):
            self._armed = True
            # TODO: device arming functions

    def _disarm(self, pin: str):
        """
        Disarms the system if the system is armed and the pin is correct.
        :param pin: the system pin
        :return:
        """
        if self._armed and self._check_pin(pin):
            self._armed = False
            # TODO: device disarm functions

    def _set_pin(self, current_pin: str, new_pin: str):
        """
        Sets a new pin for the system if the current_pin proved matches the system pin.
        :param current_pin: the current system pin
        :param new_pin: the new pin value
        :return if setting the pin was successful
        :rtype bool
        """
        if self._check_pin(current_pin):
            # check to see if the new pin is a length of 6 and if it only contains numbers
            if len(new_pin) == 6 and new_pin.isnumeric():
                self._pin = new_pin
                return True
        return False

    def _check_pin(self, pin: str):
        """
        Checks to see if the pin provided matches the system pin
        :param pin: the given pin to check
        :return: returns True if given pin matches system pin
        """
        if self._pin == pin:
            return True
        return False


# when this .py is called we will create a system object and run it.
if __name__ == '__main__':
    sys = System()
    sys.run()
