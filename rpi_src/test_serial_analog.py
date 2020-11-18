""" Test module to ensure the arduino mock interface is working correctly
"""
import time
import logging
from serial_analog import ArduinoInterface


def test_setup_lock(caplog):
    """ Test that the AnalogInput setup lock to ensure that
    initialize() gets run exactly once before any pins are initialized
    else it should raise an exception
    """
    logging.disable(logging.NOTSET)
    ArduinoInterface.initialize()

    # Sleep to wait for logs from previous tests threads that are still shutting down
    time.sleep(1)

    caplog.clear()
    ArduinoInterface.handshake()
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
    assert "Handshake has already been initiated" in caplog.text
    # Reset setup lock
    ArduinoInterface.handshake_lock = False

    logging.disable(level=logging.CRITICAL)


def test_mock_input():
    """ Test to make sure the mock voltage and value intefaces are working
    """
    ArduinoInterface.initialize()

    # Set a mock voltage
    voltage = 1.234
    ArduinoInterface.mock_voltages[0] = voltage

    # Test that the values are returned
    assert ArduinoInterface.get_analog_voltages(0) == voltage
