""" Unit tests for the main.py module
"""
import os
import threading
import time

import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

from config import Config as config
import main
from serial_analog import AnalogInputs
from gate import Gate
from job_queue import JobQueue


def delayed_put(delay, message, queue):
    """ Function to be threaded that puts a message on a queue after a delay
    Keyword arguments:
        delay - delay in seconds to wait before putting message on queue
        message - message to put
        queue - queue to put to
    """
    time.sleep(delay)
    queue.validate_and_put(message)


def test_lock_open_loop(tmp_path):
    """ Test for lock_open mode loop, to ensure it does not exit until another mode is selected
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    # Setup gate dependencies
    AnalogInputs.initialize()
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_queue = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    gate = Gate(test_queue)

    # Set gate mode to lock_open
    gate.current_mode = 'lock_open'

    # Ensure queue is empty to start
    assert test_queue.get_nonblocking() is None
    # Set shunt voltage above threshold to indicate gate already in position
    AnalogInputs.mock_voltages[config.SHUNT_PIN] = 10

    start_time = time.monotonic()
    # put a non mode message on the queue to ensure it ignores it
    threading.Thread(target=lambda: delayed_put(0.2, 'open', test_queue)).start()
    # put a non lock_open mode message on the queue in 1 second
    threading.Thread(target=lambda: delayed_put(1.5, 'lock_closed', test_queue)).start()
    main.lock_open_loop(gate, test_queue)
    time_taken = time.monotonic()-start_time
    assert time_taken == pytest.approx(1.5, 0.2)

    #Cleanup
    test_queue.cleanup()


def test_lock_closed_loop(tmp_path):
    """ Test for lock_closed mode loop, to ensure it does not exit until another mode is selected
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    # Setup gate dependencies
    AnalogInputs.initialize()
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_queue = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    gate = Gate(test_queue)

    # Set gate mode to lock_open
    gate.current_mode = 'lock_closed'

    # Ensure queue is empty to start
    assert test_queue.get_nonblocking() is None
    # Set shunt voltage above threshold to indicate gate already in position
    AnalogInputs.mock_voltages[config.SHUNT_PIN] = 10

    start_time = time.monotonic()
    # put a non mode message on the queue to ensure it ignores it
    threading.Thread(target=lambda: delayed_put(0.2, 'open', test_queue)).start()
    # put a non lock_closed mode message on the queue in 1 second
    threading.Thread(target=lambda: delayed_put(1.5, 'lock_open', test_queue)).start()
    main.lock_closed_loop(gate, test_queue)
    time_taken = time.monotonic()-start_time
    assert time_taken == pytest.approx(1.5, 0.2)

    #Cleanup
    test_queue.cleanup()
