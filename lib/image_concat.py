import csv
import os

import numpy as np
import pandas as pd


class ImageConcat:
    """Uses strip mining. Thanks Dr. Peir
    
    Returns:
        Nothing
    """
    def __init__(self):
        #these explain which values we are reading, we may want to add more later or something
        self.data_descriptor = {
            'Open': 'open.csv',
            'High': 'high.csv',
            'Low': 'low.csv',
            'Close': 'close.csv',
            'Adjusted Close': 'adj_close.csv',
            'Volatility': 'vol.csv'
        }

        self.IMAGE_SEED_KEYS = list(self.data_descriptor.keys())[0:2]

        #sets the reference folder
        self.DATA_FOLDER = '../data/processed/'
        self.OUTPUT_FOLDER = '../data/concat/'
        self.DATA_LEN_FILE = "../data/processed/aapl/close.csv"
        self.BLOCK_SIZE = 1000 #Each data file is chunked into smaller pieces for efficient working

        if os.path.exists(self.OUTPUT_FOLDER) == False:
            os.mkdir(self.OUTPUT_FOLDER)

        #Initializes everything needed to run
        self.symbol_index = 0
        self.data_index = 0
        self.load_symbols()
        self.current_symbol = self.symbols[self.symbol_index]
        self.get_data_length()
        self.run()

    def run(self):
        self.running = True
        while self.symbol_index < len(self.symbols):
            self.resource_heavy_way()
            self.incr_symbol()

    def incr_symbol(self):
        self.data_index = 0
        self.symbol_index += 1

        if self.symbol_index < len(self.symbols):
            self.current_symbol = self.symbols[self.symbol_index]
        
    def resource_heavy_way(self):
        self.get_data_length()

        #needed later
        self.data = {}

        print('Loading data for:', self.current_symbol)
        #read the data 
        for descriptor in self.data_descriptor:
            path = self.construct_path_to_descriptor(self.data_descriptor[descriptor])
            df = pd.read_csv(path)
            self.dates = df['Date']
            df = df.drop(columns='Date')
            self.data[descriptor] = df

        #build the initial images
        self.images = pd.concat([self.data[self.IMAGE_SEED_KEYS[0]], self.data[self.IMAGE_SEED_KEYS[1]]], axis=1)

        #for each descriptor concat that on to the images and reshape into final shape
        for descriptor in self.data_descriptor:
            if descriptor in self.IMAGE_SEED_KEYS:
                continue
            self.images = pd.concat([self.images, self.data[descriptor]], axis=1)

        self.images = self.images.values.reshape(self.images.shape[0], 1, 30, 180)
        print('Done processing data for:', self.current_symbol)

        output_path = os.path.join(self.OUTPUT_FOLDER, self.current_symbol + '.npy')
        dates_path = os.path.join(self.OUTPUT_FOLDER, self.current_symbol + '_dates.csv')
        np.save(output_path, self.images)
        self.dates.to_csv(dates_path)
        print('Done saving data for:', self.current_symbol)
        print('Output saved to:', output_path) 


    def get_data_length(self):
        data_len_path = os.path.join(self.DATA_FOLDER, self.current_symbol, 'open.csv')
        self.data_len = len(list(csv.reader(open(data_len_path,"r+"))))
        self.remainder = self.data_index % self.BLOCK_SIZE
        
    def load_symbols(self):
        """Loads the symbols (the directories) of the companies 
        that we have image data for. '.DS_Store' is a weird mac thing 
        """
        symbols = os.listdir(self.DATA_FOLDER)
        try:
            temp = symbols.remove('.DS_Store') #this is a weird macosx thing
        except Exception as e:
            print('Could not remove .DS_Store', e)

        self.symbols = symbols if temp is None else temp
        self.symbols = ('goog',)


    def load_data(self, symbol):
        """Loads the data for each descriptor for the passed in symbol into 
        a variable called data
        
        Arguments:
            symbol {string} -- The company
        """
        self.data = {}

        for descriptor in self.data_descriptor:
            path = self.construct_path_to_descriptor(self.data_descriptor[descriptor])
            self.data[descriptor] = pd.read_csv(path, skiprows=self.data_index, nrows=self.BLOCK_SIZE)
        
        print('Successfully loaded data for:', symbol)
        
    def construct_path_to_descriptor(self, descriptor):
        """Construct a path from the current directory to the data folder
        and then adds the current symbol and the specified descriptor
        
        Arguments:
            descriptor {string} -- Key value to a dictionary containing the specific filenames of the data
        
        Returns:
            path -- Obvious
        """
        return os.path.join(self.DATA_FOLDER, self.current_symbol, descriptor)

if __name__ == '__main__':
    ic = ImageConcat()


    


    #ic = ImageConcat()