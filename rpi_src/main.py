"""Smart gate module entry point
"""
import logging

# Smart gate module imports
from config import Config as config
from serial_analog import ArduinoInterface
from battery_voltage_log import BatteryVoltageLog
from gate import Gate
from job_queue import JobQueue
from camera import Camera
from db import DB

logger = logging.getLogger('root')

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
            # If exiting lock_open into a normal mode, then cycle gate to ensure it closes.
            if job.startswith('normal'):
                queue.validate_and_put('open')
            _gate.mode_change(job)


if __name__ == '__main__':
    logger.info('Starting smart gate')
    db = DB()
    cam = Camera(db) if config.CAMERA_ENABLED else None
    job_q = JobQueue(config.COMMANDS+config.MODES, config.FIFO_FILE)
    gate = Gate(job_q)
    ArduinoInterface.initialize(gate, job_q, cam, db)
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
                raise ValueError("Unexpected Mode")
    # Catch and log any unexpected exception before program exits
    except Exception as exception:  # pylint: disable=broad-except
        logger.critical('Critical Exception: %s', exception)
    finally:
        logger.debug('running cleanup')
        db.cleanup()
        job_q.cleanup()
        config.log_listener.stop()
