"""Smart gate class module
"""
import logging
import time

import gpiozero

from config import Config as config
from serial_analog import AnalogInputs

logger = logging.getLogger("root")


class Gate:
    """Gate instance
    This keeps track of all the gate methods (functions) and the related status/vaiables
    """

    def __init__(self, queue):
        self.current_state = "unknown"
        self.current_mode = self._read_mode()
        self.job_q = queue
        self.setup_pins()
        self.shunt_pin = config.SHUNT_PIN

    @staticmethod
    def _write_mode(mode):
        """Save current mode on mode change
        """
        with open(config.SAVED_MODE_FILE, "w") as saved_mode:
            saved_mode.write(mode)

    @staticmethod
    def _read_mode():
        """Read most recent mode on start up (if mode is invalid load the default mode)
        """
        try:
            with open(config.SAVED_MODE_FILE, "r") as saved_mode:
                mode = saved_mode.read()
                mode = mode.strip().replace("\n", "")
                if mode not in config.MODES:
                    logger.warning("Invalid read_mode value: %s", mode)
                    mode = config.MODES[0]
                    logger.warning("Setting mode to the default: %s", mode)
        except FileNotFoundError:
            mode = config.MODES[0]
            logger.warning("Saved mode file not found")
        return mode

    def mode_change(self, new_mode):
        """allow user to change gates current operating mode
        """
        if new_mode in config.MODES:
            self.current_mode = new_mode
            self._write_mode(new_mode)
            logger.info("Changed gate mode to: %s", self.current_mode)
        else:
            logger.warning("Invalid mode_change attempted: %s", new_mode)

    def _open(self):
        """Open the gate
        """
        self.current_state = "opening"
        logger.debug("opening gate motor")
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
        while True:
            # Check shunt voltage
            shunt_voltage = AnalogInputs.get(self.shunt_pin)
            if shunt_voltage > config.SHUNT_THRESHOLD:
                logger.debug('Shunt threshold exceeded: %s', shunt_voltage)
                self._stop()
                self.current_state = "opened"
                return

            # Check security timer
            if time.monotonic() > security_time:
                logger.critical("Open security timer has elapsed")
                self.current_state = "Open time error"
                self._stop()
                return
            # This will allow for a close request to jump out of opening & skip holding
            job = self.job_q.get_nonblocking()
            if job == "close":
                self._stop()
                self.current_state = "holding"
                return

    def hold(self):
        """Method to control hold the gate open while cars drive through
        When called it should hold the gate open for a set duration
        """
        self.current_state = "holding"
        start_time = time.monotonic()
        while time.monotonic() < start_time + config.HOLD_OPEN_TIME:
            time.sleep(0.25)
            job = self.job_q.get_nonblocking()
            # This will allow a new open request to extend the hold time by reseting it
            if job == "open":
                start_time = time.monotonic()
            # This will allow a close request to skip the rest of the holding time
            if job == "close":
                return

    def _close(self):
        """Close the gate
        """
        self.current_state = "closing"
        logger.debug("closing gate motor")
        self.motor_pin0.on()
        self.motor_pin1.off()

    def close(self):
        """Method to control the gate closing
        When called it should close the gate and handle when the task is complete,
        or an obstruction has been hit
        """
        self.current_state = "closing"
        start_time = time.monotonic()
        security_time = start_time + config.MAX_TIME_TO_OPEN_CLOSE
        hit_time = start_time + config.MIN_TIME_TO_OPEN_CLOSE
        self._close()
        time.sleep(config.SHUNT_READ_DELAY)
        while True:
            # Check shunt voltage
            shunt_voltage = AnalogInputs.get(self.shunt_pin)
            if shunt_voltage > config.SHUNT_THRESHOLD:
                logger.debug('Shunt threshold exceeded: %s', shunt_voltage)
                self._stop()
                # Check if gate hit object or is closed
                if time.monotonic() < hit_time:
                    # It can be assumed that the gate has hit something closing,
                    logger.warning("Gate has hit something whilst closing")
                    logger.debug("Reopening gate due to hit")
                    self.job_q.validate_and_put('open')
                    return
                self.current_state = "closed"
                logger.debug("Gate closed")
                return
            # Check security timer
            if time.monotonic() > security_time:
                logger.critical("Close security timer has elapsed")
                self.current_state = "Close time error"
                self._stop()
                return
            # Allow for open request to jump out of closing
            job = self.job_q.get_nonblocking()
            if job == "open":
                self._stop()
                self.current_state = "stopped"
                self.job_q.validate_and_put('open')
                return

    def _stop(self):
        """Stop the gate
        """
        logger.debug("stopping gate motor")
        self.motor_pin0.off()
        self.motor_pin1.off()

    def setup_pins(self):
        """Setup for gpio pins
        """
        logger.debug("Running pin setup")

        # Initialize output pins
        self.motor_pin0 = gpiozero.OutputDevice(config.MOTORPIN0, active_high=False)
        self.motor_pin1 = gpiozero.OutputDevice(config.MOTORPIN1, active_high=False)
