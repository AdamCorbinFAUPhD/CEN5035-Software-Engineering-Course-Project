import glob
import logging
import os
import queue
from threading import Thread, Timer
import socket
from sys import exit
import json
from time import time, sleep
from multiprocessing import Process

from keypad import Keypad
from led import LED, LEDColor
from notifications import Notifications
from pir_event import PIREvent, PirEventType
from pir_sensor import PirSensor
from google_cal import Calendar
from ultra_sonic_dist import UltraSonicDistanceSensor
from watson_processing import Watson
import camera
import ui

"""
# Arming the system
To _arm the system, press # the system PIN. The system will allow the user to enter their pin within
10 seconds of first keypress. Otherwise the pin will get cleared to allow the user to re-enter.  On successful arming of 
the system the LED will flash green 5 times and the LED will be set to blue. When arming the system, the system needs to 
give at least 1 min for the home owner to leave the house before it sensing becomes active

# Disarming the system
When the system is armed the user can press the pin with a 10 second window from the first keypress. On successful 
disarming, the LED will flash green 5 times and the LED will then be turned off.

# Keypad entry behaviors
* Pressing # will reset the internal tracking of the user entry.
* Invalid entry of a pin will reset the internal tracking of the user entry and flash the LED yellow 5 times.
* The letter keys will have no effect on the system.
* Invalid entry of 5 times will lock the system for 5 minutes and set the yellow LED during this time. 

# Activating the alarm
When the system has been armed and the delay time has pass to allow for the home owner to leave the house the PIR is 
sensing for any IR sensing disturbance. If this case is met the alarm system will be active. 

Lesson learned: In python a tread can not be started twice. The initial idea was going to just start and stop the thread
which python doesnt like to do. From this we have an alarm thread that will always be running to just use a flag to keep
track of the alarm should be active or not.  

# Test cases
1. Arm the system by pressing the pin. Verify that the led flashed green 5 time and then the led then turned blue
2. Lock the system after 5 invalid pins when the system is disarmed. Verify led flashes red and then stays on red until
the timeout expires
3. Lock the system after 5 invalid pins when the system is armed. Verify led flashes red and then stays on red until
the timeout expires
4. Verify that when a pin in incorrectly entered that the led flashes red 5x
5. Verify the system can be disarmed on a correct pin entry by verifying that the green LED flashes green and then turns off.
6. Verify that when the system is armed and the PIR Sensor detects motion then the LED starts flashing red causing an active alarm
7. Verify that when the system has an active alarm where the LED is flashing red that when the user enters in the correct pin
the system will deactivate the alarm, _disarm the system, and flash green 5 times confirming a correct pin
8. Verify that when the system has an active alarm where the LED is flashing red that when the user enters in 
an incorrect pin, the yellow light flashes confirming an invalid pin and goes back to flashing red
9. Verify that when the calender event starts, that the system becomes armed.
10. Verify that when the calender event ends, that the system becomes diarmed.
"""


class System:
    # __init__ is the class constructor and is also where you must define your instance variables
    def __init__(self, pin: str = '123456'):
        # system starts disarmed, the '_' in front on the name indicates that this variable is supposed to be private
        # python does not have any other way to differentiate between public and private. This same annotation is also
        # used for private functions
        # The 'self' indicates that this variable is an instance variable much like 'this' is used in other languages.
        self.is_armed = False
        self.is_sensing = False  # is sensing is used to tell the system start looking for intruders
        # When arming a system, the system needs to give a delay in order to for the home owner to leave the house
        # without tripping the alarm system
        self._arm_time_delay = 5  # 1 * 60
        # setting to a default pin
        self._pin = pin
        self._user_pin_entry = ""
        self._user_first_key_entry_time = 0
        self._invalid_entry_count = 0

        # When user incorrectly enters in the pass code 4 times the system gets locked for 5min
        self.system_locked = False
        self._lock_time = 0
        self._lockout_duration = 10  # * 60  # currently set to 5 min but might consider less for testing
        self._pin_entry_max_timeout = 10  # Unit in seconds
        self._max_invalid_entry_before_system_lock = 4
        self.alarm_active = False

        # variable that tracks if a user modified the current state of the system
        # System needs to be running
        self._running = False
        # list to keep track of worker threads
        # DO NOT Create or start threads here!! Do it in the run method.
        self._threads = []

        # Setup logging for this module.
        self._logger = logging.getLogger('AlarmSystem')
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

        # Create the sub system items that the main system will monitor and control
        self.keypad = Keypad()
        self.led = LED()
        self.event_queue = queue.Queue()
        # self.pir_sensor = PirSensor(self.event_queue)  # Turned off for now due to interference
        self.ultra_sonic_distance_sensor = UltraSonicDistanceSensor(self.event_queue)
        self.calendar = Calendar()
        self.watson = Watson()
        self.notifications = Notifications()

        # The web UI
        self._web_client = ui.create_app()
        self._web_process = Process(target=self._web_client.run, args=('0.0.0.0', 1234))

    def run(self):
        """
        System will create and start the helper threads here to ensure synchronization
        """
        if not self._running:
            self._running = True
            sensor_t = Thread(target=self._sensor_thread, args=(), name="Sensor_Thread")
            self._threads.append(sensor_t)
            sensor_t.start()

            calendar_t = Thread(target=self._calendar_thread, args=(), name="Calendar_Thread")
            self._threads.append(calendar_t)
            calendar_t.start()

            k_thread = Thread(target=self.keypad.capture_keypress, args=(), name="Keypad_Thread")
            self._threads.append(k_thread)
            k_thread.start()

            alarm_t = Thread(target=self._alarm_thread, args=(), name="Alarm_Thread")
            self._threads.append(alarm_t)
            alarm_t.start()

            ultra_sonic_thread = Thread(target=self.ultra_sonic_distance_sensor.monitor_distance, args=(), name="Ultra_Sonic_Thread")
            self._threads.append(ultra_sonic_thread)
            ultra_sonic_thread.start()

            self._web_process.start()
            self._main_thread()
            self._logger.info('web client has started')

    def _process_keypress_event(self, keypress_event: str):
        """
        The process of keypress event to deactivate or activate a system

        :param keypress_event:
        :return:
        """
        # When the last entry has been greater than x seconds, just clear the past data because of the timeout req
        if time() - self._user_first_key_entry_time > self._pin_entry_max_timeout:
            self.reset_user_entry()

        if not self.is_armed:
            # start the timer for the first keypress and reset the user entry
            if keypress_event == "#":
                self.reset_user_entry()
                self._logger.debug('# entered, passcode reset')
            else:
                self._user_pin_entry += keypress_event
                self._logger.debug('current pass code:' + self._user_pin_entry)
                # Check for success, we will only check for valid entry when the sizes are the same
                if len(self._user_pin_entry) == len(self._pin):
                    self._arm(self._user_pin_entry)
        else:
            self._user_pin_entry += keypress_event
            self._logger.debug('current pass code:' + self._user_pin_entry)
            if len(self._user_pin_entry) == len(self._pin):
                self._disarm(self._user_pin_entry)

    def reset_user_entry(self):
        self._user_pin_entry = ""
        self._user_first_key_entry_time = time()

    def _alarm_thread(self):
        """
        This method is intended to handle the periodic processing when the alarm needs to go off. Sounding an alarm and led
        This is indented to be run in a thread and only run when alarm is active. The Pictures and video should be handled
        outside this thread when the alarm gets activated
        :return:
        """
        # Threads should reference this run flag for loops so the system can close and join them when stopped.
        while self._running:
            if self.alarm_active:
                while self.alarm_active and self._running:
                    self.led.turn_on(color=LEDColor.RED, debug=False)
                    sleep(.1)
                    self.led.turn_off(color=LEDColor.RED, debug=False)
                    sleep(.1)
            else:
                # Added to not eat up the processing. This give a max of .5 delay when the alarm can be started
                sleep(.5)

    def _process_pir_event(self, pir_event: PIREvent):
        """
        The process of a PIR event that can signal an alarm if the system is armed

        For the alarm it will be latched. A latched alarm means that once it has been activated someone has to
        manually disable it using the pin or some kind of confirmation.

        :param pir_event:
        :return:
        """

        if pir_event.event_type == PirEventType.falling:
            self._logger.debug('Falling event occurred')
            self.watson.send_movement_falling()
        elif pir_event.event_type == PirEventType.rising:
            if self.is_sensing:
                # First event that has occurred when armed, activate alarm thread
                if not self.alarm_active:
                    self.alarm_active = True
                    self._logger.info('Alarm has been activated')
                    self.watson.send_alarm_activated()
                    camera.take_photo()
                    camera.take_video()
                    sleep(1)
                    # Get the latest image taken and send that in the message
                    list_of_files = glob.glob("/home/pi/motion/camera1" + '/*-snapshot.jpg')
                    latest_file = max(list_of_files, key=os.path.getctime)
                    self.notifications.send_alert_message(latest_file)
                    camera.take_video()
            self._logger.debug('Rising event occurred')
            self.watson.send_movement_rising()

    def _sensor_thread(self):
        """
        Thread for checking the sensor inputs.
        """
        self._logger.debug('starting sensor thread')
        while self._running:
            """
            Keypress Event check
            In the even of the queue being empty, the exception queue.Empty will be thrown. Thus a Try catch will be
            needed to handle the normal case when no event is in the queue
            """
            try:
                """
                Monitor if the system is locked. When locked all keypress are ignored. After the 5min timer is up then
                the time is reset and the system is unlocked
                """
                keypress_event = self.keypad.keypress_queue.get_nowait()
                if not self.system_locked:
                    self._process_keypress_event(keypress_event)
                else:
                    # Once the lockout has expired, reset the invalid entry count and led status
                    if time() - self._lock_time > self._lockout_duration:
                        self.system_locked = False
                        self._invalid_entry_count = 0
                        self.led.turn_off(LEDColor.RED)

            except queue.Empty:
                pass

            """
            PIR Event check
            In the even of the queue being empty, the exception queue.Empty will be thrown. Thus a Try catch will be
            needed to handle the normal case when no event is in the queue
            """
            try:
                pir_event = self.event_queue.get_nowait()
                self._process_pir_event(pir_event)
            except queue.Empty:
                pass
            sleep(.2)
            # TODO - should we consider a delay in this tread to not eat up the process?

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
                    # self._logger.info("Received connection")
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
        Process a connection from the system client.
        :param connection: The socket connection to utilize
        """
        try:
            data = json.loads(bytes(connection.recv(1024)).decode('utf-8'))
            if data is not None and isinstance(data, dict) and 'func' in data:
                func = data['func']
                if func == 'arm_disarm' and 'pin' in data and isinstance(data['pin'], str):
                    if self.is_armed:
                        result = self._disarm(data['pin'])
                        connection.send(json.dumps({'result': result}).encode('utf-8'))
                    else:
                        result = self._arm(data['pin'])
                        connection.send(json.dumps({'result': result}).encode('utf-8'))
                elif func == 'set_pin' and 'current_pin' in data and isinstance(data['current_pin'], str) \
                        and 'new_pin' in data and isinstance(data['new_pin'], str):
                    result = self._set_pin(data['current_pin'], data['new_pin'])
                    connection.send(json.dumps({'result': result}).encode('utf-8'))
                elif func == 'take_photo':
                    camera.take_photo()
                    connection.send(json.dumps({'result': True}).encode('utf-8'))
                elif func == 'take_video':
                    camera.take_video()
                    connection.send(json.dumps({'result': True}).encode('utf-8'))
                elif func == 'status':
                    connection.send(json.dumps({'armed': self.is_armed, 'led_color': self.led.color.name,
                                                'led_enabled': self.led.enabled,
                                                "is_sensing": self.is_sensing}).encode('utf-8'))
        except socket.error as e:
            self._logger.error('{}'.format(e))
        except json.JSONDecodeError as e:
            self._logger.error('{}'.format(e))
        finally:
            connection.close()

    def _calendar_thread(self):
        """
        Thread that checks the google calendar once a second and takes action as appropriate.
        """
        while self._running:
            res = self.calendar.check_calendar()
            if res[0]:
                if res[1] and not self.is_armed:
                    self._arm(self._pin)
                elif not res[1] and self.is_armed:
                    self._disarm(self._pin)
            sleep(1)

    def _join_threads(self):
        """
        Joins all active threads before the program exits
        """
        self._logger.debug('joining threads...')
        for t in self._threads:
            t.join()
        self._logger.debug('threads joined')
        self._logger.debug('stopping UI process')
        self._web_process.close()
        self._logger.debug('stopped UI process')

    def _set_arm_after_delay(self):
        # Its possible we could have the system disarmed right way so we need to ignore this request to start sensing
        if self.is_armed:
            self._logger.info("System has been set to armed")
            self.is_sensing = True
            self.watson.send_armed()

    def _turn_off_led_after_system_unlocked(self):
        self.system_locked = False
        self._invalid_entry_count = 0
        self.led.turn_off(color=LEDColor.RED)

    def _arm(self, pin: str):
        # to create function documentation in pycharm simple type '"' three times and hit enter.
        """
        Arms the system if the system is not armed and the pin is correct.
        Assumption: The pin entry is the same length as the given pin. Upon a failed check the user entry is reset
        :param pin: the system pin
        """
        if not self.is_armed and self._check_pin(pin):
            self._logger.info('Passcode entered correctly. System will be armed in ' + str(self._arm_time_delay)
                              + " seconds")
            self.reset_user_entry()
            self._invalid_entry_count = 0
            self.led.flash_led(color=LEDColor.GREEN, flash_count=5)
            self.led.turn_on(color=LEDColor.BLUE)
            self.is_armed = True
            Timer(self._arm_time_delay, self._set_arm_after_delay).start()
            self.notifications.send_armed_message()
            return True
        else:
            return self.invalid_pin_entry()

    def invalid_pin_entry(self):
        self._invalid_entry_count += 1
        if self._invalid_entry_count > self._max_invalid_entry_before_system_lock:
            self.led.flash_led(color=LEDColor.YELLOW, flash_count=5)
            self.led.turn_on(color=LEDColor.RED)
            self._lock_time = time()
            self.system_locked = True
            self.notifications.send_locked_message()
            self._logger.info('System is locked')
            Timer(self._lockout_duration, self._turn_off_led_after_system_unlocked).start()
        else:
            turn_alarm_back_on = False
            # Handing the case where the alarm is active and we need to notify the user they entered in an incorrect pin
            # This case will disable the alarm while the led will flash yellow, then will turn the alarm back on
            if self.alarm_active:
                self.alarm_active = False
                turn_alarm_back_on = True
                sleep(.5)
            self.led.flash_led(color=LEDColor.YELLOW, flash_count=2)
            if turn_alarm_back_on:
                self.alarm_active = True

            self.reset_user_entry()
            self._logger.info('Failed to enter the pin correctly')
        return False

    def _disarm(self, pin: str):
        """
        Disarms the system if the system is armed and the pin is correct.
        :param pin: the system pin
        :return:
        """
        if self.is_armed:
            if self._check_pin(pin):
                # When the alarm is running, deactivate alarm
                if self.alarm_active:
                    self.alarm_active = False
                    self._logger.info('Alarm turned off')
                    self.watson.send_alarm_deactivated()
                self.reset_user_entry()
                self._logger.info('System is now disarmed')
                self.is_armed = False
                self.is_sensing = False
                self.watson.send_diarmed()
                self.led.clear_led()
                self.led.flash_led(color=LEDColor.GREEN, flash_count=5)
                self._invalid_entry_count = 0
                self.notifications.send_disarmed_message()
                return True
            else:
                return self.invalid_pin_entry()

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
        return self.is_armed


# when this .py is called we will create a system object and run it.
if __name__ == '__main__':
    sys = System()
    sys.run()
