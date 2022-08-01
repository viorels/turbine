#!/usr/bin/python3

import subprocess

# physical pin numbering https://pinout.xyz/#
BUTTON1_PIN = 11
BUTTON2_PIN = 13
BUTTON3_PIN = 15

BUTTON_TIMEOUT = 20

VIDEOS = ['video1_francisc.mp4', 'video2_pelton.mp4', 'video3_kaplan.mp4']

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

last_button = 0
last_time = 0
player = None

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
    global last_button, player
    if button == last_button:
        return
    last_button = button

    if player:
        player.terminate()
        player = None
    player = subprocess.call(['/usr/bin/cvlc', VIDEOS[button-1], 'vlc://quit'])


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BUTTON1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.add_event_detect(BUTTON1_PIN,GPIO.RISING,callback=button1_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON2_PIN,GPIO.RISING,callback=button2_callback, bouncetime=500)
GPIO.add_event_detect(BUTTON3_PIN,GPIO.RISING,callback=button3_callback, bouncetime=500)

message = input("Press enter to quit\n\n") # Run until someone presses enter

GPIO.cleanup() # Clean up
