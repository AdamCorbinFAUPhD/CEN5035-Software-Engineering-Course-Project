"""
This module is intended to have a human manually send events into the system. This will help test the system remotely
"""
import time
from threading import Timer

import camera
from pir_event import PIREvent, PirEventType
from system import System


class ManualTesting:
    def __init__(self):
        """
        You will find that when testing using the manual test you will get messages from the system that might mix
        between the manual testing output. Thats because we have multiple treads going on at the same time. No clean
        way around this but just a heads up.
        """
        Timer(10, self.run, ()).start()  # Wait for the system to finish initializing
        self.system = System()
        self.system.run()

    @staticmethod
    def print_actions():
        print("")
        print("")
        print("Actions to simulate:")
        print("00 - List actions")
        print("11 - Send PIR Rising event")
        print("12 - Send PIR Falling event")
        print("0 - Send '0' Keypad event")
        print("1 - Send '1' Keypad event")
        print("Keypad events a a 1:1 mapping to the number entered")
        print("# Send '#' Keypad event")
        print("20 - Clear LED")
        print("30 - System status")
        print("40 - _arm the system")
        print("41 - de-_arm the system")
        print("50 - Take picture")
        print("")

    def run(self):
        user_entry = -1
        while True:
            # dont print the actions after the keypad entries (0-9)
            if user_entry == -1 or user_entry >= 10:
                self.print_actions()
            user_entry = self.get_and_process_user_entry()

    def get_and_process_user_entry(self):
        user_entry = input("Enter action: ")

        if user_entry == "00":
            self.print_actions()
        elif user_entry == "11":
            print("Sending Rising event")
            self.system.pir_sensor.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.rising))
        elif user_entry == "12":
            print("Sending Falling event")
            self.system.pir_sensor.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.falling))
        elif user_entry == "0" or user_entry == "1" or user_entry == "2" or user_entry == "3" or user_entry == "4" \
                or user_entry == "5" or user_entry == "6" or user_entry == "7" or user_entry == "8" \
                or user_entry == "9" or user_entry == "#":
            print("Sending key event: ", user_entry)
            self.system.keypad.keypress_queue.put(user_entry[0])
        elif user_entry == "20":
            print("Clearing LED")
            self.system.led.clear_led()
        elif user_entry == "30":
            print("Armed: ", self.system.is_armed)
            print("LED Enabled: ", self.system.led.enabled)
            print("LED Color: ", self.system.led.color.name)
            print("Alarm active: ", self.system.alarm_active)
            print("System Locked: ", self.system.system_locked)
            print("Armed: ", self.system.is_armed)
        elif user_entry == "40":
            self.system.is_armed = True
        elif user_entry == "41":
            self.system.is_armed = False
        elif user_entry == "50":
            camera.take_photo()
        elif user_entry == "":
            pass
        return int(user_entry)


if __name__ == '__main__':
    test = ManualTesting()
    test.run()
