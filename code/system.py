import logging
from threading import Thread
import socket
from sys import exit
import json

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
        self._logger = logging.getLogger('Alarm System')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
        self._logger.setLevel(logging.DEBUG)
        # setting up tcp socket to receive
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._socket.bind(('127.0.0.1', 9090))
        except socket.error as e:
            self._logger.fatal('{}'.format(e))
            exit(1)
        # TODO: initialize sensor classes

    def run(self):
        """
        System checks sensors if armed and looks for inputs.
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
                # accept connections
                self._socket.listen(5)
                connection = self._socket.accept()
                if connection is not None:
                    self._logger.info("Received connection")
                    # create new thread an pass it the connection
                    t = Thread(target=self._connection_thread, args=(connection[0],))
                    self._threads.append(t)
                    t.start()
        except socket.error as e:
            self._logger.error('{}'.format(e))
        except KeyboardInterrupt as e:
            self._logger.info('{}'.format(e))
        finally:
            self._running = False
            self._join_threads()

    def _connection_thread(self, connection: socket.socket):
        """
        Process a connection
        :param connection: The socket connection to utilize
        """
        try:
            data = json.loads(bytearray(connection.recv(1024)).decode('utf-8'))
            if data is not None and isinstance(data, dict) and 'func' in data:
                func = data['func']
                if func == 'arm' and 'pin' in data and isinstance(data['pin'], str):
                    result = self._arm(data['pin'])
                    connection.send(json.dumps({'result': result}).encode('utf-8'))
                elif func == 'disarm' and 'pin' in data and isinstance(data['pin'], str):
                    result = self._disarm(data['pin'])
                    connection.send(json.dumps({'result': result}).encode('utf-8'))
                elif func == 'set_pin' and 'current_pin' in data and isinstance(data['current_pin'], str) \
                        and 'new_pin' in data and isinstance(data['new_pin'], str):
                    result = self._set_pin(data['current_pin'], data['new_pin'])
                    connection.send(json.dumps({'result': result}).encode('utf-8'))
                # TODO: other functions including photo stuff.
        except socket.error as e:
            self._logger.error('{}'.format(e))
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
        finally:
            connection.close()

    def _join_threads(self):
        """
        Joins all active threads before the program exits
        """
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
            self._logger.info('System is now armed')
            self._armed = True
            # TODO: device arming functions
            return True
        self._logger.info('Failed to arm system')
        return False

    def _disarm(self, pin: str):
        """
        Disarms the system if the system is armed and the pin is correct.
        :param pin: the system pin
        :return:
        """
        if self._armed and self._check_pin(pin):
            self._logger.info('System is now disarmed')
            self._armed = False
            # TODO: device disarm functions
            return True
        self._logger.info('Failed to disarmed system')
        return False

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
                self._logger.info('System pin set')
                return True
        self._logger.info('Failed to set system pin')
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

    def is_armed(self):
        """
        Returns the armed status of the system.
        :return: armed
        """
        return self._armed


# when this .py is called we will create a system object and run it.
if __name__ == '__main__':
    sys = System()
    sys.run()
