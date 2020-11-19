#!/bin/bash -e
# Installs arduino-cli tool only if running on rpi as pi user else it just configures arduino-cli

# Install arduino-cli and move it to /usr/bin
echo "Installing arduino-cli"
curl -L --retry 5 --retry-delay 5 https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sudo BINDIR=/usr/bin sh

# Setup arduino-cli
echo "Setting up arduino-cli"
arduino-cli config init
arduino-cli core update-index
# Install core for Arduino Uno
arduino-cli core install arduino:avr

# Install 3rd party arduino libraries
arduino-cli lib install QuickMedianLib
arduino-cli lib install Servo
