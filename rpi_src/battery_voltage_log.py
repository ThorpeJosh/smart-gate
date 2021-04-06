""" Module to log battery voltage every hour
"""
import logging
import threading
import time

import schedule

from config import Config as config
from serial_analog import ArduinoInterface

# Hide schedule logging messages
logging.getLogger("schedule").setLevel(logging.CRITICAL)

root_logger = logging.getLogger("root")


class BatteryVoltageLog:
    """Logs the battery voltage every hour to file"""

    def __init__(self, path, analog_pin, db=None):
        # Create voltage logger
        log_format = "%(levelname)s %(asctime)s : %(message)s"
        self.bat_logger = logging.getLogger(__name__)
        self.bat_logger.setLevel(logging.INFO)
        file_handler = logging.handlers.TimedRotatingFileHandler(path, when="W0", backupCount=50)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        self.bat_logger.addHandler(file_handler)

        # Setup analog read for battery pin
        self.battery_pin = analog_pin

        # Schedule job
        schedule.every(1).hour.at(":00").do(self.scheduled_job)

        if db is not None:
            self.database = db

    @staticmethod
    def analog_to_battery_voltage(analog_voltage, decimals=1):
        """Calculates battery voltage from the 0-3.3v analog voltage"""
        return round(analog_voltage * config.BATTERY_VOLTAGE_CORRECTION_FACTOR, decimals)

    def scheduled_job(self):
        """scheduled job"""
        bat_volt = self.analog_to_battery_voltage(
            ArduinoInterface.get_analog_voltages(self.battery_pin)
        )
        self.database.log_voltage(bat_volt)
        if config.BATTERY_LOWER_ALERT <= bat_volt <= config.BATTERY_UPPER_ALERT:
            self.bat_logger.info("%.1fv", bat_volt)
        elif config.BATTERY_LOWER_ALERT-0.5 < bat_volt < config.BATTERY_LOWER_ALERT:
            self.bat_logger.warning("%.1fv", bat_volt)
            root_logger.warning("Battery voltage: %sv", bat_volt)
        else:
            self.bat_logger.critical("%.1fv", bat_volt)
            root_logger.critical("Battery voltage: %sv", bat_volt)

    def start(self):
        """Start logging job"""
        threading.Thread(target=self.schedule_check_loop, daemon=True).start()

    @staticmethod
    def schedule_check_loop():
        """Threaded loop to check schedule"""
        while 1:
            schedule.run_pending()
            time.sleep(1)
