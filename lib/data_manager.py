
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os

import numpy as np
import pandas as pd

import sys
sys.path.append('../../../Github/')
import Janet

class DataManager:
    def __init__(self, clock):
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
        self.current_symbol = self.load_symbols()
        self.length = 0
        
        self.set_initial_state()
        print('after initial state is set in dm')
        print(self.dates.head())
        print(self.prices.head())
        print(self.images[0])

    def set_initial_state(self):
        self.load_data()
        self.set_length()
        self.clock.set_params(self.length, len(self.symbols))


    def load_dates(self, symbol):
        date_path = os.path.join(self.concat_dir, symbol.split('.')[0] + '_dates.csv')
        self.dates = pd.read_csv(date_path)
        self.dates = Janet.pandas.reverse_df(self.dates)

    def print_state(self):
        print('Current index: {}, Symbol index: {}'.format(self.index, self.symbol_index))

    def load_symbols(self):
        self.symbols = os.listdir(self.raw_dir)
        self.symbols.remove('.DS_Store') #mac is weird
        self.symbols.remove('tsla.csv')
        self.symbols = ['goog.csv',]
        return self.symbols[0]

    def load_prices(self, symbol):
        self.prices = pd.read_csv(os.path.join(self.raw_dir, symbol))
        #self.prices = Janet.pandas.reverse_df(self.prices)

        print('Loaded pricing data')

    def load_image_data2(self, symbol):
        symbol = symbol.split('.')[0]
        symbol += '.npy'

        data_path = os.path.join(self.concat_dir, symbol)
        self.images = np.load(data_path)
        self.images = Janet.numpy.rev_ndarray(self.images)
        print(self.images.shape)

    def get_current_image(self, offset=0):
        return self.images[self.index + offset]

    def increment_symbol(self):
        print('Incrementing symbol')
        self.current_symbol = self.symbols[self.clock.symbol_index]
        self.load_data()
        print('Loaded new symbol: {}'.format(self.current_symbol))
        return (len(self.images), len(self.symbols))

    def get_date_with_index(self, index):
        return self.dates.iloc[index]

    def reset(self):
        self.current_symbol = self.symbols[self.clock.symbol_index]
        self.load_data()

    def load_data(self):
        self.load_prices(self.current_symbol)
        self.load_image_data2(self.current_symbol)
        self.load_dates(self.current_symbol)

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

    def get_value_w_index(self, index, column):
        return self.prices.iloc[index][column]

    def get_symbols(self):
        return self.symbols