""" Module to handle the capturing of pictures and videos for vehicles or perople that operate
the smart-gate
"""
import os
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
    def __init__(self, entry_db):
        # setup camera queue and start a thread to read it and handle the camera
        self.camera_q = queue.Queue()
        threading.Thread(target=self._read_queue, daemon=True).start()
        logger.debug("Camera class has been initialized")
        self.entry_db = entry_db

    @staticmethod
    def move_servo(position):
        """ Request arduino to move servo to position
        position: a value between 0 and 180 """
        assert 0 <= position <= 180
        ArduinoInterface.ser.write("S".encode())
        ArduinoInterface.ser.write(position.to_bytes(1, byteorder='little'))


    def take_picture(self, now):
        """ Method to take a picture using the rpi camera
        """
        datetime_string = '{}{}{}{}{}{}'.format(
            str(now.year).zfill(4),
            str(now.month).zfill(2),
            str(now.day).zfill(2),
            str(now.hour).zfill(2),
            str(now.minute).zfill(2),
            str(now.second).zfill(2))
        filename = '{}.jpg'.format(datetime_string)
        filepath = os.path.join(config.CAMERA_SAVE_PATH, filename)
        logger.debug("Taking a picture: %s", filepath)

        # Create camera objects
        camera = PiCamera()
        camera.resolution = (2592, 1944)

        camera.start_preview()
        time.sleep(5)
        camera.capture(filename)
        camera.close()

        # Update db with filename
        self.entry_db.add_media_filename(now, filename)

    def _read_queue(self):
        """ Method that monitors camera queue and takes pictures when requested
        """
        while True:
            job = self.camera_q.get()
            # If job is a tuple then  job is (button, datetime), else it will be "kill"
            if isinstance(job, tuple):
                job, entry_dt = job
            logger.debug("Camera queue: %s", job)
            # Exit thread gracefully with a 'kill' command
            if job == 'kill':
                logger.warning('received kill command on camera queue')
                return
            if job == 'inside':
                self.move_servo(config.CAMERA_INSIDE_ANGLE)
                self.take_picture(entry_dt)
            elif job == 'outside':
                self.move_servo(config.CAMERA_OUTSIDE_ANGLE)
                self.take_picture(entry_dt)
            else:
                logger.warning("Received invalid command on camera queue")
