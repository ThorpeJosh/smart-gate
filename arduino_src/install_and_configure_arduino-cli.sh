#!/bin/bash -e
# Installs arduino-cli tool only if running on rpi as pi user else it just configures arduino-cli

if [ $(whoami) = 'pi' ]
then
    # Install arduino-cli and move it to /usr/bin
    echo "Installing arduino-cli"
    sudo curl -L --retry 5 --retry-delay 5 https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/bin sh
fi


# Setup arduino-cli
echo "Setting up arduino-cli"
arduino-cli config init
arduino-cli core update-index
# Install core for Arduino Uno
arduino-cli core install arduino:avr
