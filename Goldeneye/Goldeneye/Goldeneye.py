import logging
import time

from Goldeneye.Camera.Camera import Camera
from Goldeneye.Goldeneye.GoldeneyeMode import GoldeneyeMode
from Goldeneye.Goldeneye.MJPEGStreamProcessor import MJPEGStreamProcessor
from multiprocessing import Queue, Value
from Goldeneye.Goldeneye.GoldeneyeConfiguration import GoldeneyeConfiguration as CONFIG
from Goldeneye.ImageProcessor.ImageProcessor import ImageProcessor
from Goldeneye.Recognizers.RecognizerType import RecognizerType


class Goldeneye:

    def __init__(self):
        self.buffer = Queue()
        self.result = Queue()
        self.pool_semaphore = Value('i', CONFIG.number_of_image_processors)
        self.mode = CONFIG.mode
        self.start_time = None
        self.stop_time = None
        self.stream_processor = None
        self.camera = None
        self.pool = None

        self.logger = None
        self.__create_logger()

        self.logger.info('### Creating Goldeneye ###')

    def __init_goldeneye(self):
        self.logger.info('### Initializing Goldeneye ###')
        self.pool = [ImageProcessor(self.pool_semaphore, self.result, self.buffer, self.mode)
                     for _ in range(CONFIG.number_of_image_processors)]
        self.stream_processor = MJPEGStreamProcessor(self.pool_semaphore, self.buffer, self.mode)
        self.camera = Camera(self.stream_processor,
                             fps=CONFIG.fps,
                             x=CONFIG.x_resolution,
                             y=CONFIG.y_resolution,
                             shutter_speed=CONFIG.shutter_speed,
                             iso=CONFIG.iso,
                             flip=CONFIG.flip)

    def prepare_goldeneye(self):
        self.__init_goldeneye()

    def start(self):
        self.logger.info('Starting Goldeneye!')

        if self.camera is None:
            self.__init_goldeneye()

        if self.mode == GoldeneyeMode.SKIPPED:
            self.logger.info('Starting in Mode: Skipped')

        if self.mode == GoldeneyeMode.BUFFERED:
            self.logger.info('Starting in Mode: Buffered')

        self.logger.info('Start Recording!')
        self.camera.start()
        self.start_time = time.time()
        self.logger.info('Goldeneye started! Results can be read from Queue!')

    def change_recognizers(self, recognizer_type):
        for image_processor in self.pool:
            if recognizer_type is RecognizerType.RecognizerCDNN:
                image_processor.changing_queue.put(RecognizerType.RecognizerCDNN.value)
            elif recognizer_type is RecognizerType.RecognizerRoundSignal:
                image_processor.changing_queue.put(RecognizerType.RecognizerRoundSignal.value)

    def stop(self):
        self.logger.info('Stopping Goldeneye!')
        self.logger.info('Stop Recording!')
        self.camera.stop()
        self.logger.info('Recording stopped!')
        self.logger.info('Waiting till Buffer is processed!')
        while self.buffer.qsize() > 0:
            time.sleep(0.05)
        self.logger.info('Buffer cleared!')
        self.stop_time = time.time()
        self.logger.info('Joining Processes!')
        for process in self.pool:
            process.terminated = True
        self.logger.info('Goldeneye stopped!')

    def stats(self):
        return [self.stream_processor.images_captured,
                self.stream_processor.images_processed,
                self.camera.camera_runtime(),
                self.stop_time - self.start_time,
                self.stream_processor.images_captured / self.camera.camera_runtime(),
                self.stream_processor.images_processed / (self.stop_time - self.start_time)]

    def terminate(self):
        self.logger.info('Terminating Goldeneye!')
        self.camera.join()
        for process in self.pool:
            process.terminate()
            process.join()
        self.logger.info('Goldeneye terminated!')

    def __create_logger(self):
        self.logger = logging.getLogger('Goldeneye')
        #self.logger.setLevel(constants.LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #fh = logging.FileHandler(constants.LOG_FILE)
        #fh.setLevel(constants.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        #fh.setFormatter(formatter)
        self.logger.addHandler(ch)
        #self.logger.addHandler(fh)
