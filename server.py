from flask import Flask, render_template, request, Response, send_file
from subprocess import check_call
import os
if os.environ.get("MOCK_WATER"):
    def read():
        return "null: no sensor interface"
else:
    from sensor import read

import pygame.camera
import pygame
PASSWORD = os.environ.get("FLASK_PASSWORD")

BASE_RELAY_CMD = "sudo usbrelay V5ZEA_1={}"
app = Flask(__name__)
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

import json

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
        start_watering()
        time.sleep(duration)
    finally:
        stop_watering()
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
import io
from PIL import Image
import time
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


import subprocess
@app.route("/")
def main():
    return render_template("home.html", reading=(read()))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
