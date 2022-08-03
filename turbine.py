#!/usr/bin/python3

# GPIO pin numbering https://pinout.xyz/#
BUTTON1_PIN = 17
BUTTON2_PIN = 27
BUTTON3_PIN = 22

PUMP_PIN = 6
VALVE1_PIN = 2
VALVE2_PIN = 3
VALVE3_PIN = 4

BUTTON_TIMEOUT = 20

VIDEOS = ['video1_francisc.mp4', 'video2_pelton.mp4', 'video3_kaplan.mp4']

########################################

import vlc
import time
import datetime
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use Broadcom pin numbering

GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(VALVE1_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(VALVE2_PIN, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(VALVE3_PIN, GPIO.OUT, initial=GPIO.HIGH)

GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_button = 0
last_time = None

script_path = os.path.dirname(os.path.realpath(__file__))

vlc_instance = vlc.Instance()
MEDIAS = [vlc_instance.media_new(os.path.join(script_path, video)) for video in VIDEOS]
player = vlc_instance.media_player_new()
#player.set_fullscreen(True)

def set_pump(active):
    GPIO.output(PUMP_PIN, not active)   # relay has reversed logic

def set_valve(number, active):
    assert number in (1, 2, 3)
    valve_pins = (VALVE1_PIN, VALVE2_PIN, VALVE3_PIN)
    GPIO.output(valve_pins[number-1], not active)   # relay has reversed logic

def activate_valve(new, old):
    # TODO: hardware button to disable pump and valves
    print("OPEN VALVE", new)
    set_valve(new, True)
    if not old:
        print("START PUMP")
        set_pump(True)
    else:
        time.sleep(0.5)
        print("CLOSE VALVE", last_button)
        set_valve(last_button, False)

def deactivate_all():
    print("STOP EVERYTHING")
    set_pump(False)
    time.sleep(1)
    for valve in (1, 2, 3):
        set_valve(valve, False)

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
    activate_valve(button, last_button)

    last_button = button
    last_time = datetime.datetime.now()

    video(MEDIAS[button-1])

GPIO.add_event_detect(BUTTON1_PIN,GPIO.RISING,callback=button1_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON2_PIN,GPIO.RISING,callback=button2_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON3_PIN,GPIO.RISING,callback=button3_callback, bouncetime=500)

deactivate_all()

while True:
    if last_time is not None:
        duration = datetime.datetime.now() - last_time
        if duration.total_seconds() > BUTTON_TIMEOUT:
            deactivate_all()
            last_button = 0
            last_time = None
    time.sleep(0.5)

GPIO.cleanup() # Clean up
