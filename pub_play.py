#!/usr/bin/env python2
# -*- coding: utf-8 -*-

HOST = "localhost"
PORT = 4223
UID = "EG6" # Change XYZ to the UID of your DMX Bricklet
DMX = True

# Timecodes:
# 00:00 Documentary
# 00:50 Karaoke
# 04:01 Documentary
# 05:11 Karaoke
# 08:21 Documentary
# 18:59 Karaoke
# 22:00 Documentary

# Xicato group is 102

# Video:
# /opt/video/Publicani\ Assembly\ 03.mp4

from time import sleep, time
from datetime import datetime, timedelta
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from os import listdir, system, environ
from os.path import join, splitext
if DMX:
    from tinkerforge.ip_connection import IPConnection
    from tinkerforge.bricklet_dmx import BrickletDMX

scheduler = None
dmx = None
ipcon = None

if environ['VIDEO_FILENAME'] != '':
    VIDEO_FILENAME = environ['VIDEO_FILENAME']
else:
    VIDEO_FILENAME = '/opt/video/Publicani\ Assembly\ 03.mp4'

if environ['AUDIO_VOLUME'] != '':
    AUDIO_VOLUME = environ['AUDIO_VOLUME']
else:
    AUDIO_VOLUME = '0'

if environ['AUDIO_DEVICE'] != '':
    AUDIO_DEVICE = environ['AUDIO_DEVICE']
else:
    AUDIO_DEVICE = 'hdmi' # options: alsa, hdmi

if environ['AUDIO_LAYOUT'] != '':
    AUDIO_LAYOUT = environ['AUDIO_LAYOUT']
else:
    AUDIO_LAYOUT = '2.1' # options: 2.1, 5.1, 7.1

def disco_ball_off():
    print("Disco ball OFF")
    # Write DMX frame with 3 channels
    if DMX:
        for i in range(1000):
            dmx.write_frame([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            # dmx.write_frame([0, 0, 255, 0, 0, 0, 255, 255, 0, 0, 100, 0])
        sleep(1)


def disco_ball_on():
    print("Disco ball ON")
    # Write DMX frame with 3 channels
    if DMX:
        for i in range(1000):
            dmx.write_frame([0, 0, 255, 0, 0, 0, 255, 255, 0, 0, 100, 0])
        sleep(1)


if __name__ == "__main__":

    if DMX:
        ipcon = IPConnection() # Create Tinkerforge IP connection
        dmx = BrickletDMX(UID, ipcon) # Create device object
        ipcon.connect(HOST, PORT) # Connect to brickd
        # Don't use device before ipcon is connected
        # Configure Bricklet as DMX master
        dmx.set_dmx_mode(dmx.DMX_MODE_MASTER)

    # Timecodes:
    # 00:00 Documentary
    # 00:50 Karaoke
    # 04:01 Documentary
    # 05:11 Karaoke
    # 08:21 Documentary
    # 18:59 Karaoke
    # 22:00 Documentary

    disco_ball_off()

    scheduler = BackgroundScheduler()
    t = timedelta(seconds=50)
    scheduler.add_job(disco_ball_on, 'date', run_date=datetime.now()+t)
    t = timedelta(seconds=4*60+1)
    scheduler.add_job(disco_ball_off, 'date', run_date=datetime.now()+t)
    t = timedelta(seconds=5*60+11)
    scheduler.add_job(disco_ball_on, 'date', run_date=datetime.now()+t)
    t = timedelta(seconds=8*60+21)
    scheduler.add_job(disco_ball_off, 'date', run_date=datetime.now()+t)
    t = timedelta(seconds=18*60+59)
    scheduler.add_job(disco_ball_on, 'date', run_date=datetime.now()+t)
    t = timedelta(seconds=22*60+21)
    scheduler.add_job(disco_ball_off, 'date', run_date=datetime.now()+t)

    scheduler.start()

    # TODO: add player
    #sleep(30)
    filename = VIDEO_FILENAME
    print("Playing file:", filename)
    system('omxplayer -r -b -o %s --vol %s --layout %s "%s"' % (AUDIO_DEVICE, str(AUDIO_VOLUME), str(AUDIO_LAYOUT), filename))

    # Shutdown the scheduler
    scheduler.shutdown()

    if DMX:
        # Disconnect the Tinkerforge connection
        ipcon.disconnect()