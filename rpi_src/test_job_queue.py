"""Unit Tests for the job_queue module
"""
import os
import subprocess
import time

from config import Config as config
from job_queue import JobQueue


def test_queue(tmp_path):
    """Testing just the modified queue put and get methods
    """
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    job_q = JobQueue(config.COMMANDS+config.MODES, fifo_file)
    # Check queue is empty
    assert job_q.get_nonblocking() is None
    # Check valid commands work
    for command in config.COMMANDS+config.MODES:
        job_q.validate_and_put(command)
    for command in config.COMMANDS+config.MODES:
        assert job_q.get_nonblocking() == command
    # Check invalid commands do not end up on the queue
    for command in ['hello', 12, -1, 4+2j, 0.234, 'INVALID']:
        job_q.validate_and_put(command)
        assert job_q.get_nonblocking() is None
    job_q.cleanup()
    del job_q


def test_named_pipe(tmp_path):
    """Test the FIFO named pipe
    """
    fifo_file = os.path.join(str(tmp_path), 'pipe')
    job_q = JobQueue(config.COMMANDS+config.MODES, fifo_file)

    # Put commands on the queue via name pipe
    for command in config.COMMANDS+config.MODES:
        print(subprocess.run('echo {} > {}'.format(command, fifo_file), shell=True, check=True))
        # Delay is to allow FIFO reading thread time to process each message and avoid rare errors
        time.sleep(0.2)
    # Check the commands got placed on queue
    for command in config.COMMANDS+config.MODES:
        assert job_q.get() == command
    job_q.cleanup()
    del job_q
