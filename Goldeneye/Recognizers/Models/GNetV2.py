from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import Adam
from Goldeneye.Recognizers.RecognizerCDNNConstants import RecognizersCDNNConstants as constants
from Goldeneye.Recognizers.Models.Model import Model


class GNetV2(Model):

    @staticmethod
    def load_model(weights_path=None):
        # create model
        model = Sequential()

        # add model layers
        # 1. Layer
        model.add(Conv2D(filters=16, kernel_size=3, strides=1, padding='same',
                         input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION),
                         activation='relu'))
        model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 2. Layer
        model.add(Conv2D(filters=32, kernel_size=3, strides=1, padding='same', activation='relu'))
        model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 3. Layer
        model.add(Conv2D(filters=64, kernel_size=3, strides=1, padding='same', activation='relu'))
        model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 4. Layer
        model.add(Dropout(rate=0.25))
        model.add(Flatten())

        # 5. Layer
        model.add(Dense(len(constants.CATEGORIES), activation='softmax', name='preds'))

        # load weights if path is given
        if weights_path:
            model.load_weights(weights_path)

        model.compile(loss='categorical_crossentropy',
                      optimizer=Adam(lr=1e-3),
                      metrics=['accuracy'])

        return model
