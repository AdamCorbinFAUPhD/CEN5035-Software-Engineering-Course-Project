"""
This module is intended to have a human manually send events into the system. This will help test the system remotely
"""
import time
from threading import Timer

from pir_event import PIREvent, PirEventType
from system import System


class ManualTesting:
    def __init__(self):
        Timer(10, self.run, ()).start() # Wait for the system to finish initializing
        self.system = System()
        self.system.run()

    @staticmethod
    def print_actions():
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

    def run(self):
        while True:
            self.print_actions()
            self.get_and_process_user_entry()

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
            self.system.keypad.keypress_queue.put(user_entry)
        elif user_entry == "20":
            print("Clearing LED")
            self.system.led.clear_led()
        elif user_entry == "30":
            print("Armed: ", self.system.is_armed())
            print("LED Enabled: ", self.system.led.enabled)
            print("LED Color: ", self.system.led.color.name)
            print("Alarm active: ", self.system.alarm_active)
            print("System Locked: ", self.system.system_locked)
            print("Armed: ", self.system.is_armed())
        elif user_entry == "":
            pass
        elif user_entry == "":
            pass
        elif user_entry == "":
            pass


if __name__ == '__main__':
    test = ManualTesting()
    test.run()
