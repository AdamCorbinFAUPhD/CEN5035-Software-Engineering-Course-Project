import urllib
from time import time, sleep
from flask import Flask, render_template, request, redirect, jsonify
import os
import sys_client


app = Flask(__name__)


@app.route("/")
def index():
    client = sys_client.get_client()
    data = client.get_status()
    armed = None
    led_color = None
    led_enabled = None
    is_sensing = None
    if data:
        armed = data['armed']
        led_color = data['led_color']
        led_enabled = data['led_enabled']
        is_sensing = data["is_sensing"]
    return render_template("index.html", armed=armed,
                           led_color=led_color,
                           led_enabled=led_enabled,
                           is_sensing=is_sensing)


@app.route("/status/", methods=['POST'])
def status():
    client = sys_client.get_client()
    data = client.get_status()
    return data


@app.route("/arm_disarm/")
def arm_disarm():
    client = sys_client.get_client()
    result = client.arm_disarm("123456")  # This is hard coded since its coming from the UI
    return 'Armed' if result["result"] == 'true' else 'Disarmed'


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
