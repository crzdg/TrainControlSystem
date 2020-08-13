from Goldeneye.Recognizers.RecognizerCDNNConstants import RecognizersCDNNConstants as constants
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import Adam
from Goldeneye.Recognizers.Models.Model import Model


class GNet(Model):

    @staticmethod
    def load_model(weights_path=None):
        # create model
        model = Sequential()

        # add model layers
        model.add(Conv2D(16, kernel_size=3, input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, kernel_size=3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Dropout(rate=0.25))
        model.add(Flatten())

        model.add(Dense(len(constants.CATEGORIES)))
        model.add(Activation('softmax'))

        if weights_path:
            model.load_weights(weights_path)

        model.compile(loss='categorical_crossentropy',
                      optimizer=Adam(lr=1e-3),
                      metrics=['accuracy'])

        return model
