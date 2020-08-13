import logging
from multiprocessing import Queue
from threading import Thread


class SignalTrackingSystem(Thread):

    def __init__(self, queue: Queue()):
        Thread.__init__(self)
        self.eye_result_queue = queue
        self.confirmed_queue = Queue()
        self.last_seen = [-1, -1, -1]
        self.last_seen_set = False
        self.last_valid_confirmation = [-1, -1]
        self.counter = 0
        self.strikes = 0
        self.is_tracking = False
        self.terminated = True
        self.logger = None
        self.__create_logger()

    def run(self):
        self.terminated = False
        while not self.terminated:
            result = self.eye_result_queue.get()
            if self.is_tracking:
                confirmation = self.confirm(result[0])
                if confirmation[0] is not -1:
                    self.confirmed_queue.put(confirmation)

    def start_tracking(self):
        self.logger.info('Starting')
        self.__clear_queue()
        self.__reset()
        self.is_tracking = True

    def stop_tracking(self):
        self.logger.info('Stopping')
        self.__clear_queue()
        self.__reset()
        self.is_tracking = False

    def terminate(self):
        self.logger.info('Terminating')
        self.terminated = True
        self.is_tracking = False

    def confirm(self, result):
        label = result[0]
        signal_type = result[1]
        frame_number = result[2]

        last_seen_label = self.last_seen[0]
        last_seen_type = self.last_seen[1]
        last_seen_frame = self.last_seen[2]

        if label is not -1:
            self.logger.debug('Confirming result {}'.format(result))
            self.logger.debug('Current last-seen is {}'.format(self.last_seen))

        if self.last_seen_set:
            if signal_type is last_seen_type and label is last_seen_label:
                if (frame_number > (last_seen_frame - 3)) and (frame_number < (last_seen_frame + 3)):
                    self.logger.debug('Result is valid counting result.')
                    self.last_seen[2] = frame_number
                    self.counter += 1
                    if self.counter >= 1:
                        return self.__clear()
            else:
                self.strikes += 1
                if self.strikes > 1:
                    self.logger.debug('Strike Max reached! Clearing!')
                    return self.__clear()
            return [-1, -1]

        if label is -1:
            return [-1, -1]

        # check if last seen frame is empty (-1) -> new number detected
        if last_seen_frame is -1:
            self.logger.debug('New Number detected.')
            self.last_seen_set = True
            self.last_seen[0] = label
            self.last_seen[1] = signal_type
            self.last_seen[2] = frame_number

        return [-1, -1]

    def __clear(self):
        result = [-1, -1]
        self.logger.debug('Counter {}'.format(self.counter))
        if self.counter >= 1:
            result = [self.last_seen[0], self.last_seen[1]]
            if result[0] is self.last_valid_confirmation[0] and result[1] is self.last_valid_confirmation[1]:
                self.logger.info('Valid Result {} is same as last valid {}'.format(result, self.last_valid_confirmation))
                result = [-1, -1]
            else:
                self.logger.info('Valid Signal {} found'.format(result))
                self.last_valid_confirmation = result
        self.last_seen = [-1, -1, -1]
        self.last_seen_set = False
        self.counter = 0
        self.strikes = 0
        return result

    def __clear_queue(self):
        self.confirmed_queue = Queue()

    def __reset(self):
        self.last_seen = [-1, -1, -1]
        self.last_seen_set = False
        self.last_valid_confirmation = [-1, -1]
        self.counter = 0
        self.strikes = 0

    def __create_logger(self):
        self.logger = logging.getLogger('SignalTrackingSystem')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #fh = logging.FileHandler(constants.LOG_FILE)
        #fh.setLevel(constants.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        #fh.setFormatter(formatter)
        self.logger.addHandler(ch)
        #self.logger.addHandler(fh)
