"""Module to store create or read from a configuration file and parse the values and variables to
globals for other modules to access.
"""
import json
import logging
import logging.handlers
import os
from queue import Queue
import configparser
from pathlib import Path

from jsonschema import validate


class Config:
    """ Config class, manages the logging and initialization of all the necesarry globals.
    Every module in smart-gate imports this config object
    """
    @classmethod
    def init_conf(cls):
        """ This is the entry point for the class and running this will setup the smart-gate
        config and make all the necesarry globals available
        """
        # Init log paths
        cls.path_globals()

        # Create and initialize root logger (including email conf)
        cls.root_logger()

        # Setup smart-gate globals (includes handling conf.ini)
        cls.gate_globals()

    @classmethod
    def path_globals(cls):
        """ Defines the paths to where log and conf files are located """
        # Conf path
        cls.CONFIG_PATH = os.path.join(str(Path.home()), ".config/smart-gate/")

        # Email config json path
        cls.EMAIL_KEY_JSON = os.path.join(cls.CONFIG_PATH, "email_keys.json")

        # Battery Log path
        cls.BATTERY_VOLTAGE_LOG = os.path.join(str(Path.home()), "battery_voltage.log")

        # Gate Log path
        cls.GATE_LOG = os.path.join(str(Path.home()), "gate.log")

        # Arduino Log path
        cls.ARDUINO_LOG = os.path.join(str(Path.home()), "arduino.log")

        # Named pipe
        cls.FIFO_FILE = os.path.join(str(Path.home()), "pipe")

        # Store gate mode incase of restart
        cls.SAVED_MODE_FILE = os.path.join(cls.CONFIG_PATH, "saved_mode.txt")

    @classmethod
    def gate_globals(cls):
        """ Sets all the smart-gate globals such as pin values, and parameters """
        # Read from config file
        config = cls.read_write_config(os.path.join(cls.CONFIG_PATH, "conf.ini"))

        # Board Pin numbers
        cls.MOTORPIN0 = config.getint("raspberry_pins", "motor_pin_0")
        cls.MOTORPIN1 = config.getint("raspberry_pins", "motor_pin_1")

        cls.BUTTON_OUTSIDE_PIN = config.getint("arduino_pins", "button_outside")
        cls.BUTTON_INSIDE_PIN = config.getint("arduino_pins", "button_inside")
        cls.BUTTON_BOX_PIN = config.getint("arduino_pins", "button_debug")

        # Arduino analog pins
        cls.SHUNT_PIN = config.getint("arduino_pins", "shunt")
        cls.BATTERY_VOLTAGE_PIN = config.getint("arduino_pins", "battery_voltage")

        # Parameters
        cls.SHUNT_THRESHOLD = config.getfloat("parameters", "shunt_threshold")
        cls.SHUNT_READ_DELAY = config.getfloat("parameters", "shunt_read_delay")
        cls.EXPECTED_TIME_TO_OPEN_CLOSE = config.getint("parameters", "expected_time_to_open_close")
        cls.MAX_TIME_TO_OPEN_CLOSE = cls.EXPECTED_TIME_TO_OPEN_CLOSE * 1.2
        cls.MIN_TIME_TO_OPEN_CLOSE = cls.EXPECTED_TIME_TO_OPEN_CLOSE * 0.8
        cls.HOLD_OPEN_TIME = config.getint("parameters", "hold_open_time")
        cls.BATTERY_VOLTAGE_CORRECTION_FACTOR = config.getfloat(
            "parameters", "battery_voltage_correction_factor"
        )

        # Commands that the gate needs to be able to handle on the job queue
        cls.COMMANDS = ["open", "close"]

        # Valid modes for gate operation (First mode is default incase case of error on start up)
        cls.MODES = ["normal_home", "normal_away", "lock_closed", "lock_open"]

        # 8 Character password that the arduino 433MHz is looking for, if 433MHz receiver is used
        cls.RADIO_KEY = config.get("keys", "radio_key")

    @classmethod
    def root_logger(cls):
        """ Creates the root logger that every other module will use.
        The root logger is threaded, and has a stdout, file and email handler.
        """
        # Create root logger
        log_format = "%(levelname)s %(asctime)s : %(message)s"
        cls.logger = logging.getLogger("root")
        cls.logger.setLevel(logging.DEBUG)

        # Log to file, rotate logs every Monday
        file_handler = logging.handlers.TimedRotatingFileHandler(
            cls.GATE_LOG, when="W0", backupCount=50
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))

        # Log to stdout as well
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(log_format))
        stream_handler.setLevel(logging.DEBUG)

        # Log to email
        cls.email_conf()
        email_handler = logging.handlers.SMTPHandler(
            mailhost=(cls.SMTP, cls.PORT),
            fromaddr=cls.FROMADDR,
            toaddrs=cls.TOADDRS,
            subject=cls.SUBJECT,
            credentials=(cls.USER_ID, cls.USER_KEY),
            secure=(),
        )
        email_handler.setFormatter(logging.Formatter(log_format))
        email_handler.setLevel(logging.WARNING)

        # Log everything to a Queue to avoid each handler from blocking (especially email handler)
        log_q = Queue()
        queue_handler = logging.handlers.QueueHandler(log_q)
        cls.logger.addHandler(queue_handler)

        # Listen for log messages on log_q and forward them to the file, stream and email handlers
        cls.log_listener = logging.handlers.QueueListener(
            log_q, file_handler, stream_handler, email_handler, respect_handler_level=True
        )
        cls.log_listener.start()
        if cls.SMTP is None:
            cls.logger.warning("No email config json found")

    @classmethod
    def email_conf(cls):
        """ Loads the email config from file for the email logging handler """
        # Load email config json
        try:
            with open(cls.EMAIL_KEY_JSON, "r") as json_file:
                json_data = json.load(json_file)
            cls.SMTP = json_data["smtp"]
            cls.PORT = json_data["port"]
            cls.FROMADDR = json_data["fromaddr"]
            cls.TOADDRS = json_data["toaddrs"]
            cls.SUBJECT = json_data["subject"]
            cls.USER_ID = json_data["credentials"]["id"]
            cls.USER_KEY = json_data["credentials"]["key"]

            json_schema = {
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
            validate(instance=json_data, schema=json_schema)
        except FileNotFoundError:
            cls.SMTP = None
            cls.PORT = None
            cls.FROMADDR = None
            cls.TOADDRS = None
            cls.SUBJECT = None
            cls.USER_ID = None
            cls.USER_KEY = None

    @classmethod
    def read_write_config(cls, config_location):
        """ Function to read the config file or create one if it doesn't exist """
        config = configparser.ConfigParser(allow_no_value=True)
        # Write config template to file if it doesn't already exist
        if not os.path.exists(config_location):
            cls.logger.info("No config file was found, creating one at: %s", config_location)
            config["raspberry_pins"] = {
                "# First pin of the motor": None,
                "motor_pin_0": "23",
                "# Second pin of the motor": None,
                "motor_pin_1": "24",
            }

            config["arduino_pins"] = {
                "# Analog pin connected to the current shunt": None,
                "shunt": "0",
                "# Analog pin connected to the 24VDC battery voltage divider": None,
                "battery_voltage": "5",
                "# Pin for the button on outside of the gate": None,
                "button_outside": "7",
                "# Pin for the button on inside of the gate": None,
                "button_inside": "4",
                "# Optional pin for debugging or mounted on control box": None,
                "button_debug": "2",
            }

            config["parameters"] = {
                "# Minimum time to hold the gate open for, pushing a button when the gate is open "
                "will start this countdown again (seconds)": None,
                "hold_open_time": "10",
                "# Expected time for gate to open/close, used to determine if something has gone "
                "wrong, like hitting a car or a fault with the motor (seconds)": None,
                "expected_time_to_open_close": "23",
                "# Voltage threshold across shunt for the gate hitting an object (volts)": None,
                "shunt_threshold": "0.004",
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
        cls.logger.debug("Reading config file at: %s", config_location)
        input_config = configparser.ConfigParser()
        input_config.read(config_location)
        return input_config


# Initialize the config class when this module is imported
Config.init_conf()
