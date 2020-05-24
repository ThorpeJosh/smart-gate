""" Module to log battery voltage every hour
"""
import time
import datetime
import logging
import threading
import schedule
import config

# Hide schedule logging messages
logging.getLogger('schedule').setLevel(logging.CRITICAL)

class BatteryVoltageLog():
    """Logs the battery voltage every hour to file
    """
    def __init__(self, path, analog_pin_object):
        # Create voltage logger
        log_format = '%(asctime)s : %(message)s'
        self.bat_logger = logging.getLogger('Battery_voltage')
        self.bat_logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        self.bat_logger.addHandler(file_handler)

        # Setup analog read for battery pin
        self.battery_pin = analog_pin_object

        # Schedule job
        schedule.every(1).minute.at(':00').do(self.scheduled_job)

    def scheduled_job(self):
        """scheduled job
        """
        print('This job is running.')
        print(datetime.datetime.now())
        self.bat_logger.info("Battery voltage: %sv", round(self.battery_pin.voltage() * \
                                config.BATTERY_VOLTAGE_CORRECTION_FACTOR, 1))

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
