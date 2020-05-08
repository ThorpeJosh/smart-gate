"""Unit Tests for the job_queue module
"""
#import subprocess
#import time
from job_queue import JobQueue
import config

FIFO_FILE = '/tmp/fifo'

def test_queue():
    """Testing just the modified queue put and get methods
    """
    job_q = JobQueue(config.VALID_COMMANDS, FIFO_FILE)
    # Check queue is empty
    assert job_q.get_nonblocking() is None
    # Check valid commands work
    for command in config.VALID_COMMANDS:
        job_q.validate_and_put(command)
    for command in config.VALID_COMMANDS:
        assert job_q.get_nonblocking() == command
    # Check invalid commands do not end up on the queue
    for command in ['hello', 12, -1, 4+2j, 0.234, 'INVALID']:
        job_q.validate_and_put(command)
        assert job_q.get_nonblocking() is None
    job_q.cleanup()

#def test_named_pipe():
#    """Test the FIFO named pipe
#    """
#    job_q = JobQueue(config.VALID_COMMANDS, FIFO_FILE)
#
#    # Put commands on the queue via name pipe
#    for command in config.VALID_COMMANDS:
#        print(subprocess.run('echo {} > {}'.format(command, FIFO_FILE), shell=True, check=True))
#        # Delay is to allow FIFO reading thread time to process each message and avoid rare errors
#        time.sleep(0.2)
#    # Check the commands got placed on queue
#    for command in config.VALID_COMMANDS:
#        assert job_q.get() == command
#    job_q.cleanup()
