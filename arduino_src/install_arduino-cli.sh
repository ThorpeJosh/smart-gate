#!/bin/bash

# Install arduino-cli and move it to /usr/bin
echo "Installing arduino-cli"
curl -L --retry 5 --retry-delay 5 https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
apt-get install sudo
sudo mv bin/arduino-cli /usr/bin/

# Setup arduino-cli
echo "Setting up arduino-cli"
arduino-cli config init
arduino-cli core update-index
# Install core for Arduino Uno
arduino-cli core install arduino:avr
