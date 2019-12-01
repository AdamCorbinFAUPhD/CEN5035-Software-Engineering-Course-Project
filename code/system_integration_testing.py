"""
Module is intended to automatically test the system package with how it integrates with the sub systems. The main idea
would be to simulate keypresses and PIR events to feed into the queues that the system uses to take actions.
"""
import logging
import time
from threading import Thread
from time import sleep

from pir_event import PIREvent, PirEventType
from system import System


class SystemIntegrationTesting:
    def __init__(self):
        self.total_testcase_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.system_to_test = System()
        self._logger = logging.getLogger('System Testing')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
        self._logger.setLevel(logging.DEBUG)

    def test(self, expected, actual):
        if expected == actual:
            self.pass_count += 1
            self._logger.debug("Pass - Expected=" + str(expected) + " Actual=" + str(actual))
        else:
            self.fail_count += 1
            self._logger.debug("Fail - Expected=" + str(expected) + " Actual=" + str(actual))
        self.total_testcase_count += 1

    def print_results(self):
        self._logger.debug("---------")
        self._logger.debug("Results\tCount\tPercent")
        self._logger.debug("Pass" + "\t" + str(self.pass_count) + "\t" + str(round(self.pass_count / self.total_testcase_count * 100, 2)))
        self._logger.debug("Fail" + "\t" + str(self.fail_count) + "\t" + str(round(self.fail_count / self.total_testcase_count * 100, 2)))
        self._logger.debug("Total" + "\t" + str(self.total_testcase_count))
        self._logger.debug("---------")

    def run(self):
        Thread(target=self.system_to_test.run, args=(), name="Sensor_Thread").start()
        sleep(10)
        self._logger.debug("Starting up Integration testing")
        # Test case #### for Armed.
        self.system_to_test._process_keypress_event("123456")
        # Wait 1 sec for arm delay
        sleep(self.system_to_test._arm_time_delay + 1)
        self.test(expected=True, actual=self.system_to_test.is_armed)

        # Test case #### for triggering alarm
        self.system_to_test.event_queue.put(PIREvent(time=time.time(), event_type=PirEventType.rising))
        sleep(1)
        self.test(expected=True, actual=self.system_to_test.alarm_active)


        # Test case #### for disarming
        self.system_to_test._process_keypress_event("123456")
        sleep(1)
        self.test(expected=False, actual=self.system_to_test.is_armed)

        self.print_results()
        self._logger.debug("Integration testing Complete!")

if __name__ == '__main__':
    sys = SystemIntegrationTesting()
    sys.run()