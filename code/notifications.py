# Download the helper library from https://www.twilio.com/docs/python/install
from datetime import datetime
import logging
import base64

import requests

from twilio.rest import Client

# The Notifications secret will live on the server and not in the repo
from notifications_secret import corbin_from_number, corbin_account_sid, corbin_test_auth_token, key_imgbb


class Notifications:
    def __init__(self):
        self.client = Client(username=corbin_account_sid, password=corbin_test_auth_token)
        self._logger = logging.getLogger('AlarmSystem.notification')
        self._logger.info("Notifications object created")

    def send_alert_message(self, screen_shot_file):
        # Upload image
        with open(screen_shot_file, "rb") as file:
            url = "https://api.imgbb.com/1/upload"

            payload = {
                "key": key_imgbb,
                "image": base64.b64encode(file.read()),
            }
            res = requests.post(url, payload)

            # get the url linked to the updloaded picture
            image_url = res.json()["data"]["url"]

        now = datetime.now()
        now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        res = self.client.messages.create(
            body="Alert has been detected @" + now_date_time + ". View the stream here: http://adamcorbin.com:8081",
            from_=corbin_from_number,
            to='+17275108407',
            media_url=image_url)
        self._logger.debug("MMS message sent " + str(res))

    def send_armed_message(self):
        now = datetime.now()
        now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.client.messages.create(
            body="Alarm has been armed @" + now_date_time + ".",
            from_=corbin_from_number,
            to='+17275108407'
        )

    def send_locked_message(self):
        now = datetime.now()
        now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.client.messages.create(
            body="Your system has been locked due to too many failed login attempts @" + now_date_time + ".",
            from_=corbin_from_number,
            to='+17275108407'
        )

    def send_disarmed_message(self):
        now = datetime.now()
        now_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.client.messages.create(
            body="Alarm has been disarmed @" + now_date_time + ".",
            from_=corbin_from_number,
            to='+17275108407'
        )


if __name__ == '__main__':
    notif = Notifications()
    notif.send_alert_message("/home/pi/Desktop/3254-20191122051643-snapshot.jpg")