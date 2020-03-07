
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os

import numpy as np
import pandas as pd

class DataManager:
    def __init__(self, clock):
        self._index_col = 'Date'
        self._current_index = 3
        self._raw_data_folder = '../data/raw/'
        self._processed_data_folder = '../data/processed/'
        self.concat_data_folder = '../data/concat/'
        self.load_symbols()
        self.symbol_index = 0
        self.current_symbol = self.symbols[0]   
        self.load_pricing_data(self.current_symbol)
        #self.load_image_data(self.current_symbol)
        self.load_image_data2(self.current_symbol)
        self.SYMBOL_INCR_FLAG = -1
        self.clock = clock
        self.clock.set_params(len(self.images), len(self.symbols))
        #self.reshape_images()
    
    def print_state(self):
        print('Current index: {}, Symbol index: {}'.format(self._current_index, self.symbol_index))

    def load_symbols(self):
        symbols = os.listdir(self._raw_data_folder) 
        symbols.remove('.DS_Store') #mac is weird
        symbols.remove('tsla.csv')
        self.symbols = symbols

    def load_pricing_data(self, symbol):
        self._prices = pd.read_csv(os.path.join(self._raw_data_folder, symbol))
        self._dates = self._prices['Date']
        self._dates = pd.to_datetime(self._dates)
        print('Loaded pricing data')

    def load_image_data2(self, symbol):
        symbol = symbol.split('.')[0]
        symbol += '.npy'

        data_path = os.path.join(self.concat_data_folder, symbol)
        self.images = np.load(data_path)
        print(self.images.shape)

    def get_current_image(self, offset=0):
        return self.images[self._current_index + offset]

    def increment_symbol(self):
        print('Incrementing symbol')
        self.symbol_index += 1
        self.current_symbol = self.symbols[self.symbol_index]
        self._current_index = 3
        self.load_pricing_data(self.current_symbol)
        self.load_image_data2(self.current_symbol)
        print('new symbol: {}'.format(self.current_symbol))
        print('length', len(self.images.shape))
        return (len(self.images), len(self.symbols))

    def get_frame(self):
        if self.clock.done():
            return np.empty((30, 180))

        return self.get_current_image().squeeze(axis=0)
        
    def get_date(self):
        return self._dates.iloc[self._current_index].to_pydatetime()

    def step(self):
        self._current_index += 1
        return (self.get_frame(), self.get_date())

    def get_symbol(self):
        return self.symbols[self.symbol_index]

    def get_ending_date(self):
        return self._dates.iloc[-1].to_pydatetime()

    def get_date_w_index(self, index):
        return self._dates.iloc[index].to_pydatetime()

    def reset(self):
        self._current_index = 3
        return self.get_frame()

    def get_ohlc(self):
        return self._prices.iloc[self._current_index]

    def get_value_w_index(self, index, column):
        return self._prices.iloc[index][column]
