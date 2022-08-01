#!/bin/bash

# to run on STARTUP, copy turbine.desktop to ~/.config/autostart

# minimize terminal window (filtered by name)
for id in $(xdotool search --name turbine); do xdotool windowminimize $id; done

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$SCRIPT_DIR/turbine.py

