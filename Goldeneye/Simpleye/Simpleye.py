import time
from Camera.Camera import Camera
from Goldeneye.GoldeneyeMode import GoldeneyeMode
from Goldeneye.MJPEGStreamProcessor import MJPEGStreamProcessor
from multiprocessing import Queue, Value


class Simpleye:

    def __init__(self, fps=40, x=320, y=240, shutter_speed=750, iso=0):
        print(" ### Creating Simpleye ###")
        self.buffer = Queue()
        self.pool_semaphore = Value('i', 1)
        self.stream_processor = None
        self.camera = None
        self.start_time = None
        self.stop_time = None
        self.mode = GoldeneyeMode.BUFFERED
        self.camera_settings = {"fps": fps,
                                "x": x,
                                "y": y,
                                "shutter_speed": shutter_speed,
                                "iso": iso}

    def __init_simpleye(self):
        print(" ### Initializing Simpleye ###")
        self.stream_processor = MJPEGStreamProcessor(self.pool_semaphore, self.buffer, self.mode)
        self.camera = Camera(self.stream_processor,
                             fps=self.camera_settings["fps"],
                             x=self.camera_settings["x"],
                             y=self.camera_settings["y"],
                             shutter_speed=self.camera_settings["shutter_speed"],
                             iso=self.camera_settings["iso"])

    def start(self):
        print("Starting Simpleye!")

        if self.camera is None:
            self.__init_simpleye()

        if self.mode == "skipped":
            print("Starting in Mode: 'Skipped'")

        if self.mode == "buffered":
            print("Starting in Mode: 'Buffered'")

        print("Start Recording!")
        self.camera.start()
        self.start_time = time.time()
        print("Simpleye started! Results can be read from Queue!")

    def stop(self):
        print("Stopping Simpleye!")
        print("Stop Recording!")
        self.camera.stop()
        print("Recording stopped!")
        self.stop_time = time.time()
        print("Joining Processes!")
        print("Simpleye stopped!")

    def stats(self):
        return [self.stream_processor.images_captured,
                self.stream_processor.images_processed,
                self.camera.camera_runtime(),
                self.stop_time - self.start_time,
                self.stream_processor.images_captured / self.camera.camera_runtime(),
                self.stream_processor.images_processed / (self.stop_time - self.start_time)]

    def terminate(self):
        print("Terminating Simpleye!")
        self.camera.join()
        print("Simpleye terminated!")













