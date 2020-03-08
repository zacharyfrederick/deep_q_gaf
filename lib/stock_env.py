import argparse
import enum
import locale
import random
import sys
import warnings
from datetime import datetime

import gym
import gym.spaces
import keras.backend as K
import numpy as np
import pandas as pd
from colored import attr, bg, fg
from keras.layers import (Activation, Conv2D, Convolution2D, Dense, Flatten,
                          Input, Permute)
from keras.models import Sequential
from keras.optimizers import Adam
from PIL import Image
from rl.agents.dqn import DQNAgent
from rl.callbacks import FileLogger, ModelIntervalCheckpoint
from rl.core import Processor
from rl.memory import SequentialMemory
from rl.policy import BoltzmannQPolicy, EpsGreedyQPolicy, LinearAnnealedPolicy

import actions
from data_manager import DataManager
from position_manager import Position, PositionManager, PositionQueue
from clock import Clock

warnings.simplefilter(action='ignore', category=FutureWarning)

buy_count = 0;
sell_count = 0;
hold_count = 0;

class StockEnv(gym.Env):
    def __init__(self):
        self.env_name = 'gaf-environment-v1.0'
        self.REWARD_MULT = 100000
        self.cash = 100000
        self.current_action = None
        self.previous_action = None
        self.clock = Clock()
        self.dm = DataManager(self.clock)
        self.pm = PositionManager(self.clock, self.dm, self.cash, 1)
        self.symbols = self.dm.get_symbols()
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(4, 30, 180))
        self.symbols = None
        self.final_cash_value = []
        #self.print_intro()
        self.avg_reward = 0
        self.episodes_ran = 0

    def get_frame(self):
        return self.dm.get_frame()

    def build_paper_model(self):
        model = Sequential()
        model.add(Conv2D(32, (8, 8), strides=(4, 4), input_shape=(4, 30,180), activation='relu', data_format='channels_first'))
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
        return model

    def reset(self):
        print('Cash before reset:', self.cash)
        self.clock.reset()
        self.cash = 100000
        self.episodes_ran += 1
        self.dm.reset()

        if self.episodes_ran > 1:
            print('reset', self.episodes_ran)
            print('Current cash:', self.cash)

        frame = self.dm.get_frame()
        self.first_frame = frame
        return frame

    def position_to_close(self, index):
        return self.pm.position_expired(index)

    def close_positions(self):
        return self.pm.close_positions()

    def update_action_count(self, action):
        if action == actions.Actions.BUY:
            buy_count += 1
        elif action == actions.Actions.SELL:
            sell_count += 1
        elif action == actions.Actions.HOLD:
            hold_count += 1

    def step(self, action):
        self.update_action_count(action)

        done = self.clock.done()
        frame = self.dm.get_frame() if not done else self.first_frame
        reward = self.pm.close_position() * self.REWARD_MULT
        info = {}

        if not np.isfinite(reward):
            reward = 0

        if done is self.dm.SYMBOL_INCR_FLAG:
            print('\nCash before increment:', self.cash)
            self.final_cash_value.append(self.cash)
            len_images, len_symbols = self.dm.increment_symbol()
            self.clock.set_params(len_images, len_symbols)
            done = False
            self.pm.open_position(action, self.clock.index)
            self.clock.tick()
        else:
            self.pm.open_position(action, self.clock.index)
            self.update_cash(reward)
            self.clock.tick()

        return frame, reward, done, info

    def update_cash(self, reward):
        reward /= self.REWARD_MULT
        self.old_cash = self.cash
        self.cash = (1 + reward) * self.cash

    def print_intro(self):
        start = self.dm.get_date()
        end = self.dm.get_ending_date()
        delta = end-start
        print('Preparing environment for:', fg('red'),
              self.dm.get_symbol() + attr('reset'))
        print('Starting date:', start, 'Ending Date:', end)
        print("Time period:", delta.days, 'days')
        print('Starting Balance:', fg('green'), self.get_cash(), attr('reset'))

    def get_cash(self):
        #need t0 make a proper formatting method
        return self.cash

    def print_returns(self):
        for i, symbol in enumerate(self.symbols):
            print(symbol, self.final_cash_value[i])


if __name__ == "__main__":
    weights_filename = '../data/weights/dqn_{}_weights.h5f'.format('test')
    env = StockEnv()
    mode = 'train'

    env_name = 'senior_thesis_env_v1.0'
    model = env.build_paper_model()
    memory = SequentialMemory(limit=1000000, window_length=4)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                               nb_steps=1000000)

    dqn = DQNAgent(model=model, nb_actions=3, policy=policy, memory=memory,
                   nb_steps_warmup=50000, gamma=.99, target_model_update=10000,
                   train_interval=4, delta_clip=1.)
    dqn.compile(Adam(lr=.00025), metrics=['mae'])

    if mode == 'train':
        # Okay, now it's time to learn something! We capture the interrupt exception so that training
        # can be prematurely aborted. Notice that now you can use the built-in Keras callbacks!
        weights_filename = 'dqn_{}_weights.h5f'.format(env_name)
        checkpoint_weights_filename = 'dqn_' + env_name + '_weights_{step}.h5f'
        log_filename = 'dqn_{}_log.json'.format(env_name)
        callbacks = [ModelIntervalCheckpoint(checkpoint_weights_filename, interval=250000)]
        callbacks += [FileLogger(log_filename, interval=100)]
        dqn.fit(env, callbacks=callbacks, nb_steps=50000, log_interval=10000)

        # After training is done, we save the final weights one more time.
        dqn.save_weights(weights_filename, overwrite=True)
    elif mode == 'test':
        weights_filename = '../data/weights/{}'.format(env_name)
        dqn.load_weights(weights_filename)
        dqn.test(env, nb_episodes=10, visualize=True)

    env.print_returns()
    print('Completed')
    print('buy count:', buy_count)