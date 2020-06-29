""" Module to communicate with Arduino and get analog voltage values
"""
import logging
import time

import serial

logger = logging.getLogger("root")


class AnalogInputs:
    """ Class to manage the aquisition of analog voltages from an arduino.
    The arduino is presumed to be plugged into /dev/ttyUSB0 and serial is enabled on the RPi
    The arduino then takes the analog readings and sends them over serial upon recieveing a packet,
    from the RPi

    The handshake must be called prior to any values being returned
    """

    number_of_inputs = 6
    mock_mode = False
    handshake_lock = False
    try:
        ser = serial.Serial("/dev/ttyUSB0", baudrate=250000, timeout=1)
        ser.flush()
    except serial.serialutil.SerialException as error:
        logger.warning("Serial device not found: %s", error)
        logger.info("Entering mock analog mode")
        mock_mode = True
        mock_voltages = [0] * number_of_inputs

    @classmethod
    def get(cls, index="all"):
        """ Get the voltage message from the arduino and return that value specified by index
        index: should be an integer to specify which analog pin value to return
        """
        if not cls.handshake_lock:
            raise ValueError("Serial Handshake has not been initiated")

        if cls.mock_mode:
            if index == "all":
                return cls.mock_voltages
            return cls.mock_voltages[index]

        # Request serial package from arduino by sending capital A
        cls.ser.write("A".encode())
        voltages = [
            float(cls.ser.readline().decode("ascii").rstrip())
            for _ in range(cls.number_of_inputs)
        ]
        if index == "all":
            return voltages
        return voltages[index]

    @classmethod
    def handshake(cls):
        """ Performes a serial handshake with the Arduino by waiting for an 'A',
        then confirms handshake by send an 'A' back.
        Handshake must be called prior to getting any values
        """
        if cls.handshake_lock:
            logger.critical("Handshake has already been initiated")
            return
        if cls.mock_mode:
            logger.info("Initiating mock serial handshake")
            cls.handshake_lock = True
            return

        while cls.ser.readline().decode("ascii").rstrip() != "A":
            logger.debug("Waiting for serial handshake")
            time.sleep(0.1)
        cls.ser.write("A".encode())
        logger.info("Serial handshake achieved")
        cls.handshake_lock = True
