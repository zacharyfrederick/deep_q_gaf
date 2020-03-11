import warnings

import actions
import gym
import gym.spaces
import numpy as np
from clock import Clock
from colored import attr, fg
from data_manager import DataManager
from position_manager import PositionManager

warnings.simplefilter(action='ignore', category=FutureWarning)

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

        if done == True:
            self.print_returns()

        if done is self.dm.INCR_FLAG:
            print('\nCash before increment:' +  str(self.cash))
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
        return self.cash

    def print_returns(self):
        if self.symbols is not None:
            for i, symbol in enumerate(self.symbols):
                print(symbol, self.final_cash_value[i])