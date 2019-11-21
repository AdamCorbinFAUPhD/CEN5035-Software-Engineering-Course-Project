import urllib
from time import time, sleep
from flask import Flask, render_template, request, url, redirect
from system import System

system_obj = System()
sleep(10)

app = Flask(__name__)


@app.route("/")
def status():
    armed = system_obj.is_armed
    led_color = system_obj.led.color.name
    led_enabled = system_obj.led.enabled
    return render_template("index.html", time=get_time(), armed=armed, led_color=led_color, led_enabled=led_enabled)


def get_time():
    return time()


@app.route("/GoogleCalendar")
def calendar():
    # Create a button that will redirect to the Google calendar
    # At the moment, not working -- need to add more
    if action == "GoogleCalendar":{
        # Placeholder for what the url is (will be changing)
        url = https://calendar.google.com/calendar/b/5?cid=ZmF1Y2VuNTAzNUBnbWFpbC5jb20
        return redirect(url, code = 307)
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
