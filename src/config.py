"""Module to store all configurable values and variables.
"""

# Board Pin numbers
MOTORPIN0 = 16
MOTORPIN1 = 18

BUTTON_OUTSIDE_PIN = 8
BUTTON_INSIDE_PIN = 10
BUTTON_BOX_PIN = 12

SHUNT_PIN = 0
BATTERY_VOLTAGE_PIN = 3

# Parameters (time in seconds unless stated otherwise)
SHUNT_THRESHOLD = 0.03 #Volts
SHUNT_READ_DELAY = 0.8
MAX_TIME_TO_OPEN_CLOSE = 15
HOLD_OPEN_TIME = 10

BATTERY_VOLTAGE_CORRECTION_FACTOR = 10.75 # 10k 1k voltage divider

# Commands that the gate needs to be able to handle on the job queue
VALID_COMMANDS = ['open', 'close', 'openp', 'closep', 'resume']

#store gate mode incase of restart
SAVED_MODE_FILE = 'saved_mode.txt'

#valid modes for gate operation (normal mode is default incase case of error when on start up)
VALID_MODE = ['normal', 'lock_closed', 'lock_open']
