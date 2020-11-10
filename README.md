# Raspberry pi powered smart gate
[![Build Status](http://jenkins.thorpe.engineering:8080/buildStatus/icon?job=smart_gate%2Fmaster&subject=build%20status)](http://jenkins.thorpe.engineering:8080/job/smart_gate/job/master/) 
[![Deployment Status](http://jenkins.thorpe.engineering:8080/buildStatus/icon?job=smart-gate-deploy&subject=deployment%20status)](http://jenkins.thorpe.engineering:8080/job/smart-gate-deploy/)  
This repo is for an IOT inspired raspberry pi controller for a motorised gate.  
In this application the gate is driven by a 24V motor with a 24V battery and solar charging system. 
An internet connection is supplied to the Raspberry Pi (RPi) via ethernet, and in the initial application of this project the gate was in a remote location where a pair of long range wifi APs in a wireless bridge mode were used to give internet access to the RPi. 
This Internet connection supports features such as sending email alerts, deploying code updates remotely, and a simple API for remote control and receiving information from anywhere in the world.

Since the RPi has no analog pins, an Arduino UNO is used for all the analog inputs and sends the analog voltages over USB to the RPi upon request.
When an update is deployed the RPi will compile and upload the new arduino code to the Arduino via the USB.

This project was initially designed around a specific application, but could be easily forked and applied to different motorised gate applications or contributions to the project that help generalise it are welcome.
All the pin numbers and configurable parameters reside in the rpi_src/config.py file to allow easy configuration for different applications.

## Wiring
![Screenshot](https://github.com/ThorpeJosh/smart-gate/blob/master/reference/smart_gate_schematics.png?raw=true)

### RPi Inputs
* 3 push-buttons (Normally Open, Activating button grounds the pin)
  * Outside the property, activated when entering
  * Inside the property, activated when exiting
  * On the control box mounted on the gate post, used for debugging
* Arduino serial via USB
  * Voltage across a shunt to measure current through motor for hit detection
  * Battery voltage for logging and alerts

### RPi outputs
* Gate Motor (2 pins, driving SPDT relays in a H-bridge configuration)

### Arduino Inputs
* Analog input from all pins (RPi decides what pins to use/ignore)
* ASK 433MHz Receiver for radio operation of the gate (Optional)

## Modes
Gate has 3 modes it can operate in
  * Normal - Closed unless a button is pushed, then it opens for a set period of time then closes again.
    If the gate hits an object when opening, it will stop the motor and wait for another button push.
    If the gate hits an object when closing, it will re-open.
  * Away - Same as normal but sends email alert when button is pressed
  * Permanently Open - Gate opens and stays there until mode is changed
  * Permanently Closed - Gate closes and stays there until mode is changed

## Email Alerts
To enable email alerts, an email config must exist at ~/.email_keys.json following the following format:
```json
{
    "smtp": "gate_smpt_email_server",
    "port": 123,
    "fromaddr": "gate@email.example",
    "toaddrs": ["recipient1@email.example", "recipient1@email.example"],
    "subject": "GATE ALERT",
    "credentials": {
        "id": "gate@email.example",
        "key": "email_credentials"
    }
}
```

## 433MHz Radio Control (Optional)
The gate can be opened with cheap 433MHz radios when a receiver is fitted to the Arduino. See the wiring diagram for the how to wire the receiver, and code to program the transmitters can be found in arduino_src/TransmitterSketch/TransmitterSketch.ino\

The 8 character secret for the Arduino to listen for, must be saved in a file on the RPi at ~/.radio_key\
The RPi will automatically send this key to the Arduino when the serial handshake is completed.

## Termux UI (Android)
The gate can be controlled via ssh from any computer or mobile.\
For a simple alias based ui, see shell_ui/aliases, and consider appending this file to your bashrc.  

To install or update a Termux UI for android devices:\
* Set your smart-gate RPi up with a static ip on a local network or vpn
* Dowload Termux app on your android, Info at [termux.com](https://termux.com/)
* Install open-ssh in Termux and setup ssh-keys with the RPi server
* Then run the following in a Termux shell substituting the ip address of the RPi smart-gate server.
```bash
export ip=192.168.0.5
curl -sS https://raw.githubusercontent.com/ThorpeJosh/smart-gate/master/shell_ui/install_ui_termux.sh | bash
```

## Deploying to a Raspberry Pi
Instructions for a Debian based OS like Raspbian/Raspberry Pi OS.
### Installation
Install python3 and virtualenv
```bash
sudo apt update && sudo apt install -y python3-dev virtualenv
```

Clone this repo in the pi users home directory
```bash
cd /home/pi
git clone https://github.com/ThorpeJosh/smart-gate.git
```

### Deployment
To deploy simply run
```bash
bash smart-gate/deploy.sh
```
This will setup a virtual environment and install all requirements.
It also adds a cronjob to the pi user to run the smart-gate program automatically.

## Working on this repository
Instructions for Debian based OS
### Installation
Install python3 and virtualenv
```bash
sudo apt update && sudo apt install -y python3-dev virtualenv
```

Create a python3 virtual environment
```bash
virtualenv venv -p python3
```

Activate the virtual environment
```bash
source venv/bin/activate
```

Install the python requirements
```bash
pip install -r requirements.txt
```

### Usage
From a raspberry pi run
```bash
python src/main.py
```

### Pylint
To run the lint filter (Also done by Jenkins on any PRs)
```bash
pylnt src/*
```

### Pytest
To run the unit tests (Also done by Jenkins on any PRs)
```bash
pytest
```

## To-do list
### Phase 1
* Bug - Changing from lock_open to normal mode doesn't close the gate

### Phase 2
* Capture picture of vehicle when button is pressed
* Remove all busy waiting (Optimize to reduce cpu usage by removing while loops with delays)

### Phase 3
* Number Plate detection
* Vehicle/person detection
