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

from actions import Actions
from data_manager import DataManager
from position_manager import Position, PositionManager, PositionQueue

warnings.simplefilter(action='ignore', category=FutureWarning)

class StockEnv(gym.Env):
    def __init__(self):
        self.env_name = 'gaf-environment-v1.0'
        self.current_action = None
        self.previous_action = None
        self.dm = DataManager()
        self.pm = PositionManager(self.dm, 1)
        self.cash = 100000
        self.index = 3
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(4, 30, 180))
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
        self.episodes_ran += 1

        if self.episodes_ran > 1:
            print('reset', self.episodes_ran)

        with open('results.txt', 'a') as file:
            file.write(str(self.cash) + "\n")


        self.dm.reset()
        self.index = 0
        frame = self.dm.get_frame()
        self.first_frame = frame
        return frame

    def position_to_close(self, index):
        return self.pm.position_expired(index)

    def close_positions(self):
        return self.pm.close_positions()

    def step(self, action):
        self.pm.open_position(action, self.index)

        reward = self.pm.close_position()
        self.update_cash(reward)

        done = self.is_done()
        frame = self.dm.get_frame() if not done else self.first_frame
        info = {}
    
        self.step_()
        return (frame, reward, done, info)

    def update_cash(self, reward):
        self.cash = (1 + reward) * self.cash

    def step_(self):
        self.index += 1
        self.dm.step()

    def is_done(self):
        return True if (self.dm.is_done() or self.cash <= 0) else False

    def step_old(self, action):
        self.previous_action = self.current_action
        self.current_action = action 

        frame, date = self.dm.step()

        if frame is None:
            frame = self.last_obsv

        if frame is -1:
            done = True
        else:
            done = False

        self.index += 1
        info = {}

        reward = 0

        if self.index % 10000 == 0:
            self.dm.print_state()

        self.last_obsv = frame
        return(frame, reward, done, info)

    def process_action(self, action):
        if action == Actions.BUY:
            return 0
        elif action == Actions.SELL:
            return 1
        elif action == Actions.HOLD:
            return 2

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

if __name__ == "__main__":
    #weights_filename = '../data/weights/dqn_{}_weights.h5f'.format('test')
    env = StockEnv()

    model = env.build_paper_model()
    memory = SequentialMemory(limit=1000000, window_length=4)
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(), attr='eps', value_max=1., value_min=.1, value_test=.05,
                               nb_steps=1000000)
 
    dqn = DQNAgent(model=model, nb_actions=3, policy=policy, memory=memory,
               nb_steps_warmup=50000, gamma=.99, target_model_update=10000,
               train_interval=4, delta_clip=1.)
    dqn.compile(Adam(lr=.00025), metrics=['mae'])

    if True:
        weights_filename = weights_filename.format('gaf')
        checkpoint_weights_filename = 'dqn_' + \
           'gaf' + '_weights_{step}.h5f'
        log_filename = 'dqn_{}_log.json'.format('gaf')
        callbacks = [ModelIntervalCheckpoint(
           checkpoint_weights_filename, interval=250000)]
        callbacks += [FileLogger(log_filename, interval=100)]
        dqn.fit(env, nb_steps=1750000, log_interval=10000)

    # print('About to start!')
    # while False:
    #     if env.dm.is_done() is False:
    #         env.dm.step()

    #         if env.dm._current_index % 500 is 0:
    #             print(env.dm._current_index)
    #     else:
    #         break
    
    print('Completed')