#!/usr/bin/python3

import vlc
import time
import datetime
import os

# physical pin numbering https://pinout.xyz/#
BUTTON1_PIN = 11
BUTTON2_PIN = 13
BUTTON3_PIN = 15

BUTTON_TIMEOUT = 20

VIDEOS = ['video1_francisc.mp4', 'video2_pelton.mp4', 'video3_kaplan.mp4']

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

last_button = 0
last_time = None

script_path = os.path.dirname(os.path.realpath(__file__))

vlc_instance = vlc.Instance()
MEDIAS = [vlc_instance.media_new(os.path.join(script_path, video)) for video in VIDEOS]
player = vlc_instance.media_player_new()
#player.set_fullscreen(True)

def video(media):
    player.set_media(media)
    player.play()

    # wait time
    time.sleep(0.5)

    # getting the duration of the video
    duration = player.get_length()

    # printing the duration of the video
    print("Duration : " + str(duration))


def button1_callback(channel):
    print("Button1 was pushed!")
    action(1)

def button2_callback(channel):
    print("Button2 was pushed!")
    action(2)

def button3_callback(channel):
    print("Button3 was pushed!")
    action(3)

def action(button):
    global last_button, last_time
    if button == last_button:
        return
    print("OPEN VALVE", button)
    if last_button == 0:
        print("START PUMP")
    else:
        print("CLOSE VALVE", last_button)

    last_button = button
    last_time = datetime.datetime.now()

    video(MEDIAS[button-1])


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(BUTTON1_PIN,GPIO.RISING,callback=button1_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON2_PIN,GPIO.RISING,callback=button2_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON3_PIN,GPIO.RISING,callback=button3_callback, bouncetime=500)

while True:
    if last_time is not None:
        duration = datetime.datetime.now() - last_time
        if duration > datetime.timedelta(seconds=BUTTON_TIMEOUT):
            print("STOP EVERYTHING")
            last_button = 0
            last_time = None
    time.sleep(0.5)

GPIO.cleanup() # Clean up
