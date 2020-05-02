import logging
import time
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logging.basicConfig(filename = 'gate.log', level = logging.DEBUG, format = LOG_FORMAT)
logger = logging.getLogger()


class Gate():
    current_state = 'unknown'
    
    def __init__(self):
        self.out_button = ''
        self.in_button = ''
        self.box_button = ''
        self.close()

    def close(self):
        self.current_state = 'closing'

    def open(self):
        self.current_state = 'opening'
        

def main_loop():

    


if __name__ == '__main__':
    logger.info('Starting smart gate')
    while 1:
        main_loop()
