from flask import Flask, render_template
from subprocess import check_call
import time
import os
BASE_RELAY_CMD = "sudo usbrelay V5ZEA_2={}"
app = Flask(__name__)


def start_watering():
    if os.environ.get("MOCK_WATER"):
        print("No hardware interface")
        return
    return check_call(BASE_RELAY_CMD.format(1).split(" "))


def stop_watering():
    if os.environ.get("MOCK_WATER"):
        print("No hardware interface")
        return
    return check_call(BASE_RELAY_CMD.format(0).split(" "))


@app.route('/water')
def hello_world():
    try:
        start_watering()
        time.sleep(5)
    finally:
        stop_watering()
    return "Success"


@app.route("/")
def main():
    return render_template("home.html")