import datetime
import cv2
import numpy as np
import os
from tqdm import tqdm

from Goldeneye.ResultSaver.ResultSaverConstant import ResultSaverConstant
from Goldeneye.ResultSaver.SaveMode import SaveMode


class ResultSaver:

    def __init__(self, results, save_mode=SaveMode.CONTINUOUS):
        self.path = None
        self.save_mode = save_mode
        self.results = results
        self._create_run_dir()
        self._save_results()

    def _save_results(self):
        for result in tqdm(self.results):
            self._save_result(result[0], result[1], self.save_mode)

    def _create_run_dir(self):
        date = datetime.datetime.now()
        date_string = str(date.year) + \
                      str(date.month) + \
                      str(date.day) + "_" + \
                      str(date.hour) + \
                      str(date.minute) + str(date.second)
        self.path = ResultSaverConstant.SAVE_FOLDER + "run_{}".format(date_string)
        os.makedirs(self.path)

    def _save_result(self, classification_result, result_to_save, save_mode):
        if save_mode == SaveMode.CONTINUOUS:
            self._save_result_continuous(classification_result, result_to_save)
        elif save_mode == SaveMode.CLASSIFIED:
            self._save_result_classified_only(classification_result, result_to_save)
        elif save_mode == SaveMode.CONTINUOUS_DETAILED:
            self._save_result_continuous_detailed(classification_result, result_to_save)

    def _save_result_dictionary(self, classification_result, result_to_save):
        result_dict = {
            "frameNumber": result_to_save[3][1],
            "timeTaken": result_to_save[2],
            "qualifiedROIs": len(result_to_save[1]),
            "signalNumber": classification_result[0],
            "signalType": classification_result[1]
        }
        frame_string = self._get_frame_string(classification_result)
        f = open(self.path + "/" + frame_string + ".json", "w+")
        f.write(str(result_dict))

    def _save_result_continuous(self, classification_result, result_to_save):
        frame_string = self._get_frame_string(classification_result)
        image_path = self.path + "/" + frame_string + ".jpg"
        frame = np.frombuffer(result_to_save[3][0], np.uint8)
        frame = cv2.imdecode(frame, 1)
        cv2.imwrite(image_path, frame)

    def _save_rois(self, classification_result, result_to_save):
        frame_string = self._get_frame_string(classification_result)
        image = np.frombuffer(result_to_save[3][0], np.uint8)
        image = cv2.imdecode(image, 1)
        for i, roi in enumerate(result_to_save[1]):
            roi_path = self.path + "/" + frame_string + "_roi_{:02d}.jpg".format(i)
            x, y, w, h, label, confidence = roi[0], roi[1], roi[2], roi[3], roi[4], roi[5]
            length = int(w * 1.1)
            height = int(h * 1.1)
            point_1 = int(y + h // 2 - height // 2)
            point_2 = int(x + w // 2 - length // 2)

            region_of_interest = image[point_1:point_1 + height, point_2:point_2 + length]
            cv2.imwrite(roi_path, region_of_interest)

    def _get_frame_string(self, classification_result):
        return "frame_{:08d}".format(classification_result[2])

    def _save_result_classified_only(self, classification_result, result_to_save):
        if classification_result[0] is not -1:
            self._save_result_continuous(classification_result, result_to_save)
            self._save_result_dictionary(classification_result, result_to_save)
            self._save_rois(classification_result, result_to_save)

    def _save_result_continuous_detailed(self, classification_result, result_to_save):
        self._save_result_continuous(classification_result, result_to_save)
        self._save_result_dictionary(classification_result, result_to_save)
        self._save_rois(classification_result, result_to_save)
