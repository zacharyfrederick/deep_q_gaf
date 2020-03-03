
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os

import numpy as np
import pandas as pd

class DataManager:
    def __init__(self):
        self._index_col = 'Date'
        self._current_index = 3
        self._raw_data_folder = '../data/raw/'
        self._processed_data_folder = '../data/processed/'
        self.load_symbols()
        self.symbol_index = 0
        self.current_symbol = self.symbols[0]
        self.load_pricing_data(self.current_symbol)
        self.load_image_data(self.current_symbol)
        self.reshape_images()
        print('len symbols: ', len(self.symbols))
    
    def print_state(self):
        print('Current index: {}, Symbol index: {}'.format(self._current_index, self.symbol_index))

    def load_symbols(self):
        symbols = os.listdir(self._raw_data_folder) 
        symbols.remove('.DS_Store') #mac is weird
        self.symbols = symbols

    def load_pricing_data(self, symbol):
        self._prices = pd.read_csv(os.path.join(self._raw_data_folder, symbol))
        self._dates = self._prices['Date']
        self._dates = pd.to_datetime(self._dates)
        print('Loaded pricing data')

    def load_image_data(self, symbol):
        symbol = symbol.split('.')[0]
        self._open = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'open.csv'))

        self._high = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'high.csv'))

        self._low = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'low.csv'))

        self._close = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'close.csv'))

        self._adj_close = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'adj_close.csv'))

        self._vol = pd.read_csv(os.path.join(self._processed_data_folder, symbol, 'vol.csv'))

    def reshape_images(self):
        self._open = self._open.drop(columns='Date')
        self._high = self._high.drop(columns='Date')
        self._low = self._low.drop(columns='Date')
        self._close = self._close.drop(columns='Date')
        self._adj_close = self._adj_close.drop(columns='Date')
        self._vol = self._vol.drop(columns='Date')

        images = pd.concat([self._open, self._high], axis=1)
        images = pd.concat([images, self._low], axis=1)
        images = pd.concat([images, self._close], axis=1)
        images = pd.concat([images, self._adj_close], axis=1)
        images = pd.concat([images, self._vol], axis=1)
        images = images.values.reshape(images.shape[0], 1, 30, 180)
        self.images = images

    def get_current_image(self, offset=0):
        return self.images[self._current_index + offset]

    def is_done(self):
        if self._current_index >= len(self._open):
            if self.symbol_index + 1 < len(self.symbols):
                return True
            else:
                print('symbold incremented')
                self.symbol_index += 1
                self.current_symbol = self.symbols[self.symbol_index]
                self._current_index = 3
                print('new symbol: {}', self.current_symbol)
                return False
        else:
            return False

    def increment_symbol(self):
        self.symbol_index += 1
        self.current_symbol = self.symbols[self.symbol_index]
        self._current_index = 3
        self.load_pricing_data(self.current_symbol)
        self.load_image_data(self.current_symbol)

    def get_frame(self):
        if self.is_done():
            return None

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
        self._current_index = 0
        return self.get_frame()

    def get_ohlc(self):
        return self._prices.iloc[self._current_index]

    def get_value_w_index(self, index, column):
        return self._prices.iloc[index][column]
