from keras.layers import Input, Dense, concatenate
from keras.layers import Activation, Conv2D, Flatten, Dropout, Reshape, Permute, Lambda
from keras.utils import multi_gpu_model
from keras.models import Sequential
from keras.models import Model
import keras.backend as K
import keras

resized_shape=(224,224,3)

def flatten_fo_final_size(x, size=512):
    x = Flatten()(x)
    x = Dense(512, activation='linear')(x)
    return x

def build_deepmind_model(x):
    x = Conv2D(32, (8, 8), strides=(4, 4), activation='relu', data_format='channels_first')(x)
    x = Conv2D(64, (4, 4), strides=(1, 1), activation='relu', data_format='channels_first')(x)
    x = Conv2D(64, (3, 3), strides=(1, 1), activation='relu', data_format='channels_first')(x)
    return x

def convert_tensors_to_model(x, num_actions, activation):
    x = Dense(num_actions, activation=activation)(x)
    model = Model

def build_resnet_model(x):
    x = Permute((2,3,1))(x)
    x = Reshape(target_shape=(32,225, 3))(x)
    x = keras.applications.ResNet50(\
        include_top=False, weights='imagenet',\
        input_shape=(32, 225, 3),\
        pooling=None, classes=3)(x)
    return x

def build_combined_model():
    input = Input(shape=(4, 30,180))
    x = flatten_fo_final_size(build_deepmind_model(input))
    x_prime = flatten_fo_final_size(build_resnet_model(input))
    merged = concatenate([x, x_prime])
    output = Dense(3, activation='linear')(merged)
    model = Model(inputs=input, outputs=output)
    return model

def build_paper_model(num_gpus=None):
    model = Sequential()
    model.add(
        Conv2D(32, (8, 8), strides=(4, 4), input_shape=(4, 30, 180), activation='relu', data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (4, 4), strides=(1, 1), data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3), strides=(1, 1), data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dense(3))
    model.add(Activation('linear'))

    if num_gpus is not None:
        model = multi_gpu_model(model)
        print('using' + str(num_gpus) + ' GPUs')

    return model