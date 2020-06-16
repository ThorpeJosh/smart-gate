""" Module to log battery voltage every hour
"""
import time
import logging
import threading
import schedule
import config

# Hide schedule logging messages
logging.getLogger('schedule').setLevel(logging.CRITICAL)

root_logger = logging.getLogger('root')

class BatteryVoltageLog():
    """Logs the battery voltage every hour to file
    """
    def __init__(self, path, analog_pin_object):
        # Create voltage logger
        log_format = '%(levelname)s %(asctime)s : %(message)s'
        self.bat_logger = logging.getLogger(__name__)
        self.bat_logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        self.bat_logger.addHandler(file_handler)

        # Setup analog read for battery pin
        self.battery_pin = analog_pin_object

        # Schedule job
        schedule.every(1).hour.at(':00').do(self.scheduled_job)

    def scheduled_job(self):
        """scheduled job
        """
        bat_volt = round(self.battery_pin.voltage() * config.BATTERY_VOLTAGE_CORRECTION_FACTOR, 1)
        if 24.5 <= bat_volt <= 29.6:
            self.bat_logger.info("%sv", bat_volt)
        elif 24 < bat_volt < 24.5:
            self.bat_logger.warning("%sv", bat_volt)
            root_logger.warning("Battery voltage: %sv", bat_volt)
        else:
            self.bat_logger.critical("%sv", bat_volt)
            root_logger.critical("Battery voltage: %sv", bat_volt)

    def start(self):
        """Start logging job
        """
        threading.Thread(target=self.schedule_check_loop, daemon=True).start()

    @staticmethod
    def schedule_check_loop():
        """Threaded loop to check schedule
        """
        while 1:
            schedule.run_pending()
            time.sleep(1)
