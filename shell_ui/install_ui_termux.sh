#!/bin/bash
# Script that installs smart-gate ui for the Termux app on an andriod phone
set -e

if [ "$HOSTNAME" != "localhost" ]
then
    echo "This is not a Termux environment"
    exit 0
fi

if [ -z "$ip" ]
then 
    echo "ip for smart-gate server not set"
    echo "run \"export ip=<server ip>\" first"
    exit 0
fi

cd
echo "Downloading UI aliases"
curl --fail -L --retry 5 --retry-delay 5 https://raw.githubusercontent.com/ThorpeJosh/smart-gate/master/shell_ui/aliases -o aliases
sed -i 's/$ip/'$ip'/g' aliases

BASHRC="../usr/etc/bash.bashrc"
# Check if aliases exist in bashrc
if $(grep -Fxq "$(head -n1 aliases)" $BASHRC) || $(grep -Fxq "$(tail -n1 aliases)" $BASHRC)
then
    echo "Removing old smart-gate UI..."
    sleep 1
    START=$(grep -Fxn "##smart-gate begin" $BASHRC | cut -d: -f1) 
    FINISH=$(grep -Fxn "##smart-gate end" $BASHRC | cut -d: -f1)
    sed -i "${START},${FINISH}d" $BASHRC
fi

echo "Installing script for ip=$ip"
cat aliases >> $BASHRC

echo "Please ensure ssh keys have been setup between termux and the smart-gate server at $ip"
echo "Termux will need restarting to take effect"
echo "...Installation Finished..."
