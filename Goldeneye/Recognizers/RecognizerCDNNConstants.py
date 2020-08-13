from Goldeneye.Recognizers.Models.ModelType import ModelType


class RecognizersCDNNConstants:
    CATEGORIES = ["-1", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    MODEL_DIR = "/home/pi/pren/"
    MODEL_TYPE = ModelType.GNETV2Ultimate

    IMG_SIZE = 28
    USE_GRAY_SCALE = True
    DIMENSION = 1

    CONFIDENCE = 0.95
