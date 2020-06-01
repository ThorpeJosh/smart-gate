""" Test module to ensure the adc mock interface is working correctly
"""
import pytest
from adc import AnalogInput

def test_setup_lock():
    """ Test that the AnalogInput setup lock to ensure that
    setup() gets run exactly once before any pins are initialized else it should raise an exception
    """
    with pytest.raises(ValueError):
        _ = AnalogInput(1)

    AnalogInput.setup()

    with pytest.raises(ValueError):
        AnalogInput.setup()


def test_mock_input():
    """ Test to make sure the mock voltage and value intefaces are working
    """
    mock_pin = AnalogInput(0)

    # Set some mock values
    value = 12345
    voltage = 1.234
    mock_pin.mock_value = value
    mock_pin.mock_voltage = voltage

    # Test that the values are returned
    assert mock_pin.value() == value
    assert mock_pin.voltage() == voltage
