import logging
from multiprocessing import Process, Queue

from Goldeneye.Goldeneye.GoldeneyeMode import GoldeneyeMode
from Goldeneye.Recognizers.RecognizerType import RecognizerType
from Goldeneye.Recognizers.RecognizerCDNN import RecognizerCDNN
from Goldeneye.Recognizers.RecognizerRoundSignal import RecognizerRoundSignal


class ImageProcessor(Process):

    def __init__(self, pool_semaphore, result_output, buffer, mode):
        Process.__init__(self)
        self.terminated = False
        self.result_output = result_output
        self.pool_semaphore = pool_semaphore
        self.buffer = buffer

        self.recognizer_type = RecognizerType.RecognizerCDNN
        self.recognizer = None
        self.recognizer_cdnn = RecognizerCDNN()
        self.recognizer_round_signal = RecognizerRoundSignal()

        self.changing_queue = Queue()

        self.mode = mode

        self.logger = None
        self.__create_logger()

        self.start()

    def _process_frame(self, frame):
        try:
            self.change_recognizer()
            if self.recognizer_type is RecognizerType.RecognizerCDNN:
                result_label, result_save = self.recognizer_cdnn.classify(frame[0])
            elif self.recognizer_type is RecognizerType.RecognizerRoundSignal:
                result_label, result_save = self.recognizer_round_signal.classify(frame[0])
            result_label.append(frame[1])
            result_save.append(frame)
            result = [result_label, result_save]
            self.result_output.put(result)
        except:
            pass

    def _buffered_mode(self):
        frame = self.buffer.get()
        self._process_frame(frame)

    def _skipped_mode(self):
        frame = self.buffer.get()
        with self.pool_semaphore.get_lock():
            self.pool_semaphore.value -= 1
        self._process_frame(frame)
        with self.pool_semaphore.get_lock():
            self.pool_semaphore.value += 1

    def run(self):
        if self.recognizer_type is RecognizerType.RecognizerCDNN:
            self.recognizer_cdnn.load_model()

        while not self.terminated:
            if self.mode == GoldeneyeMode.BUFFERED:
                self._buffered_mode()

            elif self.mode == GoldeneyeMode.SKIPPED:
                self._skipped_mode()

    def change_recognizer(self):
        if not self.changing_queue.empty():
            result = self.changing_queue.get()
            if result == RecognizerType.RecognizerCDNN.value:
                self.recognizer_type = RecognizerType.RecognizerCDNN
            elif result == RecognizerType.RecognizerRoundSignal.value:
                self.recognizer_type = RecognizerType.RecognizerRoundSignal
            self.logger.info('Changed recognizers to: {}'.format(self.recognizer_type))

    def __create_logger(self):
        self.logger = logging.getLogger('ImageProcessor')
        #self.logger.setLevel(constants.LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #fh = logging.FileHandler(constants.LOG_FILE)
        #fh.setLevel(constants.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        #fh.setFormatter(formatter)
        self.logger.addHandler(ch)
        #self.logger.addHandler(fh)
