""" Module to handle the capturing of pictures and videos for vehicles or perople that operate
the smart-gate
"""
import os
import datetime
import time
import logging
import queue
from picamera import PiCamera

from config import Config as config

logger = logging.getLogger('root')

class Camera():

    def __init__():
        pass

    def take_picture(self):
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

        # Create camera objects
        camera = PiCamera()
        camera.resolution = (2592, 1944)

        camera.start_preview()
        time.sleep(5)
        camera.capture(os.path.join(config.RECORDING_PATH, '{}.jpg'.format(self.datetime_string)))
        camera.close()

