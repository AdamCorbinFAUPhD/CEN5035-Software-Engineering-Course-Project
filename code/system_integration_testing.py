"""
Module is intended to automatically test the system package with how it integrates with the sub systems. The main idea
would be to simulate keypresses and PIR events to feed into the queues that the system uses to take actions.
"""
from system import System


class SystemIntegrationTesting:
    def __init__(self):
        self.test_case_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.system_to_test = System()

    def run(self):
        self.system_to_test.run()
