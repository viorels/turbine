#!/usr/bin/python3

# GPIO pin numbering https://pinout.xyz/#
BUTTON1_PIN = 17
BUTTON2_PIN = 27
BUTTON3_PIN = 22

PUMP_PIN = 6
VALVE1_PIN = 4  # was 4
VALVE2_PIN = 3  # was 2
VALVE3_PIN = 2  # was 3

BUTTON_TIMEOUT = 20
IDLE_TIMEOUT = 60

VIDEOS = ['video1_francisc.mp4', 'video2_pelton.mp4', 'video3_kaplan.mp4']
VIDEO_IDLE = 'video_idle.mp4'

########################################

import vlc
import time
from datetime import datetime
import os

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use Broadcom pin numbering

BUTTONS = (BUTTON1_PIN, BUTTON2_PIN, BUTTON3_PIN)

GPIO.setup([PUMP_PIN, VALVE1_PIN, VALVE2_PIN, VALVE3_PIN], GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

last_button = 0
last_time = None
idle_mode = False
idle_since = datetime.now()

script_path = os.path.dirname(os.path.realpath(__file__))

vlc_instance = vlc.Instance()
MEDIAS = [vlc_instance.media_new(os.path.join(script_path, video)) for video in VIDEOS]
MEDIA_IDLE = vlc_instance.media_new(os.path.join(script_path, VIDEO_IDLE))
player = vlc_instance.media_player_new()
player.set_fullscreen(True)

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
    time.sleep(0.5)
    if not old:
        print("START PUMP")
        set_pump(True)
    else:
        print("CLOSE VALVE", last_button)
        set_valve(last_button, False)

def deactivate_all():
    print("STOP EVERYTHING")
    set_pump(False)
    time.sleep(1)
    for valve in (1, 2, 3):
        set_valve(valve, False)

def video(media, loop=False):
    player.set_media(media)
    if loop:
        vlc_instance.vlm_set_loop("video_idle", True)
    player.play()

    # wait time
    time.sleep(0.5)

    # getting the duration of the video
    duration = player.get_length()

    # printing the duration of the video
    print("Duration : " + str(duration))


def action(button):
    global last_button, last_time, idle_mode, idle_since

    if button == last_button:
        return

    print(f"*** Button [{button}] was pushed!")
    video(MEDIAS[button-1])
    activate_valve(button, last_button)

    last_button = button
    last_time = datetime.now()
    idle_mode = False
    idle_since = datetime.now()

def button_callback(channel):
    button = BUTTONS.index(channel) + 1
    action(button)

#for button in BUTTONS:
#    GPIO.add_event_detect(button, GPIO.RISING, callback=button_callback, bouncetime=500)

deactivate_all()

try:
    while True:
        pushed = [i+1 for i, but_io in enumerate(BUTTONS) if GPIO.input(but_io)]
        #print(pushed)
        if (len(pushed) == 1):
            action(pushed[0])

        if last_time is not None:
            duration = datetime.now() - last_time
            if duration.total_seconds() > BUTTON_TIMEOUT:
                deactivate_all()
                last_button = 0
                last_time = None

        time.sleep(0.05)

        idle_duration = datetime.now() - idle_since
        if idle_duration.total_seconds() > IDLE_TIMEOUT:
            video(MEDIA_IDLE, loop=True)
            idle_mode = True
            idle_since = datetime.now()

except KeyboardInterrupt:
    deactivate_all()
    GPIO.cleanup() # Clean up

