"""Smart gate module entry point
"""
import os
import logging
import statistics
try:
    # Only imports on a Raspberry Pi
    import RPi.GPIO as GPIO
except RuntimeError:
    # Import mock interface for non-RPi dev and set the Mock.GPIO log level to debug
    os.environ['LOG_LEVEL'] = 'Debug'
    import Mock.GPIO as GPIO

# Smart gate module imports
import config
import gate
from adc import AnalogInput
from battery_voltage_log import BatteryVoltageLog
from job_queue import JobQueue

# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Log to file
handler = logging.FileHandler(config.GATE_LOG)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(handler)

# Log to stdout as well
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)

def button_callback(pin):
    """Callback for when a button is pushed
    """
    readings = []
    for _ in range(100):
        readings.append(GPIO.input(pin))

    # Double check trigger was real button push and not an anomoly
    if round(statistics.mean(readings)):
        return

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
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.BUTTON_OUTSIDE_PIN, GPIO.IN)
    GPIO.setup(config.BUTTON_INSIDE_PIN, GPIO.IN)
    GPIO.setup(config.BUTTON_BOX_PIN, GPIO.IN)

    GPIO.setup(config.MOTORPIN0, GPIO.OUT, initial=1)
    GPIO.setup(config.MOTORPIN1, GPIO.OUT, initial=1)

    # Button callbacks
    GPIO.add_event_detect(config.BUTTON_OUTSIDE_PIN, GPIO.FALLING, callback=button_callback,
                          bouncetime=1000)
    GPIO.add_event_detect(config.BUTTON_INSIDE_PIN, GPIO.FALLING, callback=button_callback,
                          bouncetime=1000)
    GPIO.add_event_detect(config.BUTTON_BOX_PIN, GPIO.FALLING, callback=button_callback,
                          bouncetime=1000)

    # Setup Analog controller
    AnalogInput.setup()

def main_loop():
    """Main loop
    Similair to the MainLoop() on an arduino, this will loop through indefinately,
    calling all required inputs and outputs to make the gate function
    """
    job = job_q.get()
    if job == 'open':
        gate.current_state = 'opening'
        with job_q.mutex:
            job_q.queue.clear()
    if gate.current_state == 'opening':
        gate.open()
    if gate.current_state == 'opened':
        gate.hold()
    if gate.current_state == 'holding':
        gate.close()



if __name__ == '__main__':
    logger.info('Starting smart gate')
    setup()
    gate = gate.Gate()
    job_q = JobQueue(config.VALID_COMMANDS, config.FIFO_FILE)
    battery_pin = AnalogInput(config.BATTERY_VOLTAGE_PIN)
    battery_logger = BatteryVoltageLog(config.BATTERY_VOLTAGE_LOG, battery_pin)
    battery_logger.start()
    try:
        while 1:
            main_loop()
    finally:
        GPIO.cleanup()
        job_q.cleanup()
