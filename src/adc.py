"""Module to handle analog reading using the ADS1115
"""
import board
import busio
import time
import statistics
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


class AnalogInput:
    setup_lock = False
    #ADC object for the ADS1115 on the I2C bus, after setup()
    ads = None

    def __init__(self, pin1, pin2 = None):
        """Initialize a new analog intput channel
        """
        # Ensure  setup method has run
        assert self.setup_lock

        if pin2 is None:
            # Create single-ended input on channel 0
            exec('chan = AnalogIn(ads, ADS.P{})'.format(pin1))
        else:
            exec('chan = AnalogIn(ads, ADS.P{}, ADS.P{})'.format(pin1, pin2))
        self.analog_channel = chan

    def value(self):
        """Wrapper for returning value of analog_channel object with median smoothing over 50ms
        """
        readings = []
        for i in range(50):
            readings.append(self.analog_channel.value)
            time.sleep(0.01)
        return statistics.median(readings)

    def voltage(self):
        """Wrapper for returning voltage of analog_channel object with median smoothing over 50ms
        """
        readings = []
        for i in range(50):
            readings.append(self.analog_channel.voltage)
            time.sleep(0.01)
        return statistics.median(readings)


    @classmethod
    def setup(cls):
        """ Setup method to be called once prior to any ananlog channels being used.
            cls.setup_lock will be true if this setup method has been called already.
        """
        if cls.setup_lock:
            raise ValueError('AnalogInput.setup() has already been called')

        # Create the I2C bus
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except ValueError:
            print("I2C could not be initiated. Run raspi-config and ensure I2C is enabled")

        # Create the ADC object using the I2C bus
        cls.ads = ADS.ADS1015(i2c)
        
        cls.setup_lock = True

    def debug(self):
        """Method to debug and calibrate analog inputs
        """
        while True:
            print("{:>5}\t{:>5.3f}".format(self.value(), self.voltage()))
            time.sleep(0.1)
