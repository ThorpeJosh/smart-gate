"""Module to store all configurable values and variables.
"""
import json
import logging
import os
from pathlib import Path

from jsonschema import validate

logger = logging.getLogger("root")

# Board Pin numbers
MOTORPIN0 = 23
MOTORPIN1 = 24

BUTTON_OUTSIDE_PIN = 27
BUTTON_INSIDE_PIN = 22
BUTTON_BOX_PIN = 17

# Arduino analog pins
SHUNT_PIN = 0
BATTERY_VOLTAGE_PIN = 5

# Parameters (time in seconds unless stated otherwise)
SHUNT_THRESHOLD = 0.04  # Volts. Shunt is 0.01R
SHUNT_READ_DELAY = 0.5
MAX_TIME_TO_OPEN_CLOSE = 30
HOLD_OPEN_TIME = 10

BATTERY_VOLTAGE_CORRECTION_FACTOR = 10.7  # 10k 1k voltage divider

# Commands that the gate needs to be able to handle on the job queue
COMMANDS = ["open", "close"]
# Valid modes for gate operation (First mode is default incase case of error on start up)
MODES = ["normal_home", "normal_away", "lock_closed", "lock_open"]

# Battery Log
BATTERY_VOLTAGE_LOG = os.path.join(str(Path.home()), "battery_voltage.log")

# Gate Log
GATE_LOG = os.path.join(str(Path.home()), "gate.log")

# Named pipe
FIFO_FILE = os.path.join(str(Path.home()), "pipe")

# Store gate mode incase of restart
SAVED_MODE_FILE = os.path.join(str(Path.home()), "saved_mode.txt")

# Load email config json
try:
    EMAIL_KEY_JSON = os.path.join(str(Path.home()), ".email_keys.json")
    with open(EMAIL_KEY_JSON, "r") as json_file:
        json_data = json.load(json_file)
    SMTP = json_data["smtp"]
    PORT = json_data["port"]
    FROMADDR = json_data["fromaddr"]
    TOADDRS = json_data["toaddrs"]
    SUBJECT = json_data["subject"]
    USER_ID = json_data["credentials"]["id"]
    USER_KEY = json_data["credentials"]["key"]

    JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "smtp": {"type": "string"},
            "port": {"type": "number"},
            "fromaddr": {"type": "string"},
            "toaddrs": {"type": "array", "minItems": 1},
            "subject": {"type": "string"},
            "credentials": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "key": {"type": "string"}},
            },
        },
    }
    validate(instance=json_data, schema=JSON_SCHEMA)
except FileNotFoundError:
    logger.warning("No email config json found")
    SMTP = None
    PORT = None
    FROMADDR = None
    TOADDRS = None
    SUBJECT = None
    USER_ID = None
    USER_KEY = None
