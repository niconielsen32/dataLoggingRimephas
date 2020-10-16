#!/bin/bash

echo Starting...

sudo pip3 install pushbullet.py
sudo pip3 install keyboard

git clone https://github.com/niconielsen32/rimephasElectronics.git

cd rimephasElectronics/dataLog

echo Program Running!
echo press "o" for output file
echo press "q" for exit

sudo python3 loggingDispenser.py


