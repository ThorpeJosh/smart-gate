""" Test module to ensure the arduino mock interface is working correctly
"""
import time
from serial_analog import AnalogInputs


def test_setup_lock(caplog):
    """ Test that the AnalogInput setup lock to ensure that
    initialize() gets run exactly once before any pins are initialized
    else it should raise an exception
    """
    AnalogInputs.initialize()

    # Sleep to wait for logs from previous tests threads that are still shutting down
    time.sleep(1)

    caplog.clear()
    AnalogInputs.handshake()
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
    assert "Handshake has already been initiated" in caplog.text
    # Reset setup lock
    AnalogInputs.handshake_lock = False


def test_mock_input():
    """ Test to make sure the mock voltage and value intefaces are working
    """
    AnalogInputs.initialize()

    # Set a mock voltage
    voltage = 1.234
    AnalogInputs.mock_voltages[0] = voltage

    # Test that the values are returned
    assert AnalogInputs.get(0) == voltage
