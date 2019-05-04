from flask import Flask
from subprocess import check_call
import time

BASE_RELAY_CMD = "sudo usbrelay V5ZEA_2={}"
app = Flask(__name__)

@app.route('/water')
def hello_world():
    try:
        check_call(BASE_RELAY_CMD.format(1).split(" "))
        time.sleep(5)
    finally:
        check_call(BASE_RELAY_CMD.format(0).split(" "))
    return "Success"
