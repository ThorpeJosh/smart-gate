"""Smart gate module entry point
"""
import os
import time
import logging
from pathlib import Path
try:
    # Only imports on a Raspberry Pi
    import RPi.GPIO as GPIO
except RuntimeError:
    # Import mock interface for non-RPi dev and set the Mock.GPIO log level to debug
    os.environ['LOG_LEVEL'] = 'Debug'
    import Mock.GPIO as GPIO

# Smart gate module imports
import config
from job_queue import JobQueue

# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logging.basicConfig(filename='gate.log', level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()

# Log to stdout as well
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)


class Gate():
    """Gate instance
    This keeps track of all the gate methods (functions) and the related status/vaiables
    """
    def __init__(self):
        self.current_state = 'unknown'
        self.current_mode = self._read_mode()

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
        GPIO.output(config.MOTORPIN0, 1)
        GPIO.output(config.MOTORPIN1, 0)

    def open(self):
        """Method to control the gate opening
        When called it should open the gate and handle when the task is complete,
        or an obstruction has been hit
        """
        self._open()
        time.sleep(config.SHUNT_READ_DELAY)

        time.sleep(4)
        self.stop()

    def _close(self):
        """Close the gate
        """
        self.current_state = 'closing'
        logger.debug('closing gate')
        GPIO.output(config.MOTORPIN0, 0)
        GPIO.output(config.MOTORPIN1, 1)


    def close(self):
        """Method to control the gate closing
        When called it should open the gate and handle when the task is complete,
        or an obstruction has been hit
        """
        self._close()
        time.sleep(config.SHUNT_READ_DELAY)

        time.sleep(4)
        self.stop()

    @staticmethod
    def stop():
        """Stop the gate
        """
        logger.debug('stopping gate motor')
        GPIO.output(config.MOTORPIN0, 1)
        GPIO.output(config.MOTORPIN1, 1)

    @staticmethod
    def button_callback(pin):
        """Callback for when a button is pushed
        """
        if pin == config.BUTTON_OUTSIDE_PIN:
            logger.info('Outside button pressed')
        elif pin == config.BUTTON_INSIDE_PIN:
            logger.info('Inside button pressed')
        elif pin == config.BUTTON_BOX_PIN:
            logger.info('Box button pressed')
        else:
            logger.warning('Unknown button pressed')

        job_q.validate_and_put('open')


def setup():
    """Setup to be run once at start of program
    """
    logger.debug('Running setup()')

    # Initialize all digital pins
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config.BUTTON_OUTSIDE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.BUTTON_INSIDE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.BUTTON_BOX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(config.MOTORPIN0, GPIO.OUT, initial=1)
    GPIO.setup(config.MOTORPIN1, GPIO.OUT, initial=1)

    # Button callbacks
    GPIO.add_event_detect(config.BUTTON_OUTSIDE_PIN, GPIO.FALLING, callback=gate.button_callback,
                          bouncetime=1000)
    GPIO.add_event_detect(config.BUTTON_INSIDE_PIN, GPIO.FALLING, callback=gate.button_callback,
                          bouncetime=1000)
    GPIO.add_event_detect(config.BUTTON_BOX_PIN, GPIO.FALLING, callback=gate.button_callback,
                          bouncetime=1000)

def main_loop():
    """Main loop
    Similair to the MainLoop() on an arduino, this will loop through indefinately,
    calling all required inputs and outputs to make the gate function
    """
    print('In main loop')
    job = job_q.get()
    print('Job in queue: ', job)
    if job == 'open':
        gate.open()
        time.sleep(4)
        gate.close()


if __name__ == '__main__':
    logger.info('Starting smart gate')
    gate = Gate()
    job_q = JobQueue(config.VALID_COMMANDS, os.path.join(Path.home(), 'pipe'))
    setup()
    try:
        while 1:
            main_loop()
    finally:
        GPIO.cleanup()
        job_q.cleanup()
