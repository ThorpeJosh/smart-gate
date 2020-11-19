""" Module to handle the capturing of pictures and videos for vehicles or perople that operate
the smart-gate
"""
import os
import datetime
import time
import logging
import queue
import threading
from config import Config as config
from serial_analog import ArduinoInterface

logger = logging.getLogger('root')

try:
    from picamera import PiCamera
except OSError:
    # Camera module only works on RPi, ensure it is disabled
    config.CAMERA_ENABLED = False

class Camera():
    """ Class to handle operations of the camera """
    def __init__(self):
        # setup camera queue and start a thread to read it and handle the camera
        self.camera_q = queue.Queue()
        threading.Thread(target=self._read_queue, daemon=True).start()
        logger.debug("Camera class has been initialized")

    @staticmethod
    def move_servo(position):
        """ Request arduino to move servo to position
        position: a value between 0 and 180 """
        assert 0 <= position <= 180
        ArduinoInterface.ser.write("S".encode())
        ArduinoInterface.ser.write(position.to_bytes(1, byteorder='little'))


    @staticmethod
    def take_picture():
        """ Method to take a picture using the rpi camera
        """
        # Record datetime for filename
        now = datetime.datetime.now()
        datetime_string = '{}{}{}{}{}{}'.format(
            str(now.year).zfill(4),
            str(now.month).zfill(2),
            str(now.day).zfill(2),
            str(now.hour).zfill(2),
            str(now.minute).zfill(2),
            str(now.second).zfill(2))
        filename = os.path.join(config.CAMERA_SAVE_PATH, '{}.jpg'.format(datetime_string))
        logger.debug("Taking a picture: %s", filename)

        # Create camera objects
        camera = PiCamera()
        camera.resolution = (2592, 1944)

        camera.start_preview()
        time.sleep(5)
        camera.capture(filename)
        camera.close()

    def _read_queue(self):
        """ Method that monitors camera queue and takes pictures when requested
        """
        while True:
            job = self.camera_q.get()
            logger.debug("Camera queue: %s", job)
            # Exit thread gracefully with a 'kill' command
            if job == 'kill':
                logger.warning('received kill command on camera queue')
                return
            if job == 'inside':
                self.move_servo(config.CAMERA_INSIDE_ANGLE)
                self.take_picture()
            elif job == 'outside':
                self.move_servo(config.CAMERA_OUTSIDE_ANGLE)
                self.take_picture()
            else:
                logger.warning("Received invalid command on camera queue")
