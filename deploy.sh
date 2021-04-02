#!/bin/bash
# Initialization/deployment script for the smart gate environment
VALID_USER="pi"

cd /home/${VALID_USER}/smart-gate/

# Usually do update first but RPi takes too long and it will have been done manually prior
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    virtualenv

# Install docker and download postgres database
if [ ! $(command -v docker) ]
then
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
    rm get-docker.sh
else
    echo "Skipping docker install, already installed"
fi
sudo docker pull postgres:13

# Setup the virtual environment
if [ -f venv/bin/activate ]
then
    source venv/bin/activate
    pip install --upgrade pip
    pip install .
else
    echo setting up virtual environment
    virtualenv venv -p python3
    source venv/bin/activate
    pip install --upgrade pip
    export READTHEDOCS=True # picamera requirement
    pip install .
fi

# Deploy the db
cd rpi_src
python -c "from db import DB; DB.deploy()"

# Compile and upload arduino code
bash arduino_src/install_and_configure_arduino-cli.sh
bash arduino_src/upload.sh

#Insall crontab to run run-smart-gate every minute
crontab -u $VALID_USER - <<EOF
* * * * * /bin/bash /home/${VALID_USER}/smart-gate/run-smart-gate
EOF
