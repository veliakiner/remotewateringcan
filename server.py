import json
import os
import threading

import time
from datetime import datetime
from subprocess import check_call

from flask import Flask, render_template, request, send_file
from PIL import Image

import pygame
import requests
import pygame.camera
from database import MoistureReading, init_db, WateringEvent

SAMPLING_FREQ = 60
session = init_db()

if os.environ.get("MOCK_WATER"):
    def read():
        return time.time()
else:
    from sensor import read

slack_key = os.environ.get("SLACK_KEY")

PASSWORD = os.environ.get("FLASK_PASSWORD")

BASE_RELAY_CMD = "sudo usbrelay V5ZEA_1={}"
app = Flask(__name__, static_url_path=os.getcwd())
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.cam = pygame.camera.init()


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


@app.route('/water', methods=['POST'])
def hello_world():
    loaded = json.loads(request.data.decode("utf-8"))

    password = loaded.get("password")
    if password != PASSWORD:
        return "Failed: wrong password"
    duration = loaded.get("duration")
    try:
        duration = int(duration)
    except TypeError:
        return "Failed: invalid"
    duration = max(duration, 0)
    duration = min(duration, 20)
    try:
        initial_reading = read() # assume this blocks
        start_watering()
        time.sleep(duration)
    finally:
        stop_watering()

    def confirm_and_commit(reading_before, delay=SAMPLING_FREQ * 1.5):
        time.sleep(delay)
        reading_after = read()
        # lower reading is wetter, but due to fluctations in the moisture level you the reading might drop slightly
        # without watering so check for a minimum reading drop
        wet = (reading_before - reading_after) > 100
        dry = not wet
        event = WateringEvent(date=datetime.now(), duration=duration, dry=dry)
        session.add(event)
        session.commit()
        fail_message = "Plant was watered but no moisture level increase was detected " \
                       "(before: {}, after: {}). Check that the tank has water.".format(reading_before, reading_after)
        # for debugging purposes
        success_message = "Watered successfully. Readings: (before: {}, after: {})".format(reading_before, reading_after)
        # Warn me about potentially dry tank
        if dry:
            requests.post("https://hooks.slack.com/services/{}".format(slack_key),
                          headers={"Content-type": "application/json"},
                          json={"text": (fail_message)})


    # TODO: use sensor to detect moisture level increase and to figure out if the water tank is empty
    deferred = threading.Thread(target=lambda: confirm_and_commit(initial_reading))
    deferred.start()
    return "Success"


# @app.after_request
# def add_header(r):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     r.headers["Pragma"] = "no-cache"
#     r.headers["Expires"] = "0"
#     r.headers['Cache-Control'] = 'public, max-age=0'
#     return r

RES = (640, 480)


def gen(feed):
    cam = pygame.camera.Camera("/dev/video{}".format(feed), RES)
    cam.start()
    try:
        img = cam.get_image()
        bytes = pygame.image.tostring(img, "RGB")
        img = Image.frombytes("RGB", RES, bytes)
        filename = "feed-{}.png".format(feed)
        with open(filename, "w") as output:
            img.save(output, "JPEG")
        return filename
    finally:
        print("stopped")
        cam.stop()


@app.route('/video_feed_1')
def video_feed_1():
    return _video_feed(0)


@app.route('/video_feed_2')
def video_feed_2():
    return _video_feed(1)


def _video_feed(feed):
    filename = gen(feed)
    return send_file(filename, mimetype='image/jpg')


@app.route("/")
def main():
    latest_reading = (session.query(MoistureReading.reading).order_by(MoistureReading.date.desc()).first() or ["None"])[
        0]
    last_watering = (session.query(WateringEvent.date).order_by(WateringEvent.date.desc()).first() or ["None"])[0]
    return render_template("home.html", reading=latest_reading, last_watering=last_watering)


@app.route("/dump-watering")
def dump_water():
    with open("dump_watering.csv", "w") as f:
        for reading in session.query(WateringEvent).all():
            f.write("{},{},{}\n".format(reading.duration, reading.date.timestamp(), reading.dry))
    return send_file('dump_watering.csv')

import os
@app.route("/dump-moisture")
def dump_moisture():
    with open("dump_moisture.csv", "w") as f:
        for reading in session.query(MoistureReading).all():
            f.write("{},{}\n".format(reading.reading, reading.date.timestamp()))
    return send_file('dump_moisture.csv')


def record_moisture(session):
    session.add(MoistureReading(reading=read(), date=datetime.now()))
    session.commit()


def record_forever(session):
    while True:
        record_moisture(session)
        time.sleep(SAMPLING_FREQ)


if __name__ == "__main__":
    record_forever(session)
