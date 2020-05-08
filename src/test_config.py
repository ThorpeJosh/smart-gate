"""Unit Tests for the config module
"""
import config

GPIO_PINS = [config.MOTORPIN0,
             config.MOTORPIN1,
             config.BUTTON_OUTSIDE_PIN,
             config.BUTTON_INSIDE_PIN,
             config.BUTTON_BOX_PIN]

ANALOG_PINS = [config.SHUNT_PIN,
               config.BATTERY_VOLTAGE_PIN]

def test_gpio_pins():
    """Test configuration pin values are logical
    """
    # Ensure no duplicates in pin list
    assert len(GPIO_PINS) == len(set(GPIO_PINS))
    # Ensure pins are positive integers between 1 and 40
    for pin in GPIO_PINS:
        assert isinstance(pin, int)
        assert 1 <= pin <= 40


def test_analog_pins():
    """Test configuration pin values are logical
    """
    # Ensure no duplicates in pin list
    assert len(ANALOG_PINS) == len(set(ANALOG_PINS))
    # Ensure pins are positive integers between 0 and 3
    for pin in ANALOG_PINS:
        assert isinstance(pin, int)
        assert 0 <= pin <= 3
