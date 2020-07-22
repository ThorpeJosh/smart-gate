""" Module to communicate with Arduino and get analog voltage values
"""
import logging
import time
import queue
import threading
import serial

logger = logging.getLogger("root")


class AnalogInputs:
    """ Class to manage the aquisition of analog voltages from an arduino.
    The arduino is presumed to be plugged into /dev/ttyUSB0 and serial is enabled on the RPi
    The arduino then takes the analog readings and sends them over serial upon recieveing a packet,
    from the RPi

    The handshake must be called prior to any values being returned
    """

    @classmethod
    def initialize(cls):
        """ Method similar to __init__ but it does not make sense for any instances to be created
        of this class.
        This method initializes the class variables and sets up mock mode if necessary.
        """
        cls.number_of_inputs = 6
        cls.mock_mode = False
        cls.handshake_lock = False
        try:
            cls.ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
            cls.ser.flush()
            # Start the serial thread
            threading.Thread(target=cls.read_serial, daemon=True).start()
        except serial.serialutil.SerialException as error:
            logger.warning("Serial device not found: %s", error)
            logger.info("Entering mock analog mode")
            cls.mock_mode = True
            cls.mock_voltages = [0] * cls.number_of_inputs
        cls.arduino_queue = queue.Queue()
        cls.handshake()

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

        # Request serial package from arduino by sending capital V
        cls.ser.write("V".encode())
        voltages = [cls.arduino_queue.get() for _ in range(cls.number_of_inputs)]
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

    @classmethod
    def read_serial(cls):
        """ Indefinite serial reading
        This is done with a blocking command to reduce cpu usage.
        """
        while True:
            data = cls.ser.readline().decode("ascii").rstrip()
            if data == 'V':
                # Arduino is sending analog voltages, collect and put on queue
                voltages = [cls.ser.readline().decode("ascii").rstrip()
                            for _ in range(cls.number_of_inputs)]
                checksum = cls.ser.readline().decode("ascii").rstrip()
                try:
                    # Check that the voltages are valid floats
                    voltages = [float(voltage) for voltage in voltages]
                    checksum = float(checksum)
                    # Check that the voltage checksum matches the data received
                    if sum(voltages) == checksum:
                        for voltage in voltages:
                            cls.arduino_queue.put(voltage)
                    else:
                        raise ValueError("Sum of voltages {} does not match checksum {}".format(
                            sum(voltages), checksum))
                except ValueError as err:
                    logger.warning(err)
                    time.sleep(0.001)
                    cls.ser.flushInput()
                    logger.debug("Requesting another set of voltages from Arduino")
                    cls.ser.write("V".encode())
            elif data == 'O':
                pass
