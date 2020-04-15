from lib import helper
from lib import portfolio
from lib import company
from lib import clock
from lib import position
import os
import pandas as pd
import gym

class BestEnvironment(gym.Env):
    def __ini__(self, sheets_file, prices_file, directory,  x_cols):
        self.sheets_file = sheets_file
        self.prices_file = prices_file
        self.data_loc = directory
        self.x_cols = x_cols

    @property
    def sheets_path(self):
        return os.path.join(self.data_loc, self.sheets_file)

    @property
    def prices_path(self):
        return os.path.join(self.data_loc, self.prices_file)

    @property
    def obsv(self):
        return self.sheets[self.index][self.x_cols]

    @property
    def first_obsv(self):
        return self.sheets[0][self.x_cols]

    @property
    def is_done(self):
        return self.index == len(self.sheets) - 1

    @property
    def price_exists(self):
        return None

    @property
    def info(self):
        return {}

    def step(self, action):
        reward = self.calculate_reward(action)
        obsv = self.obsv
        done = self.is_done
        info = self.info
        self.tick()
        return obsv, reward, done, info

    def tick(self):
        self.index += 1

    #step n: observation n-1
    def reset(self):
        self.index = 1
        self.sheets = pd.read_csv(self.sheets_path)
        self.prices = pd.read_csv(self.prices_path)
        return self.first_obsv

    def calculate_reward(self, action):
        adj_index = self.index - 1
        return None

class BetterEnvironment:
    def __init__(self, config):
        self.config = config
        self.helper = helper.Helper()
        self.episodes = 0
        self.prev_action = None

    def prepare_env(self):
        self.company = self.create_company()
        self.clock = self.create_clock()
        self.portfolio = self.create_portfolio()

    def create_company(self):
        return company.Company(self.config.symbol, self.config.paths, self.helper)

    def create_clock(self):
        return clock.Clock(self.env_len)

    def create_portfolio(self):
        return portfolio.Portfolio(self.config.cash)

    def reset(self):
        if self.episodes > 0:
            self.portfolio.print_portfolio_results()

        self.episodes += 1
        self.prepare_env()
        return self.company.get_first_observation()

    def step(self, action):
        info = self.info
        done = self.done
        observation, reward = self.get_obsv_and_reward(action)
        self.portfolio.update_cash(reward, self.prev_action)

        if self.prev_action == position.PositionTypes.sell.value:
            reward *= -1
        elif self.prev_action == position.PositionTypes.hold.value:
            reward = 0

        self.prev_action = action
        self.clock.tick()
        return observation, reward, done, info

    def get_obsv_and_reward(self, action):
        step_data = self.company.get_data_for_step(self.clock.index, action)
        reward = self.calculate_reward_for_step(step_data)
        return step_data.frame, reward

    def calculate_reward_for_step(self, step_data):
        return 0 if step_data.should_skip else self.calculate_return(step_data)

    def calculate_return(self, step_data):
        #print(step_data.current_prices, step_data.next_prices, self.prev_action)
        exit_price = step_data.next_prices['Open'].values[0]
        entry_price = step_data.current_prices['Close'].values[0]
        delta = self.calc_delta(step_data.action, entry_price, exit_price)
        return delta / entry_price

    def calc_delta(self, action, entry_price, exit_price):
        delta = entry_price - exit_price

        return delta

    @property
    def done(self):
        return self.clock.done

    @property
    def info(self):
        return {}

    @property
    def env_len(self):
        return self.company.data_length - 1