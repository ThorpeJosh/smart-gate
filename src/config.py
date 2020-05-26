"""Module to store all configurable values and variables.
"""

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
SHUNT_THRESHOLD = 0.05 #Volts. Shunt is 0.01R
SHUNT_READ_DELAY = 0.8
MAX_TIME_TO_OPEN_CLOSE = 25
HOLD_OPEN_TIME = 10

BATTERY_VOLTAGE_CORRECTION_FACTOR = 10.75 # 10k 1k voltage divider
BATTERY_VOLTAGE_LOG = 'battery_voltage.log'

# Commands that the gate needs to be able to handle on the job queue
VALID_COMMANDS = ['open', 'close', 'openp', 'closep', 'resume']

#store gate mode incase of restart
SAVED_MODE_FILE = 'saved_mode.txt'

#valid modes for gate operation (normal mode is default incase case of error when on start up)
VALID_MODE = ['normal', 'lock_closed', 'lock_open']
