#!/usr/bin/env python

# *****************************************************************************
# Copyright (c) 2014, 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

import sys
import signal
import os

try:
    import wiotp.sdk.device
except ImportError:
    # This part is only required to run the sample from within the samples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import wiotp.sdk"
    import os
    import inspect

    cmd_subfolder = os.path.realpath(
        os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../../src"))
    )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import wiotp.sdk.device


def command_processor(cmd):
    global interval
    print("Command received: %s" % cmd.data)
    if cmd.commandId == "setInterval":
        if "interval" not in cmd.data:
            print("Error - command is missing required information: 'interval'")
        else:
            try:
                interval = int(cmd.data["interval"])
            except ValueError:
                print("Error - interval not an integer: ", cmd.data["interval"])
    elif cmd.commandId == "print":
        if "message" not in cmd.data:
            print("Error - command is missing required information: 'message'")
        else:
            print(cmd.data["message"])


class Watson:
    def __init__(self):
        signal.signal(signal.SIGINT, self.interrupt_handler)
        self.client = None
        try:
            # Setting the env variables
            os.environ['WIOTP_IDENTITY_ORGID'] = "4j9rx2"
            os.environ['WIOTP_IDENTITY_DEVICEID'] = "1"
            os.environ['WIOTP_IDENTITY_TYPEID'] = "RasberryPi"
            os.environ['WIOTP_AUTH_TOKEN'] = "OZn21rHzjzK2Db+NnT"
            options = wiotp.sdk.device.parseEnvVars()

            self.client = wiotp.sdk.device.DeviceClient(options)
            self.client.commandCallback = command_processor
            self.client.connect()
        except Exception as e:
            print(str(e))
            sys.exit(1)

    def interrupt_handler(self, signal, frame):
        self.client.disconnect()
        sys.exit(0)

    def send_movement_rising(self):
        message_data = {"movement_rising": True}
        self.client.publishEvent("MOVEMENT", "json", message_data)

    def send_movement_falling(self):
        message_data = {"movement_rising": False}
        self.client.publishEvent("MOVEMENT", "json", message_data)

    def send_alarm_activated(self):
        message_data = {"alarm_activation": True}
        self.client.publishEvent("ALARM_ACTIVATION", "json", message_data)

    def send_alarm_deactivated(self):
        message_data = {"alarm_activation": False}
        self.client.publishEvent("ALARM_ACTIVATION", "json", message_data)

