#!/usr/bin/env bash


FLASK_PASSWORD=DontOverwaterSagoPalms FLASK_DEBUG=1 FLASK_APP=server.py flask run --host=0.0.0.0 > /dev/null 2>&1 &
python3 server.py &