#!/usr/bin/env bash


sudo apt-get install -y usbrelay
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux64-amd64.zip -O ng.zip
unzip ng.zip -d ./
./ngrok authtoken 5aoC3eKttoW1LXLDv4YbT_2qbyphConKdYSv4HckbCD
