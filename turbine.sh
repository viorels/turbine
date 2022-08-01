#!/bin/bash

# minimize terminal window (containing "modulab" in name)
for id in $(xdotool search --name modulab); do xdotool windowminimize $id; done

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$SCRIPT_DIR/turbine.py

