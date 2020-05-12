#!/bin/bash
# Initialization/deployment script for the smart gate environment
VALID_USER="pi"

sudo apt-get update && sudo apt install -y \
    python3-dev \
    python3-pip \
    virtual-env

# Setup the virtual environment
if [ -f venv/bin/activate ]
then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo setting up virtual environment
    virtualenv venv -p python3
    source venv/bin/activate
    pip install -r requirements.txt
fi

#Insall crontab to run run-smart-gate every minute
crontab -u $VALID_USER - <<EOF
* * * * * /home/${VALID_USER}/smart_gate/run-smart-gate
EOF
