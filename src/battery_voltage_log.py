import schedule
import time
import datetime
import logging
import threading
import config

class BatteryVoltageLog():
    """Logs the battery voltage every hour to file
    """
    def __init__(self, path, analog_pin_object):
        # Create voltage logger
        LOG_FORMAT = '%(asctime)s : %(message)s'
        logging.basicConfig(filename='battery_voltage.log', level=logging.INFO, format=LOG_FORMAT)
        self.logger = logging.getLogger()

        # Setup analog read for battery pin
        self.battery_pin = analog_pin_object

        # Schedule job
        schedule.every(1).minute.at(':00').do(self.scheduled_job)

    def scheduled_job(self):
        """scheduled job
        """
        print('This job is running.')
        print(datetime.datetime.now())
        self.logger.info("Battery voltage: {}v".format(round(self.battery_pin.voltage() * config.BATTERY_VOLTAGE_CORRECTION_FACTOR, 1)))

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
