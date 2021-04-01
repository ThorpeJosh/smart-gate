""" Module to communicate with Arduino
"""
import logging
import datetime
import time
import queue
import threading
import serial
from config import Config as config

logger = logging.getLogger("root")

class ArduinoInterfaceError(Exception):
    """ Class of errors to be raised if something goes wrong with the serial ardiuno interface
    """

class ArduinoInterface:
    """ Class to manage the communication with the arduino.
    The arduino is presumed to be plugged into /dev/ttyUSB0 and serial is enabled on the RPi
    The arduino then takes the analog readings and sends them over serial upon recieveing a packet,
    from the RPi

    The handshake must be called prior to any values being returned
    """

    @classmethod
    def initialize(cls, gate=None, job_q=None, cam=None, entry_db=None):
        """ Method similar to __init__ but it does not make sense for any instances to be created
        of this class.
        This method initializes the class variables and sets up mock mode if necessary.
        """
        cls.gate = gate

        # Create a class rotating file logger for all arduino messages
        cls.arduino_logger = logging.getLogger(__name__)
        cls.arduino_logger.setLevel(logging.DEBUG)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            config.ARDUINO_LOG, when="W0", backupCount=50
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s : %(message)s"))
        cls.arduino_logger.addHandler(file_handler)

        # Number of analog channels on the arduino
        cls.number_of_inputs = 6
        # Voltage decimal places
        cls.precision = 4
        cls.mock_mode = False
        cls.handshake_lock = False
        # Give cls.read_serial access to the global job_q
        if job_q is not None:
            cls.job_q = job_q
        else:
            logger.warning("Job Queue was not passed to ArduinoInterface,\
Arduino will not be able to trigger the gate opening")
        # Initiate the serial connection
        try:
            cls.ser = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
            cls.ser.flush()
            # Start the serial thread
            cls.handshake()
            threading.Thread(target=cls.read_serial, daemon=True).start()
        except serial.serialutil.SerialException as error:
            logger.warning("Serial device not found: %s", error)
            logger.info("Entering mock analog mode")
            cls.mock_mode = True
            cls.mock_voltages = [0] * cls.number_of_inputs
            cls.handshake()
        cls.arduino_queue = queue.Queue()
        cls.camera_queue = cam.camera_q if cam is not None else None
        # Give class access to the db
        cls.db = entry_db if entry_db is not None else \
                logger.warning("DB was not passed to ArduinoInterface")

    @classmethod
    def get_analog_voltages(cls, index="all"):
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
        try:
            voltages = [cls.arduino_queue.get(timeout=0.5) for _ in range(cls.number_of_inputs)]
            if index == "all":
                return voltages
            return voltages[index]
        except queue.Empty:
            raise ArduinoInterfaceError('Arduino Queue was empty when trying to get voltages') \
                    from None

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
            # Catch serial errors
            try:
                cls.ser.timeout = 1
                data = cls.ser.readline().decode("ascii").rstrip()
                if data == 'V':
                    # Arduino is sending analog voltages
                    cls._arduino_receive_voltages()

                elif data == 'O':
                    # Arduino has requested the gate to open
                    cls.arduino_logger.debug(data)
                    cls._arduino_receive_trigger()

                elif data == 'R':
                    # Arduino is requesting the 433MHz radio secret key
                    cls.arduino_logger.debug(data)
                    cls._arduino_requesting_radiokey()

                elif data == 'B':
                    # Arduino is requesting the button pins
                    cls.arduino_logger.debug(data)
                    cls._arduino_requesting_buttons()

            except serial.serialutil.SerialException as err:
                logger.critical('Shutting down gate due to serial error %s', err)
                return

    @classmethod
    def _arduino_receive_voltages(cls):
        """ Arduino is sending analog voltages through. Receive them and perform a
        checksum to ensure they all came through successfully
        """
        # Remove serial timeout so it doesn't hang in here
        cls.ser.timeout = 0
        # Arduino is sending analog voltages, collect and put on queue
        voltages = [cls.ser.readline().decode("ascii").rstrip()
                    for _ in range(cls.number_of_inputs)]
        checksum = cls.ser.readline().decode("ascii").rstrip()
        try:
            # Check that the voltages are valid floats
            voltages = [float(voltage) for voltage in voltages]
            checksum = float(checksum)
            # Check that the voltage checksum matches the data received
            if round(sum(voltages), cls.precision) == checksum:
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
        cls.ser.timeout = 1

    @classmethod
    def _arduino_receive_trigger(cls):
        """ Arduino has sent a request to open the gate. This method handles the serial and
        logging of either the button or 433MHz radio that triggered the Arduino.
        """
        # pylint: disable=too-many-branches
        message = cls.ser.readline().decode("ascii").rstrip()
        message_dt = datetime.datetime.now()
        logger.debug("Arduino: %s", message)
        cls.arduino_logger.debug(message)
        # Check what button triggered the arduino and send email if in away mode
        try:
            pin = int(message)
            if pin == config.BUTTON_OUTSIDE_PIN:
                button = "outside"
                if cls.gate.current_mode.endswith("away"):
                    logger.warning("Outside button pressed")
                else:
                    logger.info("Outside button pressed")
                # Take picture
                if cls.camera_queue is not None:
                    cls.camera_queue.put("outside")
            elif pin == config.BUTTON_INSIDE_PIN:
                button = "inside"
                if cls.gate.current_mode.endswith("away"):
                    logger.warning("Inside button pressed")
                else:
                    logger.info("Inside button pressed")
                # Take picture
                if cls.camera_queue is not None:
                    cls.camera_queue.put("inside")
            elif pin == config.BUTTON_BOX_PIN:
                button = "box"
                if cls.gate.current_mode.endswith("away"):
                    logger.warning("Box button pressed")
                else:
                    logger.info("Box button pressed")
            else:
                button = "unknown"
                logger.warning("Unknown button pressed")
            cls.job_q.validate_and_put('open')
            cls.db.add_entry(button, message_dt)
        except AttributeError:
            logger.debug("Arduino tried to open gate, but didn't have access to queue")
        except ValueError:
            logger.debug("Arduino did not supply a valid pin value, likely the 433MHz")

    @classmethod
    def _arduino_requesting_radiokey(cls):
        """ Arduino is requesting radiokey for 433MHz, if a key exists then send it through"""
        try:
            key = config.RADIO_KEY
            key = key.strip().replace("\n", "")
            logger.debug("Read radio key from config: %s", key)
            if len(key) != 8:
                raise ValueError
            logger.debug("Sending radio secret key to Arduino")
            cls.ser.write(key.encode())
        except ValueError:
            logger.warning("Radio key is not 8 characters long, please revise for radio operation")
            cls.ser.write(('x'*10).encode())

    @classmethod
    def _arduino_requesting_buttons(cls):
        """ Arduino is requesting input button pin numbers"""
        logger.debug("Sending button pins to Arduino")
        for pin in [config.BUTTON_OUTSIDE_PIN,
                    config.BUTTON_INSIDE_PIN,
                    config.BUTTON_BOX_PIN]:
            cls.ser.write(str(pin).encode())
        logger.debug("Finished sending button pins to Arduino")
        # Arduino expects to get a "B" back when all button pins are sent
        cls.ser.write("B".encode())
