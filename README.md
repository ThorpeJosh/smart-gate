# Raspberry pi powered smart gate
This repo is for a private application of a IOT inspired raspberry pi controller for a household front gate
The gate has 3 input buttons to operate it, a 24V motor, a 24V battery with solar charging, and wifi for internet connectivity.

## GPIO inputs
* 3 push-buttons (Normally Open, Activating button grounds the pin)
  * Outside the property, activated when entering
  * Inside the property, activated when exiting
  * On the control box mounted on the gate post, used for debugging
* ADS1115 via I2C
  * Voltage across a shunt to measure current through motor for hit detection
  * Battery voltage for logging

## GPIO outputs
* Gate Motor (2 pins, driving SPDT relays in a H-bridge configuration)

## Connectivity
Raspberry pi is fitted with a wifi radio and is connected to a personal VPN for remote access and control

## Modes
Gate has 3 modes it can operate in
  * Normal - Closed unless a button is pushed then it opens for a period of time then closes again.
    If the gate hits an object when opening, it will stop the motor and wait for another button push.
    If the gate hits an object when closing, it will re-open.
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
