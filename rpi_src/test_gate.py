""" Test module for the gate class
"""
import logging
import os
import time
import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

import config
from serial_analog import AnalogInputs
from gate import Gate
from job_queue import JobQueue

logging.disable(level=logging.CRITICAL)

def test_motor_pins(tmp_path):
    """ Testing open method
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    # pylint: disable=protected-access
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue(config.COMMANDS, fifo_file)
    AnalogInputs.initialize()
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
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    # Alter safety timer to make test faster
    config.MAX_TIME_TO_OPEN_CLOSE = 2

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInputs.initialize()
    gate = Gate(test_q)

    start = time.monotonic()
    gate.open()
    # Check that the gate is stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check that the time matches the time in config.MAX_TIME_TO_OPEN_CLOSE
    time_taken = time.monotonic()-start
    assert time_taken == pytest.approx(config.MAX_TIME_TO_OPEN_CLOSE, 0.2)
    test_q.cleanup()
    del test_q


def test_close_timeout(tmp_path):
    """ Test to ensure the safety timer works correctly
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    # Alter safety timer to make test faster
    config.MAX_TIME_TO_OPEN_CLOSE = 2

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInputs.initialize()
    gate = Gate(test_q)

    start = time.monotonic()
    gate.close()
    # Check that the gate is stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check that the time matches the time in config.MAX_TIME_TO_OPEN_CLOSE
    time_taken = time.monotonic()-start
    assert time_taken == pytest.approx(config.MAX_TIME_TO_OPEN_CLOSE, 0.2)
    test_q.cleanup()
    del test_q


def test_open_shunt(tmp_path):
    """ Test to ensure the gate stops if it hits something on opening
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInputs.initialize()
    gate = Gate(test_q)

    # Setup shunt voltage as a high value
    AnalogInputs.mock_voltages[config.SHUNT_PIN] = 10
    start = time.monotonic()
    gate.open()

    # Check the gate stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check the gate stopped immediately
    time_taken = time.monotonic()-start
    assert time_taken == pytest.approx(config.SHUNT_READ_DELAY, 0.1)
    test_q.cleanup()
    del test_q


def test_close_shunt(tmp_path):
    """ Test to ensure the gate stops and reopens if it hits something on closing
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue(config.COMMANDS, fifo_file)
    AnalogInputs.initialize()
    gate = Gate(test_q)

    # Setup shunt voltage as a high value
    AnalogInputs.mock_voltages[config.SHUNT_PIN] = 10
    start = time.monotonic()
    gate.close()

    # Check the gate stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check the gate stopped immediately
    time_taken = time.monotonic()-start
    assert time_taken == pytest.approx(config.SHUNT_READ_DELAY, 0.1)
    # Check that the gate is set to reopen immediately
    assert test_q.get_nonblocking() == 'open'
    test_q.cleanup()
    del test_q


def test_normal_close_shunt(tmp_path):
    """ Test to ensure the gate stops when it hits something withing the expected timeframe
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    # Set the expected, min and max times to open
    config.EXPECTED_TIME_TO_OPEN_CLOSE = 1
    config.MAX_TIME_TO_OPEN_CLOSE = 2
    config.MIN_TIME_TO_OPEN_CLOSE = 0

    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue(config.COMMANDS, fifo_file)
    AnalogInputs.initialize()
    gate = Gate(test_q)

    # Setup shunt voltage as a high value
    AnalogInputs.mock_voltages[config.SHUNT_PIN] = 10
    start = time.monotonic()
    gate.close()

    # Check the gate stopped
    assert gate.motor_pin0.value == 0
    assert gate.motor_pin1.value == 0
    # Check the gate stopped immediately
    time_taken = time.monotonic()-start
    assert time_taken == pytest.approx(config.SHUNT_READ_DELAY, 0.1)
    # Check that the gate is in the closed state
    assert gate.current_state == "closed"
    assert test_q.empty()
    test_q.cleanup()
    del test_q


def test_mode_changing(tmp_path):
    """ Test the mode change feature to ensure it:
    - Defaults to the normal mode if no save file is found
    - Can change modes successfully and save new mode to file
    - Resumes a saved mode upon restart
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()

    save_mode_file = os.path.join(str(tmp_path), 'mode.txt')
    # Point gate to the dummy file
    config.SAVED_MODE_FILE = save_mode_file
    # Setup gate
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    test_q = JobQueue([], fifo_file)
    AnalogInputs.initialize()

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
    factory.reset()
    gate = Gate(test_q)
    assert gate.current_mode == 'lock_open'

    # Cleanup
    test_q.cleanup()
    del test_q


def test_setup_button_pins(tmp_path):
    """ Test that the button pins are setup correctly
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    job_q = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    AnalogInputs.initialize()
    _ = Gate(job_q)

    for pin in [config.BUTTON_OUTSIDE_PIN, config.BUTTON_INSIDE_PIN, config.BUTTON_BOX_PIN]:
        pin_obj = Device.pin_factory.pin(pin)
        # Check pin is infact an input pin
        assert pin_obj.function == 'input'
        # Check pin number is correct
        assert pin_obj.number == pin
        # Check pull up resistor is enabled
        assert pin_obj.pull == 'up'
        # Check debounce is enabled
        assert pin_obj.bounce == 0.1
        # Check that the pin value is high due to pull up resistor
        assert pin_obj.state == 1

    # Cleanup
    job_q.cleanup()


def test_button_callback():
    """Test that when the button is pushed that the callback puts a job on the queue
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    job_q = JobQueue(config.COMMANDS+config.MODES, 'test_button_pipe')
    AnalogInputs.initialize()
    _ = Gate(job_q)

    for pin in [config.BUTTON_OUTSIDE_PIN, config.BUTTON_INSIDE_PIN, config.BUTTON_BOX_PIN]:
        pin_obj = Device.pin_factory.pin(pin)
        # Check job queue is empty
        assert job_q.get_nonblocking() is None
        # Press button
        pin_obj.drive_low()
        assert pin_obj.state == 0
        time.sleep(0.2)
        pin_obj.drive_high()
        assert pin_obj.state == 1
        # Check job queue has job
        assert job_q.get(timeout=2) == 'open'

    # Cleanup
    job_q.cleanup()
    del job_q
