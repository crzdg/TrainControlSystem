import datetime
import cv2
import numpy as np
import os
from tqdm import tqdm

from ResultSaver.ResultSaverConstant import ResultSaverConstant


class SimpleResultSaver:

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
        date_string = str(date.year) + \
                     str(date.month) + \
                     str(date.day) + "_" + \
                     str(date.hour) + \
                     str(date.minute) + str(date.second)
        self.path = ResultSaverConstant.SAVE_FOLDER + "run_simple_{}".format(date_string)
        os.makedirs(self.path)

    def _save_result(self, result):
        frame_string = "frame_{:08d}".format(result[1])
        image_path = self.path + "/" + frame_string + ".jpg"
        frame = np.frombuffer(result[0], np.uint8)
        frame = cv2.imdecode(frame, 1)
        cv2.imwrite(image_path, frame)



