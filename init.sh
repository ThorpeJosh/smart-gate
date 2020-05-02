#!/bin/bash
# Initialization/deployment script for the smart gate environment

sudo apt-get update && sudo apt install -y \
    python3-dev \
    python3-pip \
    virtual-env

# add user 'sg' if it does not exist
if ! id -u gate &>/dev/null
    then
    useradd -m -s /bin/bash gate
    echo adding user gate
else
    echo user gate already exists
fi

#Install the run script
echo installing run scripts and source code
install -o gate -g gate -m 700 run-smart-gate /home/gate/run-smart-gate
install -o gate -g gate -m 700 -d src /home/gate/src

#Insall crontab to run run-smart-gate every minute
crontab -u gate - <<EOF
* * * * * /home/gate/run-smart-gate
EOF
