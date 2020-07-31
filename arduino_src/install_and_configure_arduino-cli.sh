#!/bin/bash -e
# Installs arduino-cli tool only if running on rpi as pi user else it just configures arduino-cli

if [ $(whoami) = 'pi' ]
then
    # Install arduino-cli and move it to /usr/bin
    echo "Installing arduino-cli"
    curl -L --retry 5 --retry-delay 5 https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sudo BINDIR=/usr/bin sh
fi


# Setup arduino-cli
echo "Setting up arduino-cli"
arduino-cli config init
arduino-cli core update-index
# Install core for Arduino Uno
arduino-cli core install arduino:avr

# Get RadioHead arduino library
mkdir -p ~/Arduino/libraries/
cd ~/Arduino/libraries/
echo "Getting RadioHead library"
RH_NAME='RadioHead-1.111.zip'
wget http://www.airspayce.com/mikem/arduino/RadioHead/"$RH_NAME"
unzip -oq "$RH_NAME"
rm "$RH_NAME"
