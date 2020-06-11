""" Test module to ensure the adc mock interface is working correctly
"""
from adc import AnalogInput


def test_setup_lock(caplog):
    """ Test that the AnalogInput setup lock to ensure that
    setup() gets run exactly once before any pins are initialized else it should raise an exception
    """
    AnalogInput.setup()

    caplog.clear()
    AnalogInput.setup()
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
    assert "Analog.setup() has already been called" in caplog.text
    # Reset setup lock
    AnalogInput.setup_lock = False


def test_mock_input():
    """ Test to make sure the mock voltage and value intefaces are working
    """
    AnalogInput.setup()
    mock_pin = AnalogInput(0)

    # Set some mock values
    value = 12345
    voltage = 1.234
    mock_pin.mock_value = value
    mock_pin.mock_voltage = voltage

    # Test that the values are returned
    assert mock_pin.value() == value
    assert mock_pin.voltage() == voltage

    # Reset setup lock
    AnalogInput.setup_lock = False
