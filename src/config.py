"""Module to store all configurable values and variables.
"""
import os
from pathlib import Path

# Board Pin numbers
MOTORPIN0 = 23
MOTORPIN1 = 24

BUTTON_OUTSIDE_PIN = 27
BUTTON_INSIDE_PIN = 22
BUTTON_BOX_PIN = 17

SHUNT_PIN0 = 0
SHUNT_PIN1 = 1
BATTERY_VOLTAGE_PIN = 3

# Parameters (time in seconds unless stated otherwise)
SHUNT_THRESHOLD = 0.04 #Volts. Shunt is 0.01R
SHUNT_READ_DELAY = 0.5
MAX_TIME_TO_OPEN_CLOSE = 25
HOLD_OPEN_TIME = 10

BATTERY_VOLTAGE_CORRECTION_FACTOR = 10.8 # 10k 1k voltage divider

# Commands that the gate needs to be able to handle on the job queue
VALID_COMMANDS = ['open', 'close', 'openp', 'closep', 'resume']

# Valid modes for gate operation (normal mode is default incase case of error when on start up)
VALID_MODE = ['normal', 'lock_closed', 'lock_open']

# Battery Log
BATTERY_VOLTAGE_LOG = os.path.join(str(Path.home()), 'battery_voltage.log')

# Gate Log
GATE_LOG = os.path.join(str(Path.home()), 'gate.log')

# Named pipe
FIFO_FILE = os.path.join(str(Path.home()), 'pipe')

# Store gate mode incase of restart
SAVED_MODE_FILE = os.path.join(str(Path.home()), 'saved_mode.txt')
