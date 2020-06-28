#!/bin/bash

relative_path_to_this_script=`dirname $0`

# Compile, upload and cleanup
arduino-cli compile -v --verify --upload -p /dev/ttyUSB0 -b arduino:avr:uno $relative_path_to_this_script/GateSketch
rm $relative_path_to_this_script/GateSketch/build -r
