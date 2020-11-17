"""Module for the job queue and named pipe (FIFO) system
"""
import logging
import os
import queue
import subprocess
import threading
from config import Config as config
from battery_voltage_log import BatteryVoltageLog
from serial_analog import AnalogInputs

logger = logging.getLogger('root')


class JobQueue(queue.Queue):
    """Queue that holds commands for the gate to execute.
    Inheritated from the python queue class with the addition of a method that ensures the
    commands put on the queue are valid
    """
    def __init__(self, valid_commands, pipe_file):
        super().__init__(maxsize=10)
        assert isinstance(valid_commands, list)
        self.valid_commands = valid_commands
        # Setup FIFO named pipe
        self.pipe_file = pipe_file
        try:
            os.remove(self.pipe_file)
        except FileNotFoundError:
            pass
        finally:
            os.mkfifo(self.pipe_file)
        # Start reading from pipe in seperate thread
        # Set daemon=True to ensure the spawned thread dies when parent does
        self.read_thread = threading.Thread(target=self.read_fifo, daemon=True)
        self.read_thread.start()

    def validate_and_put(self, message):
        """Validates message is a valid command then puts it on the queue
        """
        # Ensure message is a string
        if not isinstance(message, str):
            return
        # Cleanup whitespace in string
        message = message.strip().replace('\n', '')
        if message in self.valid_commands:
            self.put(message)
        else:
            logger.warning('%s is not a valid command for queue', message)

    def get_nonblocking(self):
        """Non-blocking version of the parent classes get() method
        """
        if self.empty():
            return None
        return self.get()

    def cleanup(self):
        """Cleanup method to delete the named pipe and kill thread that was reading it
        """
        # Send kill command to the child process
        print(subprocess.run('echo {} > {}'.format('kill', self.pipe_file), shell=True, check=True))
        os.remove(self.pipe_file)

    def read_fifo(self):
        """ Indefinite FIFO pipe reading
        Open FIFO pipe and reads when the tunnel has a sender,
        it then closes and reopens to avoid exessive cpu usage.

        Note that reading a pipe is blocking so this function must be called in a seperate thread,
        hence the infinite loop.
        """
        while True:
            with open(self.pipe_file, 'r') as fifo:
                for job in fifo:
                    # Cleanup input message
                    job = job.strip().replace('\n', '')
                    logger.debug('Received message via pipe: %s', job)

                    # Check if message is for debugging
                    if job == 'log_battery':
                        # log battery voltage and do not put message on queue
                        bat_voltage = BatteryVoltageLog.analog_to_battery_voltage(
                            AnalogInputs.get(config.BATTERY_VOLTAGE_PIN), 2)
                        logger.debug("Battery voltage: %.2fv", bat_voltage)
                        continue

                    self.validate_and_put(job)
                    if job == 'kill':
                        logger.warning('Received kill command on read_fifo thread')
                        return
