#!/usr/bin/env python

"""
# Watson services
The IBM Watson service has a ton of different things from processing speech to text, text to speech, searching things
online, and many more. While investigating how Watson could be integrated with the Smart Security system it was found
that Watson could create time series graphs of events. This complemented the Smart Security system well since we have
many different events such as movement detection, arming the system, and when the alarm is sounded.
TODO - insert pictures
Alarm activation: https://puu.sh/EFxGh/d23fd15fe5.png
Movement Detection: https://puu.sh/EFxHo/fe27cc55c7.png
System Armed: https://puu.sh/EFxHE/d7ab793216.png

## Challenges
Ideally it would be nice to embed these graphs in our user interface but it doesnt look like Watson has the capability
to share these graphs publicly. The only way you can view them is to be on an authorized email list and you have to
login to IBM's Watson system.

## Considerations
For the Smart Security system we considered using voice activation to arm and disarm the system but in the end it seemed
like a security risk in the event that it didnt function properly or if an unauthorized user found out about the verbal
pass code. Possibly in the future when Watson can self identify someone based on their void then this could be a great
feature to add to this Smart Security System

weblink: https://4j9rx2.internetofthings.ibmcloud.com/dashboard/boards/ec987cb4-3d6b-4aa1-bb63-9eeca3412eb6
"""

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

    def send_armed(self):
        message_data = {"ARMED": True}
        self.client.publishEvent("ARMED", "json", message_data)

    def send_diarmed(self):
        message_data = {"ARMED": False}
        self.client.publishEvent("ARMED", "json", message_data)

