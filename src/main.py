"""Smart gate module entry point
"""
import os
import time
import logging
try:
    # Only imports on a Raspberry Pi
    import RPi.GPIO as GPIO
except RuntimeError:
    # Import mock interface for non-RPi dev and set the Mock.GPIO log level to debug
    os.environ['LOG_LEVEL'] = 'Debug'
    import Mock.GPIO as GPIO
import config

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
        self.out_button = ''
        self.in_button = ''
        self.box_button = ''
        self.close()

    def close(self):
        """Close the gate
        """
        self.current_state = 'closing'

    def open(self):
        """Open the gate
        """
        self.current_state = 'opening'

    def stop(self):
        """Stop the gate
        """

def setup():
    """Setup to be run once at start of program
    """

def main_loop():
    """Main loop
    Similair to the MainLoop() on an arduino, this will loop through indefinately,
    calling all required inputs and outputs to make the gate function
    """


if __name__ == '__main__':
    logger.info('Starting smart gate')
    while 1:
        main_loop()
