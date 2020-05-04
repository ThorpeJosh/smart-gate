"""Testing the job queue and named pipe (FIFO) system
"""
import time
import os
import threading
import queue

NAMED_PIPE = '/tmp/fifo'
try:
    os.remove(NAMED_PIPE)
except FileExistsError:
    pass
finally:
    os.mkfifo(NAMED_PIPE)

class JobQueue(queue.Queue):
    """Queue that holds commands for the gate to execute.
    Inheritated from the python queue class with the addition of a method that ensures the
    commands put on the queue are valid
    """
    def __init__(self, valid_commands=None):
        super().__init__(maxsize=10)
        assert isinstance(valid_commands, list)
        self.valid_commands = valid_commands

    def val_and_put(self, message):
        """Validates message is a valid command then puts it on the queue
        """
        message = message.strip().replace('\n', '')
        if message in self.valid_commands:
            self.put(message)
        else:
            print('Warning: {} is not a valid command for queue'.format(message))

VALID_COMMANDS = ['open', 'close', 'openp', 'closep', 'resume', 'status']
JOB_Q = JobQueue(VALID_COMMANDS)

def read_fifo():
    """ Indefinite FIFO pipe reading
    Open FIFO pipe and reads when the tunnel has a sender,
    it then closes and reopens to avoid exessive cpu usage.

    Note that reading a pipe is blocking so this function must be called in a seperate thread,
    hence the infinite loop.
    """
    while True:
        with open(NAMED_PIPE, 'r') as fifo:
            for job in fifo:
                JOB_Q.val_and_put(job)


threading.Thread(target=read_fifo).start()
while True:
    print('main loop')
    if not JOB_Q.empty():
        print(JOB_Q.get())
    time.sleep(1)
