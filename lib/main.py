import logging
import sys
from stock_env import StockEnv
from rl.agents.dqn import DQNAgent
from rl.callbacks import FileLogger, ModelIntervalCheckpoint
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy, LinearAnnealedPolicy
from rl.memory import SequentialMemory
from keras.layers import Activation, Conv2D, Dense, Flatten, Dropout
from keras.models import Sequential
from keras.utils import multi_gpu_model
from keras.optimizers import Adam

if sys.platform == 'darwin':
    janet_path = '../../../Github/'
else:
    janet_path = '../../../zachfred62/'

sys.path.append(janet_path)
import Janet

def build_paper_model(num_gpus):
    model = Sequential()
    model.add(
        Conv2D(32, (8, 8), strides=(4, 4), input_shape=(4, 30, 180), activation='relu', data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (4, 4), strides=(1, 1), data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3), strides=(1, 1), data_format='channels_first'))
    model.add(Activation('relu'))
    model.add(Flatten())
    model.add(Dropout(0.5))
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(3))
    model.add(Activation('linear'))

    if not Janet.python_tools.is_mac():
        model = multi_gpu_model(model, gpus=num_gpus)
        print('using' + str(num_gpus) + ' GPUs')

    return model

if __name__ == "__main__":
    debug = True
    env_name = 'gaf_v1.5'
    mode = 'train'
    log_file = '../logs/debug.log'
    buy_count = 0
    sell_count = 0
    hold_count = 0
    num_gpus = 4

    #Janet.filesystem.mkdir_if_null('../logs/')
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(filename=log_file, level=level)

    env = StockEnv()
    model = build_paper_model(num_gpus)
    memory = SequentialMemory(limit=1000000, window_length=4)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                                  nb_steps=1000000)

    dqn = DQNAgent(model=model, nb_actions=3, policy=policy, memory=memory,
                   nb_steps_warmup=50000, gamma=.99, target_model_update=10000,
                   train_interval=4, delta_clip=1.)
    dqn.compile(Adam(lr=.00025), metrics=['mae'])

    if mode == 'train':
        weights_filename = 'dqn_{}_weights.h5f'.format(env_name)
        dqn.fit(env, nb_steps=100000, log_interval=10000)
        dqn.save_weights(weights_filename, overwrite=True)

    elif mode == 'test':
        weights_filename = '../data/weights/{}'.format(env_name)
        dqn.load_weights(weights_filename)
        dqn.test(env, nb_episodes=10, visualize=True)

    logging.info('Finished')
    print('buy count:', buy_count)
    print('sell count:', sell_count)
    print('hold count:', hold_count)