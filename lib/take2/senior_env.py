import json
import os
from lib import helper
from lib import env_config
from lib import portfolio
from lib import company
from lib import clock

class BetterEnvironment:
    def __init__(self, config):
        self.config = config
        self.helper = helper.Helper()

    def prepare_env(self):
        self.company = self.create_company()
        self.clock = self.create_clock()
        self.portfolio = self.create_portfolio()

    def create_company(self):
        return company.Company(self.config.symbol, self.config.paths, self.helper)

    def create_clock(self):
        return clock.Clock(self.company.data_length)

    def create_portfolio(self):
        return portfolio.Portfolio(self.config.cash)

    def reset(self):
        self.clock.reset(self.company.get_data_len())

    def step(self, action):
        if not self.done:

            clock.tick()
        else:
            pass

    @property
    def done(self):
        return self.clock.done

if __name__ == '__main__':
    config_ = env_config.EnvConfig('config/debug.json')

    env = BetterEnvironment(config_)
    env.prepare_env()

    observation, current_prices, tomorrows_prices\
        = env.company.get_data_for_step(env.clock.index)

    print(current_prices, tomorrows_prices)
