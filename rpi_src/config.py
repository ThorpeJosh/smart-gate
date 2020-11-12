"""Module to store create or read from a configuration file and parse the values and variables to
globals for other modules to access.
"""
import json
import logging
import os
import configparser
from pathlib import Path

from jsonschema import validate

logger = logging.getLogger("root")


def read_write_config(config_location):
    """Function to read the config file or create one if it doesn't exist"""
    config = configparser.ConfigParser(allow_no_value=True)
    # Write config template to file if it doesn't already exist
    if not os.path.exists(config_location):
        logger.info("No config file was found, creating one at: %s", config_location)
        config["raspberry_pins"] = {
            "# First pin of the motor": None,
            "motor_pin_0": "23",
            "# Second pin of the motor": None,
            "motor_pin_1": "24",
            "# Pin for the button on outside of the gate": None,
            "button_outside": "27",
            "# Pin for the button on inside of the gate": None,
            "button_inside": "22",
            "# Optional pin for debugging or mounted on control box": None,
            "button_debug": "17",
        }

        config["arduino_pins"] = {
            "# Analog pin connected to the current shunt": None,
            "shunt": "0",
            "# Analog pin connected to the 24VDC battery voltage divider": None,
            "battery_voltage": "5",
        }

        config["parameters"] = {
            "# Minimum time to hold the gate open for, pushing a button when the gate is open will "
            "start this countdown again (seconds)": None,
            "hold_open_time": "10",
            "# Expected time for gate to open/close, used to determine if something has gone wrong"
            ", like hitting a car or a fault with the motor (seconds)": None,
            "expected_time_to_open_close": "23",
            "# Voltage threshold across shunt for the gate hitting an object (volts)": None,
            "shunt_threshold": "0.03",
            "# Delay before reading shunt voltage, due to motor startup current spike (seconds)"
            : None,
            "shunt_read_delay": "0.5",
            "# Correction factor for battery voltage input. Gets multiplied to the arduinos "
            "voltage reading on the battery voltage pin": None,
            "battery_voltage_correction_factor": "10.7",
        }

        config["keys"] = {
            "# Secret key to use for 433MHz radio, if being used. Must be 8 characters": None,
            "radio_key": "8CharSec",
        }

        path = os.path.split(config_location)[0]
        os.makedirs(path, exist_ok=True)
        with open(config_location, "w") as config_file:
            config.write(config_file)

    # Read the config file
    logger.debug("Reading config file at: %s", config_location)
    input_config = configparser.ConfigParser()
    input_config.read(config_location)
    return input_config


# Read from config file
CONFIG_PATH = os.path.join(str(Path.home()), ".config/smart-gate/")
CONFIG = read_write_config(os.path.join(CONFIG_PATH, "conf.ini"))

# Board Pin numbers
MOTORPIN0 = CONFIG.getint("raspberry_pins", "motor_pin_0")
MOTORPIN1 = CONFIG.getint("raspberry_pins", "motor_pin_1")

BUTTON_OUTSIDE_PIN = CONFIG.getint("raspberry_pins", "button_outside")
BUTTON_INSIDE_PIN = CONFIG.getint("raspberry_pins", "button_inside")
BUTTON_BOX_PIN = CONFIG.getint("raspberry_pins", "button_debug")

# Arduino analog pins
SHUNT_PIN = CONFIG.getint("arduino_pins", "shunt")
BATTERY_VOLTAGE_PIN = CONFIG.getint("arduino_pins", "battery_voltage")

# Parameters
SHUNT_THRESHOLD = CONFIG.getfloat("parameters", "shunt_threshold")
SHUNT_READ_DELAY = CONFIG.getfloat("parameters", "shunt_read_delay")
EXPECTED_TIME_TO_OPEN_CLOSE = CONFIG.getint("parameters", "expected_time_to_open_close")
MAX_TIME_TO_OPEN_CLOSE = EXPECTED_TIME_TO_OPEN_CLOSE * 1.2
MIN_TIME_TO_OPEN_CLOSE = EXPECTED_TIME_TO_OPEN_CLOSE * 0.8
HOLD_OPEN_TIME = CONFIG.getint("parameters", "hold_open_time")
BATTERY_VOLTAGE_CORRECTION_FACTOR = CONFIG.getfloat(
    "parameters", "battery_voltage_correction_factor"
)

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
SAVED_MODE_FILE = os.path.join(CONFIG_PATH, "saved_mode.txt")

# 8 Character password that 433MHz arduino receiver is looking for, if 433MHz receiver is used
RADIO_KEY = CONFIG.get("keys", "radio_key")

# Load email config json
try:
    EMAIL_KEY_JSON = os.path.join(CONFIG_PATH, "email_keys.json")
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
