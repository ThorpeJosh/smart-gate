"""Smart gate module entry point
"""
import logging
import logging.handlers
import gpiozero
# Smart gate module imports
import config
from gate import Gate
from adc import AnalogInput
from battery_voltage_log import BatteryVoltageLog
from job_queue import JobQueue

# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Log to file
file_handler = logging.FileHandler(config.GATE_LOG)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)

# Log to stdout as well
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

# Log to email
email_handler = logging.handlers.SMTPHandler(mailhost=(config.SMTP, config.PORT),
                                             fromaddr=config.FROMADDR,
                                             toaddrs=config.TOADDRS,
                                             subject=config.SUBJECT,
                                             credentials=(config.USER_ID, config.USER_KEY),
                                             secure=())
email_handler.setFormatter(logging.Formatter(LOG_FORMAT))
email_handler.setLevel(logging.ERROR)
logger.addHandler(email_handler)


def button_callback(button, queue):
    """Callback for when a button is pushed
    button - The button object that triggered the callback
    queue - The queue that a button trigger should put a job on
    """
    pin = button.pin.number
    if pin == config.BUTTON_OUTSIDE_PIN:
        logger.info('Outside button pressed')
    elif pin == config.BUTTON_INSIDE_PIN:
        logger.info('Inside button pressed')
    elif pin == config.BUTTON_BOX_PIN:
        logger.info('Box button pressed')
    else:
        logger.warning('Unknown button pressed')

    queue.validate_and_put('open')


def setup_button_pins(queue):
    """Setup for button pins
    queue - The queue that a button trigger should put a job on
    """
    logger.debug('Running button setup')

    # Initialize input pins
    outside_button = gpiozero.Button(config.BUTTON_OUTSIDE_PIN, pull_up=True, bounce_time=0.1)
    inside_button = gpiozero.Button(config.BUTTON_INSIDE_PIN, pull_up=True, bounce_time=0.1)
    box_button = gpiozero.Button(config.BUTTON_BOX_PIN, pull_up=True, bounce_time=0.1)

    # Button callbacks
    outside_button.when_pressed = lambda: button_callback(outside_button, queue)
    inside_button.when_pressed = lambda: button_callback(inside_button, queue)
    box_button.when_pressed = lambda: button_callback(box_button, queue)


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
    job_q = JobQueue(config.COMMANDS+config.MODES, config.FIFO_FILE)
    setup_button_pins(job_q)
    AnalogInput.setup()
    gate = Gate(job_q)
    battery_pin = AnalogInput(config.BATTERY_VOLTAGE_PIN)
    battery_logger = BatteryVoltageLog(config.BATTERY_VOLTAGE_LOG, battery_pin)
    battery_logger.start()
    try:
        while 1:
            main_loop()
    finally:
        job_q.cleanup()
