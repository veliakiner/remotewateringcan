from flask import Flask, render_template, request, make_response, Response
from subprocess import check_call
import time
import os
import pygame.camera
import pygame


BASE_RELAY_CMD = "sudo usbrelay V5ZEA_2={}"
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


@app.route('/water', methods=['POST'])
def hello_world():
    print(request.data)
    try:
        start_watering()
        time.sleep(5)
    finally:
        stop_watering()
    return "Success"

RES = (320, 240)
import io
from PIL import Image
def gen():
    cam = pygame.camera.Camera("/dev/video0", RES)
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


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/")
def main():
    return render_template("home.html")