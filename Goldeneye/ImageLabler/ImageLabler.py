import cv2

import numpy as np

class ImageLabler:

    @staticmethod
    def label_image(result):
        classification_result = result[0]
        result_to_save = result[1]
        result_dict = {
            "frameNumber": result_to_save[3][1],
            "timeTaken": result_to_save[2],
            "qualifiedROIs": len(result_to_save[1]),
            "signalNumber": classification_result[0],
            "signalType": classification_result[1]
        }
        img = result_to_save[3][0]
        frame = np.frombuffer(img, np.uint8)
        frame = cv2.imdecode(frame, 1)

        image_height, image_width, _ = frame.shape

        if image_height == 240 and image_width == 320:
            info_box_width = 270
            info_box_height = 100
            text_steps = 10
            font_size = 0.5
        if image_height == 480 and image_width == 640:
            info_box_width = 540
            info_box_height = 200
            text_steps = 20
            font_size = 1


        frame[:info_box_height, info_box_width:image_width, :] = 255
        label = "Fc:" + str(result[2][1])
        cv2.putText(frame, label, (info_box_width + 10, text_steps), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "F#:" + str(result_dict["frameNumber"])
        cv2.putText(frame, label, (info_box_width + 10, text_steps*2), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "{:.2f}ms".format(result_dict["timeTaken"])
        cv2.putText(frame, label, (info_box_width + 10, text_steps*3), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "Styp:" + str(result_dict["signalType"])
        cv2.putText(frame, label, (info_box_width + 10, text_steps*4), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "S#:" + str(result_dict["signalNumber"])
        cv2.putText(frame, label, (info_box_width + 10, text_steps*5), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "t:{:.2f}".format(result[2][0])
        cv2.putText(frame, label, (info_box_width + 10, text_steps*6), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "C:{:.2f}".format((result[2][1] / result[2][0]))
        cv2.putText(frame, label, (info_box_width + 10, text_steps*7), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        label = "P:{:.2f}".format((result[2][2] / result[2][0]))
        cv2.putText(frame, label, (info_box_width + 10, text_steps*8), cv2.FONT_HERSHEY_PLAIN, font_size, (0, 0, 0), 1, cv2.LINE_AA)
        for roi in result[1][1]:
            label = "L:{} C:{:.1f}".format(roi[4], roi[5])
            if roi[4] != -1 and roi[5] > 0.95:
                cv2.rectangle(frame, (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), (0, 255, 0), 1)
                cv2.putText(frame, label, (roi[0] + (roi[2] + 10), roi[1]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1,
                            cv2.LINE_AA)
            else:
                cv2.rectangle(frame, (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), (0, 0, 255), 1)
                cv2.putText(frame, label, (roi[0] + (roi[2] + 10), roi[1]), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1,
                            cv2.LINE_AA)
        _, byte_frame = cv2.imencode('.jpg', frame)
        return byte_frame.tostring()

