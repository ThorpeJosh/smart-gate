"""Smart gate class module
"""
# Smart gate module imports
import time
import logging
import gpiozero
import config
from adc import AnalogInput


# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logging.basicConfig(filename=config.GATE_LOG, level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()

class Gate():
    """Gate instance
    This keeps track of all the gate methods (functions) and the related status/vaiables
    """
    def __init__(self, queue):
        self.current_state = 'unknown'
        self.current_mode = self._read_mode()
        self.shunt_pin = AnalogInput(config.SHUNT_PIN0, config.SHUNT_PIN1)
        self.motor_pin0 = gpiozero.OutputDevice(config.MOTORPIN0, active_high=False)
        self.motor_pin1 = gpiozero.OutputDevice(config.MOTORPIN1, active_high=False)
        self.job_q = queue

    @staticmethod
    def _write_mode(mode):
        """Save current mode on mode change
        """
        with open(config.SAVED_MODE_FILE, 'w') as saved_mode:
            saved_mode.write(mode)

    @staticmethod
    def _read_mode():
        """Read most recent mode on start up (if mode is invalid load the default mode)
        """
        try:
            with open(config.SAVED_MODE_FILE, 'r') as saved_mode:
                mode = saved_mode.read()
                mode = mode.strip().replace('\n', '')
                if mode not in config.VALID_MODE:
                    mode = config.VALID_MODE[0]
                    logger.warning("Invalid read_mode attempted: %s", mode)
        except FileNotFoundError:
            mode = config.VALID_MODE[0]
            logger.warning('Saved mode file not found')
        return mode

    def mode_change(self, new_mode):
        """allow user to change gates current operating mode
        """
        if new_mode in config.VALID_MODE:
            self.current_mode = new_mode
            self._write_mode(new_mode)
        else:
            logger.warning("Invalid mode_change attempted: %s", new_mode)

    def _open(self):
        """Open the gate
        """
        self.current_state = 'opening'
        logger.debug('opening gate')
        self.motor_pin0.off()
        self.motor_pin1.on()

    def open(self):
        """Method to control the gate opening
        When called it should open the gate and handle when the task is complete,
        or an obstruction has been hit
        """
        start_time = time.monotonic()
        security_time = start_time + config.MAX_TIME_TO_OPEN_CLOSE
        self._open()
        time.sleep(config.SHUNT_READ_DELAY)
        while self.shunt_pin.voltage() < config.SHUNT_THRESHOLD:
            if time.monotonic() > security_time:
                logger.critical('Open security timer has elapsed')
                self.current_state = 'Open time error'
                self._stop()
                return
            #this will allow for a close request to jump out of opening & skip holding
            job = self.job_q.get_nonblocking()
            if job == 'close':
                self.current_state = 'holding'
                return
        self._stop()
        self.current_state = 'opened'
        return

    def hold(self):
        """Method to control hold the gate open while cars drive through
        When called it should hold the gate open for a set duration
        """
        self.current_state = 'holding'
        start_time = time.monotonic()
        while time.monotonic() < start_time + config.HOLD_OPEN_TIME:
            time.sleep(0.25)
            job = self.job_q.get_nonblocking()
            #this will allow a new open request to extend the hold time by reseting it
            if job == 'open':
                start_time = time.monotonic()
            #this will allow a close request to skip the rest of the holding time
            if job == 'close':
                return

    def _close(self):
        """Close the gate
        """
        self.current_state = 'closing'
        logger.debug('closing gate')
        self.motor_pin0.on()
        self.motor_pin1.off()

    def close(self):
        """Method to control the gate closing
        When called it should close the gate and handle when the task is complete,
        or an obstruction has been hit
        """
        self.current_state = 'closing'
        start_time = time.monotonic()
        security_time = start_time + config.MAX_TIME_TO_OPEN_CLOSE
        self._close()
        time.sleep(config.SHUNT_READ_DELAY)
        while self.shunt_pin.voltage() < config.SHUNT_THRESHOLD:
            if time.monotonic() > security_time:
                logger.critical('Close security timer has elapsed')
                self.current_state = 'Close time error'
                self._stop()
                return
            job = self.job_q.get_nonblocking()
            if job == 'open':
                self.current_state = 'opening'
                return
        self._stop()
        self.current_state = 'closed'
        logger.debug('Gate closed')
        return

    def _stop(self):
        """Stop the gate
        """
        logger.debug('stopping gate motor')
        self.motor_pin0.off()
        self.motor_pin1.off()
