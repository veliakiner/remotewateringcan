from flask import Flask, render_template, request, Response
from subprocess import check_call
import time
import os
import pygame.camera
import pygame
PASSWORD = os.environ.get("FLASK_PASSWORD")

BASE_RELAY_CMD = "sudo usbrelay V5ZEA_1={}"
app = Flask(__name__)

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

RES = (320, 240)
import io
from PIL import Image
def gen(feed):
    cam = pygame.camera.Camera("/dev/video{}".format(feed), RES)
    cam.start()
    try:
        while True:
            img = cam.get_image()
            bytes = pygame.image.tostring(img, "RGB")
            img = Image.frombytes("RGB", RES, bytes)
            output = io.BytesIO()
            img.save(output, "JPEG")
            output.seek(0)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + output.read() + b'\r\n')
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
    return Response(gen(feed),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def main():
    return render_template("home.html")