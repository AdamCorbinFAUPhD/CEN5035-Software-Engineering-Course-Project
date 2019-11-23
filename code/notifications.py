# Download the helper library from https://www.twilio.com/docs/python/install
import logging
import base64
import requests

from twilio.rest import Client

# The Notifications secret will live on the server and not in the repo
from notifications_secret import corbin_from_number, corbin_account_sid, corbin_test_auth_token


class Notifications:
    def __init__(self):
        self.client = Client(username=corbin_account_sid, password=corbin_test_auth_token)
        self._logger = logging.getLogger('AlarmSystem.notification')
        self._logger.info("Notifications object created")

    def send_alert_message(self):
        # Upload image

        with open("/home/pi/Desktop/3254-20191122051643-snapshot.jpg", "rb") as file:
            url = "https://api.imgbb.com/1/upload"
            key_imgbb = "98372b96b86a467e80e33905a3418ad4"
            payload = {
                "key": key_imgbb,
                "image": base64.b64encode(file.read()),
            }
            res = requests.post(url, payload)
            # TODO - figure out how to get the image uploaded then create the URL
            print(res)
        image_url = "https://thumbs.dreamstime.com/z/tv-test-image-card-rainbow-multi-color-bars-geometric-signals-retro-hardware-s-minimal-pop-art-print-suitable-89603635.jpg"
        self.client.messages.create(
            body="Alert has been detected. View the stream here: http://adamcorbin.com:8081",
            from_=corbin_from_number,
            to='+17275108407',
            media_url="https://i.ibb.co/zGD10Gd/150f303418a4.jpg")

if __name__ == '__main__':
    notif = Notifications()
    notif.send_alert_message()