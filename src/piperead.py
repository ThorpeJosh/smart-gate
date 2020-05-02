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
    def __init__(self, valid_commands = []):
        super().__init__(maxsize=10)
        assert type(valid_commands) == type(list())
        self.valid_commands = valid_commands

    def val_and_put(self, message):
        message = message.strip().replace('\n', '')
        if message in self.valid_commands:
            self.put(message)
        else:
            print('Warning: {} is not a valid command for queue'.format(message))

        
VALID_COMMANDS = ['open', 'close', 'openp', 'closep', 'resume', 'status']    
JOB_Q = JobQueue(VALID_COMMANDS)

def read_fifo():
    while True:
        with open(NAMED_PIPE, 'r') as fifo:
            for job in fifo:
                JOB_Q.val_and_put(job)


threading.Thread(target = read_fifo).start()
while True:
    print('main loop')
    if not JOB_Q.empty():
        print(JOB_Q.get())
    time.sleep(1)




