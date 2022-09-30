# Raspberry pi powered smart gate
[![Build Status](https://jenkins.thorpe.work/buildStatus/icon?job=smart_gate%2Fmaster&subject=build%20status)](https://jenkins.thorpe.engineering/job/smart_gate/job/master/) 
[![Deployment Status](https://jenkins.thorpe.work/buildStatus/icon?job=smart-gate-deploy&subject=deployment%20status)](https://jenkins.thorpe.work/job/smart-gate-deploy/)  
This repo is for an IOT inspired raspberry pi controller for a motorised gate.  
In this application the gate is driven by a 24V motor with a 24V battery and solar charging system. 
An internet connection is supplied to the Raspberry Pi (RPi) via ethernet, and in the initial application of this project the gate was in a remote location where a pair of long range wifi APs in a wireless bridge mode were used to give internet access to the RPi. 
This Internet connection supports features such as sending email alerts, deploying code updates remotely, and a simple API for remote control and receiving information from anywhere in the world.

Since the RPi has no analog pins, an Arduino UNO is used for all the analog inputs and sends the analog voltages over USB to the RPi upon request.
When an update is deployed the RPi will compile and upload the new arduino code to the Arduino via the USB.

This project was initially designed around a specific application, but could be easily forked and applied to different motorised gate applications or contributions to the project that help generalise it are welcome.

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

## Configuration
All the configurable values and parameters (such as pins used, tunables and secret keys) can be found in:
```bash
~/.config/smart-gate/conf.ini
```
This directory and conf.ini file will be created when the program is launched for the first time. Then change the default values as needed.
A sample of the conf.ini file is as follows:
```ini
[raspberry_pins]
# first pin of the motor
motor_pin_0 = 23
# second pin of the motor
motor_pin_1 = 24
# pin for the button on outside of the gate
button_outside = 27
# pin for the button on inside of the gate
button_inside = 22
# optional pin for debugging or mounted on control box
button_debug = 17

[arduino_pins]
# analog pin connected to the current shunt
shunt = 0
# analog pin connected to the 24vdc battery voltage divider
battery_voltage = 5

[parameters]
# minimum time to hold the gate open for, pushing a button when the gate is open will start this countdown again (seconds)
hold_open_time = 10
# expected time for gate to open/close, used to determine if something has gone wrong like hitting a car or a faulty motor (seconds)
expected_time_to_open_close = 23
# voltage threshold across shunt for the gate hitting an object (volts)
shunt_threshold = 0.03
# delay before reading shunt voltage, due to motor startup current spike (seconds)
shunt_read_delay = 0.5
# correction factor for battery voltage input. gets multiplied to the arduinos voltage reading on the battery voltage pin
battery_voltage_correction_factor = 10.7

[keys]
# secret key to use for 433mhz radio, if being used. must be 8 characters
radio_key = 8CharSec
```

## Email Alerts (Optional)
To enable email alerts, an email config must exist at ~/.config/smart-gate/email_keys.json following the following format:
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
The gate can be opened with cheap 433MHz radios when a receiver is fitted to the Arduino. See the wiring diagram for the how to wire the receiver, and code to program the transmitters can be found in arduino_src/TransmitterSketch/TransmitterSketch.ino

The 8 character secret for the Arduino to listen for, must be set in ~/.conf/smart-gate/conf.ini\
The RPi will automatically send this key to the Arduino when the serial handshake is completed.

## Termux UI (Android)
The gate can be controlled via ssh from any computer or mobile.\
For a simple alias based ui, see shell_ui/aliases, and consider appending this file to your bashrc.  

To install or update a Termux UI for android devices:
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
pip install .[dev]
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
* Completed

### Phase 2
* Capture picture of vehicle when button is pressed
* Remove all busy waiting (Optimize to reduce cpu usage by removing while loops with delays)

### Phase 3
* Number Plate detection
* Vehicle/person detection
