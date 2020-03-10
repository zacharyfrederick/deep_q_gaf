import logging
from stock_env import StockEnv
from rl.agents.dqn import DQNAgent
from rl.callbacks import FileLogger, ModelIntervalCheckpoint
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy, LinearAnnealedPolicy
from rl.memory import SequentialMemory
from keras.layers import (Activation, Conv2D, Dense, Flatten)
from keras.models import Sequential
from keras.utils import multi_gpu_model
from keras.optimizers import Adam

import sys
sys.path.append('../..Github/')

def build_paper_model():
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

    if Janet.python_tools.is_mac():
        model = multi_gpu_model(model, gpus=2)

    return model

if __name__ == "__main__":
    debug = True
    env_name = 'gaf_v1.5'
    mode = 'train'
    log_file = '../logs/debug.log'
    buy_count = 0;
    sell_count = 0;
    hold_count = 0;

    #Janet.filesystem.mkdir_if_null('../logs/')
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(filename=log_file, level=level)

    env = StockEnv()
    model = build_paper_model()
    memory = SequentialMemory(limit=1000000, window_length=4)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                                  nb_steps=1000000)

    dqn = DQNAgent(model=model, nb_actions=3, policy=policy, memory=memory,
                   nb_steps_warmup=50000, gamma=.99, target_model_update=10000,
                   train_interval=4, delta_clip=1.)
    dqn.compile(Adam(lr=.00025), metrics=['mae'])

    if mode == 'train':
        weights_filename = 'dqn_{}_weights.h5f'.format(env_name)
        checkpoint_weights_filename = 'dqn_' + env_name + '_weights_{step}.h5f'
        callbacks = [ModelIntervalCheckpoint(checkpoint_weights_filename, interval=250000)]

        dqn.fit(env, callbacks=callbacks, nb_steps=100000, log_interval=10000)
        dqn.save_weights(weights_filename, overwrite=True)

    elif mode == 'test':
        weights_filename = '../data/weights/{}'.format(env_name)

        dqn.load_weights(weights_filename)
        dqn.test(env, nb_episodes=10, visualize=True)

    logging.info.info('Finished')
    print('buy count:', buy_count)
    print('sell count:', sell_count)
    print('hold count:', hold_count)