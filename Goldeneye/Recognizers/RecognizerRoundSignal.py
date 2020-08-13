import cv2
import numpy as np
from Goldeneye.Recognizers.RecognizerRoundSignalConstants import RecognizersRoundSignalConstants as constants
from Goldeneye.Recognizers.Recognizer import Recognizer


class RecognizerRoundSignal(Recognizer):

    def scan_image(self, image):
        label = -1
        signal_type = 2
        roi_coordinates = []

        contour_shape = None
        image_preprocessed = self.__preprocess_image(image)
        contours, hierarchy = cv2.findContours(image_preprocessed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if 125 < cv2.contourArea(cnt) < 1200:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

                if len(approx) >= 3:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if contour_shape is not None:
                        # calculate contour for searching upper or lower contour
                        searching_contour = self.__calculate_searching_contour(contour_shape, y)
                        # calculate center from contour
                        center_x, center_y = self.__calculate_center(h, w, x, y)
                        # check if center of contour is in searching contour
                        dist_center = cv2.pointPolygonTest(searching_contour, (center_x, center_y), False)
                        # 0: point is on contour, 1: point is in contour
                        if dist_center > -1:
                            label = 99
                            # create bounding box
                            cnt_x, cnt_y, cnt_w, cnt_h = contour_shape
                            if cnt_y < y:
                                roi_coordinates.append([cnt_x, cnt_y, x - cnt_x + w, y - cnt_y + h])
                            else:
                                roi_coordinates.append([x, y, cnt_x - x + cnt_w, cnt_y - y + cnt_h])
                    else:
                        contour_shape = (x, y, w, h)

        return [label, signal_type], [image_preprocessed, roi_coordinates]

    def __calculate_searching_contour(self, contour_shape, y):
        cnt_x, cnt_y, cnt_w, cnt_h = contour_shape
        if cnt_y < y:
            point_1_x = [cnt_x, cnt_y]
            point_1_y = [cnt_x + cnt_w, cnt_y]
            point_2_x = [cnt_x, cnt_y + (cnt_h * 3)]
            point_2_y = [cnt_x + cnt_w, cnt_y + (cnt_h * 3)]
        else:
            point_1_x = [cnt_x, cnt_y - (cnt_h * 3)]
            point_1_y = [cnt_x + cnt_w, cnt_y - (cnt_h * 3)]
            point_2_x = [cnt_x, cnt_y + cnt_h]
            point_2_y = [cnt_x + cnt_w, cnt_y + cnt_h]

        searching_contour = [point_1_x, point_1_y, point_2_y, point_2_x]
        searching_contour = np.array(searching_contour).reshape((-1, 1, 2)).astype(np.int32)

        return searching_contour

    def __calculate_center(self, h, w, x, y):
        length = int(w)
        height = int(h)

        point_1_x = int(x + w // 2 - length // 2)
        point_1_y = int(y + h // 2 - height // 2)

        center_x = point_1_x + int(length / 2)
        center_y = point_1_y + int(height / 2)

        return center_x, center_y

    def __preprocess_image(self, image):
        frame = np.frombuffer(image, np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_cropped = frame[0:120, :, :]
        frame_hsv = cv2.cvtColor(frame_cropped, cv2.COLOR_RGB2HSV)
        frame_mask = cv2.inRange(frame_hsv, constants.LOWER_BLUE, constants.UPPER_BLUE)

        return frame_mask
