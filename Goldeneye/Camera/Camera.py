import logging
import threading
import time
from picamera import PiCamera


class Camera(threading.Thread):

    def __init__(self, stream_processor, x=640, y=480, fps=40, shutter_speed=0, iso=0, flip=(False, False)):
        threading.Thread.__init__(self)
        self.stream_processor = stream_processor
        self.xRes = x
        self.yRes = y
        self.framerate = fps
        self.shutter_speed = shutter_speed
        self.RUNNING = False
        self.camera = None
        self.output = None
        self.iso = iso
        self.flip = flip

        self.logger = None
        self.__create_logger()

        self.logger.info('### Initializing Camera ###')

        self._print_target_camera_parameters()
        self._initialize_camera()
        self._print_used_camera_parameters()

    def _print_used_camera_parameters(self):
        self.logger.info('Used Parameters for Camera!')
        self.logger.info('Dimension, x: {}, y: {}'.format(self.camera.resolution[0], self.camera.resolution[1]))
        self.logger.info('Frames per Second (FPS): {}'.format(self.camera.framerate))
        self.logger.info('Shutter Speed: {}'.format(self.camera.shutter_speed))
        self.logger.info('Camera using ISO-Value: {}'.format(self.camera.iso))
        self.logger.info('---------------------------------------------------')

    def _print_target_camera_parameters(self):
        self.logger.info('Target Parameters for Camera!')
        self.logger.info('Dimension, x: {}, y: {}'.format(self.xRes, self.yRes))
        self.logger.info('Frames per Second (FPS): {}'.format(self.framerate))
        self.logger.info('Shutter Speed: {}'.format(self.shutter_speed))
        self.logger.info('ISO-Value {}'.format(self.iso))
        self.logger.info('---------------------------------------------------')

    def _initialize_camera(self):
        self.camera = PiCamera()
        self.camera.vflip = self.flip[0]
        self.camera.hflip = self.flip[1]
        self.camera.resolution = (self.xRes, self.yRes)
        self.camera.framerate = self.framerate
        self.camera.shutter_speed = self.shutter_speed
        self.camera.iso = self.iso

    def _video_recording(self):
        self.camera.start_preview()
        time.sleep(2)
        self.start_time = time.time()
        self.camera.start_recording(self.stream_processor, format='mjpeg')
        while self.RUNNING:
            self.camera.wait_recording()
        self.stop_time = time.time()
        self.camera.stop_recording()
        # TODO - test
        self.camera.close()

    def _start_capture(self):
        self._video_recording()

    def set_output(self, output):
        self.output = output

    def run(self):
        self.RUNNING = True
        self._start_capture()

    def stop(self):
        self.RUNNING = False

    def camera_runtime(self):
        return self.stop_time - self.start_time

    def __create_logger(self):
        self.logger = logging.getLogger('Camera')
        #self.logger.setLevel(constants.LOG_LEVEL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #fh = logging.FileHandler(constants.LOG_FILE)
        #fh.setLevel(constants.LOG_LEVEL)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        #fh.setFormatter(formatter)
        self.logger.addHandler(ch)
        #self.logger.addHandler(fh)
