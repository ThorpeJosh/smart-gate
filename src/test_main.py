""" Unit tests for the main.py module
"""
import time
import pytest
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import main
import config
from job_queue import JobQueue

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
