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
    current_state = 'unknown'

    def __init__(self):
        self.close()

    def close(self):
        """Close the gate
        """
        self.current_state = 'closing'
        GPIO.output(config.MOTORPIN0, 0)
        GPIO.output(config.MOTORPIN1, 1)

    def open(self):
        """Open the gate
        """
        self.current_state = 'opening'
        GPIO.output(config.MOTORPIN0, 1)
        GPIO.output(config.MOTORPIN1, 0)

    @staticmethod
    def stop():
        """Stop the gate
        """
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
    time.sleep(1)
    print('In main loop')
    print('Job in queue: ', job_q.get_nonblocking())


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
