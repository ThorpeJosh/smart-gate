# Raspberry pi powered smart gate
[![Build Status](http://jenkins.thorpe.engineering:8080/buildStatus/icon?job=smart_gate%2Fmaster&subject=build%20status)](http://jenkins.thorpe.engineering:8080/job/smart_gate/job/master/) 
[![Deployment Status](http://jenkins.thorpe.engineering:8080/buildStatus/icon?job=smart-gate-deploy&subject=deployment%20status)](http://jenkins.thorpe.engineering:8080/job/smart-gate-deploy/)  
This repo is for a private application of a IOT inspired raspberry pi controller for a household front gate.  
In this application the gate is driven by a 24V motor with a 24V battery with solar charging system. 
An internet connection is supplied by a pair of long range wifi APs in a wireless bridge mode. The Raspberry pi then connects to the AP via ethernet for an internet connection. This Internet connection supports features such as sending email alerts, deploying code updates remotely and a simple API for mode changes and commands to be send remotely.

Since the RPi has no analog pins, an Arduino UNO is used for all the analog inputs and sends the analog voltages over USB to the RPi upon request.
When an update is deployed the RPi will compile and upload the new arduino code as the Arduino is connected via USB to the RPi.

This repo code is designed around this specific application, but could be easily forked and applied to different smart-gate applications.
All the pin numbers and configurable parameters reside in the rpi_src/config.py file to allow easy configuration for different applications.

## RPi Inputs
* 3 push-buttons (Normally Open, Activating button grounds the pin)
  * Outside the property, activated when entering
  * Inside the property, activated when exiting
  * On the control box mounted on the gate post, used for debugging
* Arduino serial via USB
  * Voltage across a shunt to measure current through motor for hit detection
  * Battery voltage for logging and alerts

## RPi outputs
* Gate Motor (2 pins, driving SPDT relays in a H-bridge configuration)

## Arduino Inputs
* Analog input from all pins (RPi decides what pins to use/ignore)

## Modes
Gate has 3 modes it can operate in
  * Normal - Closed unless a button is pushed then it opens for a period of time then closes again.
    If the gate hits an object when opening, it will stop the motor and wait for another button push.
    If the gate hits an object when closing, it will re-open.
  * Away - Same as normal but sends email alert when button is pressed
  * Permanently Open - Gate opens and stays there until mode is changed
  * Permanently Closed - Gate closes and stays there until mode is changed
  
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
* Collision detection on closing (Immediately reopen)
* Bug - Open command from pipe doesn't work when gate is closing
* Bug - Changing from lock_open to normal mode doesn't close the gate
* Bug - Messages on pipe are adding newlines to log

### Phase 2
* Capture picture
* Remove all busy waiting (Optimize to reduce cpu usage by removing while loops with delays)

### Phase 3
* Number Plate detection
* Vehicle/person detection
