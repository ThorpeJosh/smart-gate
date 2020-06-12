""" Unit tests for the main.py module
"""
import os
import time
import threading
import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import main
import config
from job_queue import JobQueue
from gate import Gate
from adc import AnalogInput

def delayed_put(delay, message, queue):
    """ Function to be threaded that puts a message on a queue after a delay
    Keyword arguments:
        delay - delay in seconds to wait before putting message on queue
        message - message to put
        queue - queue to put to
    """
    time.sleep(delay)
    queue.validate_and_put(message)


def test_setup_button_pins():
    """ Test that the button pins are setup correctly
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    main.setup_button_pins(None)

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


def test_button_callback():
    """Test that when the button is pushed that the callback puts a job on the queue
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    job_q = JobQueue(config.COMMANDS+config.MODES, 'test_button_pipe')
    main.setup_button_pins(job_q)

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
        assert job_q.get_nonblocking() == 'open'
    job_q.cleanup()


@pytest.mark.skip(reason="Not sure best way to test this yet")
def test_main_loop():
    """ Test for main_loop
    """


def test_lock_open_loop(tmp_path):
    """ Test for lock_open mode loop, to ensure it does not exit until another mode is selected
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    # Setup gate dependencies
    AnalogInput.setup()
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    job_q = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    gate = Gate(job_q)

    # Set gate mode to lock_open
    gate.current_mode = 'lock_open'

    # Ensure queue is empty to start
    assert job_q.get_nonblocking() is None
    # Set shunt voltage above threshold to indicate gate already in position
    gate.shunt_pin.mock_voltage = 10

    start_time = time.monotonic()
    # put a non mode message on the queue to ensure it ignores it
    threading.Thread(target=lambda: delayed_put(0.2, 'open', job_q)).start()
    # put a non lock_open mode message on the queue in 1 second
    threading.Thread(target=lambda: delayed_put(1, 'lock_closed', job_q)).start()
    main.lock_open_loop(gate, job_q)
    assert time.monotonic()-start_time == pytest.approx(1, 0.02)

    #Cleanup
    job_q.cleanup()
    del job_q


def test_lock_closed_loop(tmp_path):
    """ Test for lock_closed mode loop, to ensure it does not exit until another mode is selected
    """
    # Setup mock pins
    factory = MockFactory()
    Device.pin_factory = factory
    factory.reset()
    # Setup gate dependencies
    AnalogInput.setup()
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    job_q = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    gate = Gate(job_q)

    # Set gate mode to lock_open
    gate.current_mode = 'lock_closed'

    # Ensure queue is empty to start
    assert job_q.get_nonblocking() is None
    # Set shunt voltage above threshold to indicate gate already in position
    gate.shunt_pin.mock_voltage = 10

    start_time = time.monotonic()
    # put a non mode message on the queue to ensure it ignores it
    threading.Thread(target=lambda: delayed_put(0.2, 'open', job_q)).start()
    # put a non lock_open mode message on the queue in 1 second
    threading.Thread(target=lambda: delayed_put(1, 'lock_open', job_q)).start()
    main.lock_closed_loop(gate, job_q)
    assert time.monotonic()-start_time == pytest.approx(1, 0.02)

    #Cleanup
    job_q.cleanup()
    del job_q
