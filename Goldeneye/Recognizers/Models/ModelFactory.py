from Goldeneye.Recognizers.Models.ModelType import ModelType
from Goldeneye.Recognizers.RecognizerCDNNConstants import RecognizersCDNNConstants as constants
from Goldeneye.Recognizers.Models.GNet import GNet
from Goldeneye.Recognizers.Models.GNetV2 import GNetV2


class ModelFactory:

    @staticmethod
    def get_model(model_type):
        if model_type == ModelType.GNet:
            model_name = 'CNN-gnet'
            model_path = "{}{}.h5".format(constants.MODEL_DIR, model_name)
            return GNet.load_model(model_path)

        elif model_type == ModelType.GNetV2:
            model_name = 'CNN-gnet-v2'
            model_path = "{}{}.h5".format(constants.MODEL_DIR, model_name)
            return GNetV2.load_model(model_path)

        elif model_type == ModelType.GNETV2Ultimate:
            model_name = 'CNN-gnet-deep-v2-ultimate'
            model_path = "{}{}.h5".format(constants.MODEL_DIR, model_name)
            return GNetV2.load_model(model_path)

        elif model_type == ModelType.GNetOld:
            model_name = 'number_detection_model'
            model_path = "{}{}.h5".format(constants.MODEL_DIR, model_name)
            return GNet.load_model(model_path)
