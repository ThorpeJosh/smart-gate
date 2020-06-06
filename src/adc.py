"""Module to handle analog reading using the ADS1115
"""
import logging
import statistics
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn #pylint: disable=unused-import

logger = logging.getLogger('root')

class AnalogInput:
    """Class to handle analog inputs
    Call AnanlogInput.setup() once to setup the ADC connection,
    Then create AnalogInput objects for each pin and get readings as follows...
        analog_pin0 = AnalogInput(0)
        voltage = analog_pin0.voltage()
        value = analog_pin0.value()
    """
    setup_lock = False
    #ADC object for the ADS1115 on the I2C bus, after setup()
    ads = None
    # If true then this is running on a non-RPi device
    mock = None

    def __init__(self, pin1, pin2=None):
        """Initialize a new analog intput channel
        """
        #pylint: disable=eval-used
        #Ensure setup method has run
        if not self.setup_lock:
            raise ValueError('AnalogInput.setup() has not been called')

        if self.mock:
            self.mock_value = None
            self.mock_voltage = None
            return

        if pin2 is None:
            # Create single-ended input on channel 0
            chan = eval('AnalogIn(self.ads, ADS.P{})'.format(pin1))
        else:
	    # Create a referenced input on channel 0 (out=pin1-pin2)
            chan = eval('AnalogIn(self.ads, ADS.P{}, ADS.P{})'.format(pin1, pin2))
        self.analog_channel = chan

    def value(self):
        """Wrapper for returning value of analog_channel object with median smoothing over 50ms
        """
        if self.mock:
            return self.mock_value

        readings = []
        for _ in range(7):
            # No need for delay as each call for reading takes 10ms
            readings.append(self.analog_channel.value)
        return statistics.median(readings)

    def voltage(self):
        """Wrapper for returning voltage of analog_channel object with median smoothing over 50ms
        """
        if self.mock:
            return self.mock_voltage

        readings = []
        for _ in range(7):
            # No need for delay as each call for reading takes 10ms
            readings.append(self.analog_channel.voltage)
        return statistics.median(readings)


    @classmethod
    def setup(cls):
        """ Setup method to be called once prior to any ananlog channels being used.
            cls.setup_lock will be true if this setup method has been called already.
        """
        if cls.setup_lock:
            raise ValueError('AnalogInput.setup() has already been called')

        if cls.mock:
            logger.info('Setup run on mock analog interface')
            cls.setup_lock = True
            return

        # Create the I2C bus
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            # Create the ADC object using the I2C bus
            cls.ads = ADS.ADS1015(i2c)
        except ValueError as err:
            logger.critical("I2C could not be initiated, reverting to Mock Interface. \
Run raspi-config and ensure I2C is enabled or ensure I2C device is connected correctly: %s", err)
            cls.mock = True

        cls.setup_lock = True

    def debug(self):
        """Method to debug and calibrate analog inputs
        """
        while True:
            print("{:>5}\t{:>5.3f}".format(self.value(), self.voltage()))


try:
    import board
    AnalogInput.mock = False
except NotImplementedError:
    AnalogInput.mock = True
    logger.critical('Using mock AnalogInput')
