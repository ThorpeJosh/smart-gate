"""Module for the job queue and named pipe (FIFO) system
"""
import os
import threading
import queue

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
        threading.Thread(target=self.read_fifo, daemon=True).start()

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
            print('Warning: {} is not a valid command for queue'.format(message))

    def get_nonblocking(self):
        """Non-blocking version of the parent classes get() method
        """
        if self.empty():
            return None
        return self.get()

    def cleanup(self):
        """Cleanup method to delete the named pipe
        """
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
                    self.validate_and_put(job)