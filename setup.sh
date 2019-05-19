#!/usr/bin/env bash


sudo apt-get install -y usbrelay
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip -O ng.zip
unzip ng.zip -d ./
./ngrok authtoken 5aoC3eKttoW1LXLDv4YbT_2qbyphConKdYSv4HckbCD
