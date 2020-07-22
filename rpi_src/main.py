"""Smart gate module entry point
"""
import logging
import logging.handlers

# Smart gate module imports
import config
from serial_analog import AnalogInputs
from battery_voltage_log import BatteryVoltageLog
from gate import Gate
from job_queue import JobQueue

# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Log to file, rotate logs every Monday
file_handler = logging.handlers.TimedRotatingFileHandler(config.GATE_LOG, when='W0', backupCount=50)
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
email_handler.setLevel(logging.WARNING)
logger.addHandler(email_handler)


def main_loop():
    """Loop for the normal operation mode
    """
    job = job_q.get()
    if job in config.MODES:
        gate.mode_change(job)
        return
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


def lock_closed_loop(_gate, queue):
    """Loop for when in the lock closed mode
    """
    # Close the gate
    _gate.close()
    # wait for the mode to change
    while _gate.current_mode == 'lock_closed':
        job = queue.get()
        if job in config.MODES:
            _gate.mode_change(job)


def lock_open_loop(_gate, queue):
    """Loop for when in the lock open mode
    """
    # Open the gate
    _gate.open()
    # wait for the mode to change
    while _gate.current_mode == 'lock_open':
        job = queue.get()
        if job in config.MODES:
            _gate.mode_change(job)


if __name__ == '__main__':
    logger.info('Starting smart gate')
    job_q = JobQueue(config.COMMANDS+config.MODES, config.FIFO_FILE)
    AnalogInputs.initialize()
    gate = Gate(job_q)
    battery_logger = BatteryVoltageLog(config.BATTERY_VOLTAGE_LOG, config.BATTERY_VOLTAGE_PIN)
    battery_logger.start()
    try:
        while 1:
            if gate.current_mode.startswith('normal'):
                main_loop()
            elif gate.current_mode == 'lock_closed':
                lock_closed_loop(gate, job_q)
            elif gate.current_mode == 'lock_open':
                lock_open_loop(gate, job_q)
            else:
                logger.critical("Unexpected mode: %s", gate.current_mode)
    # Catch and log any unexpected exception before program exits
    except Exception as exception:  # pylint: disable=broad-except
        logger.critical('Critical Exception: %s', exception)
    finally:
        job_q.cleanup()
