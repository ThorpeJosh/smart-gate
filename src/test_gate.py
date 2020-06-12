""" Test module for the gate class
"""
import time
import os
import logging
import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import config
from job_queue import JobQueue
from gate import Gate
from adc import AnalogInput

logger = logging.getLogger(__name__)

# Setup mock pins
factory = MockFactory()
Device.pin_factory = factory
factory.reset()


def test_motor_pins(tmp_path):
    """ Testing open method
    """
    #pylint: disable=protected-access
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue(config.COMMANDS, fifo_file)
    AnalogInput.setup()
    gate = Gate(test_q)
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    gate._open()
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 1
    gate._close()
    assert gate.motor_pin0.value == 1
    assert gate.motor_pin1.value == 0
    gate._stop()
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    test_q.cleanup()
    del test_q


def test_open_timeout(tmp_path):
    """ Test to ensure the safety timer works correctly
    """
    # Alter safety timer to make test faster
    config.MAX_TIME_TO_OPEN_CLOSE = 1

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInput.setup()
    gate = Gate(test_q)

    start = time.monotonic()
    gate.open()
    # Check that the gate is stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check that the time matches the time in config.MAX_TIME_TO_OPEN_CLOSE
    assert time.monotonic()-start == pytest.approx(config.MAX_TIME_TO_OPEN_CLOSE, 0.01)
    test_q.cleanup()
    del test_q


def test_close_timeout(tmp_path):
    """ Test to ensure the safety timer works correctly
    """
    # Alter safety timer to make test faster
    config.MAX_TIME_TO_OPEN_CLOSE = 1

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInput.setup()
    gate = Gate(test_q)

    start = time.monotonic()
    gate.close()
    # Check that the gate is stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check that the time matches the time in config.MAX_TIME_TO_OPEN_CLOSE
    assert time.monotonic()-start == pytest.approx(config.MAX_TIME_TO_OPEN_CLOSE, 0.01)
    test_q.cleanup()
    del test_q


def test_open_shunt(tmp_path):
    """ Test to ensure the gate stops if it hits something on opening
    """
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInput.setup()
    gate = Gate(test_q)

    # Setup shunt voltage as a high value
    gate.shunt_pin.mock_voltage = 10
    start = time.monotonic()
    gate.open()

    #Check the gate stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check the gate stopped immediately
    assert time.monotonic()-start == pytest.approx(config.SHUNT_READ_DELAY, 0.01)
    test_q.cleanup()
    del test_q


def test_close_shunt(tmp_path):
    """ Test to ensure the gate stops if it hits something on closing
    """
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInput.setup()
    gate = Gate(test_q)

    # Setup shunt voltage as a high value
    gate.shunt_pin.mock_voltage = 10
    start = time.monotonic()
    gate.close()

    #Check the gate stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check the gate stopped immediately
    assert time.monotonic()-start == pytest.approx(config.SHUNT_READ_DELAY, 0.01)
    test_q.cleanup()
    del test_q


def test_mode_changing(tmp_path):
    """ Test the mode change feature to ensure it:
    - Defaults to the normal mode if no save file is found
    - Can change modes successfully and save new mode to file
    - Resumes a saved mode upon restart
    """
    save_mode_file = os.path.join(str(tmp_path), 'mode.txt')
    # Point gate to the dummy file
    config.SAVED_MODE_FILE = save_mode_file
    # Setup gate
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInput.setup()

    # Ensure when no saved mode exists, it defaults to normal-home mode
    gate = Gate(test_q)
    assert gate.current_mode == 'normal_home'

    # Ensure that an incorrect mode is ignored
    for invalid_mode in ['invalid_mode', 12, -1, 4+2j, 0.234]:
        gate.mode_change(invalid_mode)
        assert gate.current_mode == 'normal_home'

    # Ensure that the mode changes and saves successfully
    for valid_mode in config.MODES:
        gate.mode_change(valid_mode)
        assert gate.current_mode == valid_mode
        with open(save_mode_file, 'r') as saved_mode:
            mode = saved_mode.read()
            mode = mode.strip().replace('\n', '')
            assert mode == valid_mode

    # Ensure that the mode is recovered upon restart
    gate.mode_change('lock_open')
    del gate
    gate = Gate(test_q)
    assert gate.current_mode == 'lock_open'

    # Cleanup
    test_q.cleanup()
    del test_q
