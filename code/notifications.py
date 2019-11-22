# Download the helper library from https://www.twilio.com/docs/python/install
import logging
import base64
import requests

from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'AC10a582ab8d3a246de34218bebd80ccfd'
auth_token = 'd6f5c31e8b7b391295be0b68d4421287'

corbin_from_number = "+14029650199"
corbin_account_sid = 'ACfb37f19d85abaa37627b727da73c776f'
corbin_test_auth_token = "5f4ab212948c4e76471a9f0b47a20863"


class Notifications:
    def __init__(self):
        self.client = Client(username=corbin_account_sid, password=corbin_test_auth_token)
        self._logger = logging.getLogger('AlarmSystem.notification')

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