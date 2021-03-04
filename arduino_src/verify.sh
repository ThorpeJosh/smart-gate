#!/bin/bash

relative_path_to_this_script=`dirname $0`

# Compile without producing build files
arduino-cli compile -v -b arduino:avr:uno $relative_path_to_this_script/GateSketch
