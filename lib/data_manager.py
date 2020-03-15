
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os

import numpy as np
import pandas as pd

import random
import sys
import time

janet_path = '../../../Github/' if sys.platform == 'darwin' else '../../../zachfred62/'

sys.path.append(janet_path)
import Janet

class DataManager:
    def __init__(self, clock):
        random.seed(time.time())
        self.clock = clock
        self.final_cash_value = []
        self.INCR_FLAG = -1
        self.name_of_index = 'Date'
        self.index = 3
        self.raw_dir = '../data/raw/'
        self.processed_dir = '../data/processed/'
        self.concat_dir = '../data/concat/'
        self.symbol_index = 0
        self.symbols = []
        self.length = 0
        self.symbols_processed = []
        self.symbols_failed = []
        self.set_initial_state()
        print('done')

    def print_day(self):
        print()

    def set_initial_state(self):
        self.current_symbol = self.load_symbols()
        self.load_data()
        self.set_length()
        self.clock.set_params(self.length, len(self.symbols))

    def load_dates(self, symbol):
        date_path = os.path.join(self.concat_dir, symbol.split('.')[0] + '_dates.csv')
        self.dates = pd.read_csv(date_path)
        self.dates = Janet.pandas.reverse_df(self.dates)
        self.dates['Date'] = pd.to_datetime(self.dates['Date'])
        self.dates = self.dates.iloc[::-1]
        print(self.dates)
        return True

    def print_state(self):
        print('Current index: {}, Symbol index: {}'.format(self.index, self.symbol_index))

    def load_symbols(self):
        self.symbols = os.listdir(self.raw_dir)
        print(self.symbols)

        remove_list = [
            '.DS_Store',
            'treasury_rates.csv',
            'treasurey_rates.xml',
            'rut.csv',
            'dji.csv',
            'gspc.csv',
        ]

        for item in remove_list:
            if item in self.symbols:
                self.symbols.remove(item)

        print(self.symbols)
        self.symbols = ['aapl.csv']
        symbol = self.get_rand_sym()
        print('Now processing', symbol)
        return symbol

    def load_prices(self, symbol):
        self.prices = pd.read_csv(os.path.join(self.raw_dir, symbol))
        self.prices['Date'] = pd.to_datetime(self.prices['Date'])
        print(self.prices)
        return True

    def load_image_data2(self, symbol):
        original = symbol
        symbol = symbol.split('.')[0] + '.npy'
        data_path = os.path.join(self.concat_dir, symbol)

        self.images = np.load(data_path)
        self.images = Janet.numpy.rev_ndarray(self.images)
        self.clock.len_images = len(self.images)
        return True

    def get_current_image(self, offset=0):
        return self.images[self.index + offset]

    def get_rand_sym(self):
        return random.choice(self.symbols)

    def increment_symbol(self, successful=True):
        if not successful:
            self.symbols_failed.append(self.current_symbol)
        else:
            self.symbols_processed.append(self.current_symbol)

        self.symbols.remove((self.current_symbol))
        self.clock.len_symbols = len(self.symbols)
        self.current_symbol = self.get_rand_sym()
        print('Now processing', self.current_symbol)
        self.load_data()
        return (len(self.images), len(self.symbols))

    def get_date_with_index(self, index):
        return self.dates.iloc[index]

    def reset(self):
        self.set_initial_state()

    def load_data(self):
        self.load_image_data2(self.current_symbol)
        self.load_dates(self.current_symbol)
        self.load_prices(self.current_symbol)
        print('all loaded succesfully')

    def set_length(self):
        self.length = len(self.images)

    def get_frame(self):
        return self.get_current_image().squeeze(axis=0)

    def get_date(self):
        return self._dates.iloc[self.index].to_pydatetime()

    def step(self):
        self.index += 1
        return (self.get_frame(), self.get_date())

    def get_symbol(self):
        return self.symbols[self.symbol_index]

    def get_ending_date(self):
        return self._dates.iloc[-1].to_pydatetime()

    def get_date_w_index(self, index):
        return self._dates.iloc[index].to_pydatetime()

    def get_ohlc(self):
        return self.prices.iloc[self.index]

    def get_price_w_index(self, index, column):
        first_date = self.dates.iloc[index]['Date']
        return self.prices[self.prices['Date'] == first_date].iloc[0][column]

    def get_symbols(self):
        return self.symbols