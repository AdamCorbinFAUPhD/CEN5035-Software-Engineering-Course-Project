import urllib
from time import time, sleep
from flask import Flask, render_template, request, redirect
import os
import sys_client
import webbrowser


app = Flask(__name__)


@app.route("/")
def status():
    client = sys_client.get_client()
    data = client.get_status()
    armed = None
    led_color = None
    led_enabled = None
    if data:
        armed = data['armed']
        led_color = data['led_color']
        led_enabled = data['led_enabled']
    return render_template("index.html", time=get_time(), armed=armed, led_color=led_color, led_enabled=led_enabled)


def arm_disarm():
    client = sys_client.get_client()
    result = client.arm_disarm()
    # Testing
    current_status = flask.request.args.get('status')
    # I'm not completely sure how to do this -- pseudocode for now
        # if current_status == armed
        # results == armed
        # else
        # results == disarmed
    # Demonstration of the backend, needs to be tested
    return 'Armed' if current_status == 'Disarmed' else 'Disarmed'

def get_time():
    return time()

 @app.route("/GoogleCalendar")
 def calendar():
     # Create a button that will redirect to the Google calendar
     # At the moment, not working -- need to add more
        # url = https://calendar.google.com/calendar/b/5?cid=ZmF1Y2VuNTAzNUBnbWFpbC5jb20
     # return redirect(url, code = 307)
    return webbrowser.open_new_tab('https://calendar.google.com/calendar/b/5?cid=ZmF1Y2VuNTAzNUBnbWFpbC5jb20')


def create_app():
    """
    Called by System to instantiate a new Flask app. This is where app setup should be done.
    """
    # create and configure the app
    app.config.from_mapping(
        SECRET_KEY='testing', )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the system client
    sys_client.init_app(app)
    return app
