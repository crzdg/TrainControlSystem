import time


class Recognizer:

    def classify(self, image):
        start_time = time.time()
        result_label, result_save = self.scan_image(image)
        result_save.append((time.time() - start_time) * 1000)
        return result_label, result_save

    def scan_image(self, image):
        raise NotImplementedError
