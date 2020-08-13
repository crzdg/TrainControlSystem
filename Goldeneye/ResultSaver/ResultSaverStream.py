import cv2
import datetime
import numpy as np
import os
from tqdm import tqdm
from Goldeneye.ImageLabler.ImageLabler import ImageLabler
from Goldeneye.ResultSaver.ResultSaverConstant import ResultSaverConstant


class ResultSaverWebstream:

    def __init__(self, results):
        self.path = None
        self.results = results
        self._create_run_dir()
        self._save_results()

    def _save_results(self):
        for result in tqdm(self.results):
            self._save_result(result)

    def _create_run_dir(self):
        date = datetime.datetime.now()
        dateString = str(date.year) + \
                     str(date.month) + \
                     str(date.day) + "_" + \
                     str(date.hour) + \
                     str(date.minute) + str(date.second)
        self.path = ResultSaverConstant.SAVE_FOLDER + "run_webstream_{}".format(dateString)
        os.makedirs(self.path)

    def _save_result(self, result):
        img = ImageLabler.label_image(result)
        frame = np.frombuffer(img, np.uint8)
        frame = cv2.imdecode(frame, 1)
        frame_string = "frame_web_{:08d}".format(result[0][2])
        image_path = self.path + "/" + frame_string + ".jpg"
        cv2.imwrite(image_path, frame)
