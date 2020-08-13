import cv2
import numpy as np
import tensorflow as tf
from Goldeneye.Recognizers.RecognizerCDNNConstants import RecognizersCDNNConstants as constants
from Goldeneye.Recognizers.Constants.RecognizerConstants import RecognizerConstants
from Goldeneye.Recognizers.Constants.RecognizerConstants320240 import RecognizerConstants320240
from Goldeneye.Recognizers.Constants.RecognizerConstants640480 import RecognizerConstants640480
from Goldeneye.Recognizers.Recognizer import Recognizer
from Goldeneye.Recognizers.Models.ModelFactory import ModelFactory
from keras import backend as K

tf.logging.set_verbosity(tf.logging.ERROR)


class RecognizerCDNN(Recognizer):
    CLASS_CONSTANTS = RecognizerConstants

    def __init__(self):
        self.session = None
        self.graph = None
        self.model = None
        self.CONSTANTS = None

    def load_model(self):
        self.model = ModelFactory.get_model(constants.MODEL_TYPE)
        for _ in range(5):
            self.model.predict(self.__preprocess_roi(np.zeros((constants.IMG_SIZE, constants.IMG_SIZE), np.uint8)))
        self.session = K.get_session()
        self.graph = tf.get_default_graph()
        self.session.as_default()
        self.graph.as_default()

    def __preprocess_roi(self, image_array):
        resized_image_array = cv2.resize(image_array, (constants.IMG_SIZE, constants.IMG_SIZE))
        reshaped_image = resized_image_array.reshape(-1, constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)

        return reshaped_image

    def scan_image(self, image):
        # decode the image from bytes to np array and convert it to gray scale
        frame = np.frombuffer(image, np.uint8)
        if constants.USE_GRAY_SCALE:
            frame = cv2.imdecode(frame, cv2.IMREAD_GRAYSCALE)
            image_array = frame
        else:
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            image_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if self.CONSTANTS is None:
            self.__set_constants(image_array)
        image_preprocessed, regions_of_interest, roi_coordinates = self.get_regions_of_interest(image_array)

        label = -1
        signal_type = 0

        for index, roi_arr in enumerate(regions_of_interest):
            roi = roi_arr[0]
            roi_type = roi_arr[1]
            roi_processed = self.__preprocess_roi(roi)
            prediction = self.model.predict(roi_processed)[0]
            i = prediction.argmax(axis=0)
            label_i = constants.CATEGORIES[i]
            confidence = prediction[i]
            roi_coordinates[index].append(int(label_i))
            roi_coordinates[index].append(confidence)
            if confidence > constants.CONFIDENCE and int(label_i) != -1:
                label = int(label_i)
                signal_type = roi_type

        if label == -1:
            signal_type = -1
        return [label, signal_type], [image_preprocessed, roi_coordinates]

    def __set_constants(self, image):
        if constants.USE_GRAY_SCALE:
            image_height, image_width = image.shape
        else:
            image_height, image_width, _ = image.shape

        if image_height == 240 and image_width == 320:
            self.CONSTANTS = RecognizerConstants320240
        elif image_height == 480 and image_width == 640:
            self.CONSTANTS = RecognizerConstants640480

    def get_regions_of_interest(self, image):
        regions_of_interest = []  # 0: roi, 1: type
        preprocessed_image = None
        roi_coordinates = []
        cropped_images = self.__crop(image)
        for index, cropped in enumerate(cropped_images):
            preprocessed_image = self.__preprocess(cropped)
            threshold_image = self.__threshold(preprocessed_image)
            contours = self.__find_contours(threshold_image)
            contours = self.__check_countours(contours)
            rois, rois_coords = self.__crop_regions_of_interest(cropped, contours)

            for roi_cord in rois_coords:
                if index is 0:
                    roi_cord[1] = roi_cord[1] + self.CONSTANTS.CROP_INFO_HEIGHT_START
                elif index is 1:
                    roi_cord[1] = roi_cord[1] + self.CONSTANTS.CROP_STOP_HEIGHT_START
                roi_coordinates.append(roi_cord)

            for roi in rois:
                roi_arr = [roi, index]
                regions_of_interest.append(roi_arr)

        return preprocessed_image, regions_of_interest, roi_coordinates

    def __crop(self, image):
        info_start = self.CONSTANTS.CROP_INFO_HEIGHT_START
        info_end = self.CONSTANTS.CROP_INFO_HEIGHT_END

        stop_start = self.CONSTANTS.CROP_STOP_HEIGHT_START
        stop_end = self.CONSTANTS.CROP_STOP_HEIGHT_END

        width_start = self.CONSTANTS.CROP_WIDTH_START
        width_end = self.CONSTANTS.CROP_WIDTH_END

        if constants.USE_GRAY_SCALE:
            image_info = image[info_start:info_end, width_start:width_end]
            image_stop = image[stop_start:stop_end, width_start:width_end]
        else:
            image_info = image[info_start:info_end, width_start:width_end, :]
            image_stop = image[stop_start:stop_end, width_start:width_end, :]

        return [image_info, image_stop]

    def __detect_edges(self, channel):
        sobel_x = cv2.Sobel(channel, cv2.CV_16S, 1, 0)
        sobel_y = cv2.Sobel(channel, cv2.CV_16S, 0, 1)
        sobel = np.hypot(sobel_x, sobel_y)
        sobel[sobel > 255] = 255

        return sobel

    def __preprocess(self, image):
        if constants.USE_GRAY_SCALE:
            # create gradient image from gray scale image
            image = self.__detect_edges(image)
        else:
            # create gradient image from all 3 color channels
            # calculate gradient for channels and put it back together
            image = np.max(np.array(
                [self.__detect_edges(image[:, :, 0]),
                 self.__detect_edges(image[:, :, 1]),
                 self.__detect_edges(image[:, :, 2])]), axis=0)
        # calculate mean of the image
        mean = np.mean(image)
        # everything that is below the mean of the image will be set to black
        image[image <= mean + self.CONSTANTS.ADDITION_MEAN] = 0
        # convert the image back to a numpy array
        image = np.asarray(image, np.uint8)

        return image

    def __threshold(self, image):
        image = cv2.inRange(image, self.CONSTANTS.THRESHOLD_LOWER, self.CONSTANTS.THRESHOLD_UPPER)

        return image

    def __find_contours(self, image):
        image_height, image_width = image.shape
        contours, hierarchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        filtered_contours = []
        for i, cnt in enumerate(contours):
            if (hierarchy[0][i][3] != -1 and hierarchy[0][i][2] == -1) or \
                    (hierarchy[0][i][3] == -1 and hierarchy[0][i][2] > 0) or \
                    (hierarchy[0][i][3] > 0 and hierarchy[0][i][2] > 0):
                if self.CONSTANTS.AREA_SIZE_MIN < cv2.contourArea(cnt) < self.CONSTANTS.AREA_SIZE_MAX:
                    x, y, w, h = cv2.boundingRect(cnt)
                    if w < self.CONSTANTS.WIDTH_MAX and h < self.CONSTANTS.HEIGHT_MAX:
                        if self.CONSTANTS.WIDTH_HEIGHT_RATIO_MIN < w / h < self.CONSTANTS.WIDTH_HEIGHT_RATIO_MAX:
                            length = int(w)
                            height = int(h)
                            point_1_x = int(x + w // 2 - length // 2)
                            point_1_y = int(y + h // 2 - height // 2)
                            point_2_x = point_1_x + length
                            point_2_y = point_1_y + height

                            if point_1_y > 0 and point_1_x > 0 and point_2_y < image_height and point_2_x < image_width:
                                region_of_interest = image[point_1_y:point_2_y, point_1_x:point_2_x]
                                if self.__qualifies_as_number(region_of_interest):
                                    filtered_contours.append(cnt)
        return filtered_contours

    def __qualifies_as_number(self, region_of_interest):
        roi_h, roi_w = region_of_interest.shape
        anz_pixel = roi_h * roi_w
        anz_pixel_white = np.sum(region_of_interest == 255)
        anz_pixel_black = anz_pixel - anz_pixel_white
        anz_pixel_black_ratio = (anz_pixel_black / anz_pixel) * 100

        if anz_pixel_black_ratio <= self.CONSTANTS.PIXEL_RATIO_MIN:
            qualifies_as_number = False
        elif anz_pixel_black_ratio >= self.CONSTANTS.PIXEL_RATIO_MAX:
            qualifies_as_number = False
        else:
            qualifies_as_number = True

        return qualifies_as_number

    def __check_countours(self, contours):
        contours_removed = []
        for i_cnt, cnt in enumerate(contours):
            for i_cnt2, cnt2 in enumerate(contours):
                if cnt is not cnt2 and cnt not in contours_removed and cnt2 not in contours_removed:
                    x, y, w, h = cv2.boundingRect(cnt2)
                    length = int(w)
                    height = int(h)

                    point_1_x = int(x + w // 2 - length // 2)
                    point_1_y = int(y + h // 2 - height // 2)

                    center_x = point_1_x + int(length / 2)
                    center_y = point_1_y + int(height / 2)

                    dist_center = cv2.pointPolygonTest(cnt, (center_x, center_y), False)

                    if dist_center > -1:
                        if cv2.contourArea(cnt) > cv2.contourArea(cnt2):
                            del contours[i_cnt2]
                            contours_removed.append(cnt2)
                        else:
                            del contours[i_cnt]
                            contours_removed.append(cnt)

        return contours

    def __crop_regions_of_interest(self, image, contours):
        regions_of_interest = []
        roi_coordinates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi_coordinates.append([x, y, w, h])

            length = int(w * 1.1)
            height = int(h * 1.1)

            point_1_x = int(x + w // 2 - length // 2)
            point_1_y = int(y + h // 2 - height // 2)
            point_2_x = point_1_x + length
            point_2_y = point_1_y + height

            if point_1_x < 0:
                point_1_x = 0
            if point_1_y < 0:
                point_1_y = 0
            if point_2_x < 0:
                point_2_x = 0
            if point_2_y < 0:
                point_2_y = 0

            region_of_interest = image[point_1_y:point_2_y, point_1_x:point_2_x]
            regions_of_interest.append(region_of_interest)

        return regions_of_interest, roi_coordinates
