import urllib
from time import time

from flask import Flask, render_template, request

from system import System

# system_obj = System()
app = Flask(__name__)


@app.route("/")
def status():
    return render_template("index.html", time=get_time())


@app.route("/")
def get_time():
    return time()


@app.route("/GoogleCalendar")
def calendar():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=True)
