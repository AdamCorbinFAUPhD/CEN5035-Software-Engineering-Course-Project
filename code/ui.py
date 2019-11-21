import urllib
from time import time, sleep
from flask import Flask, render_template, request, url
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
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
