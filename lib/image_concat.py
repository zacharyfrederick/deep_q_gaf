import csv
import os
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
# these explain which values we are reading, we may want to add more later or something
data_descriptor = {
    'Open': 'open.csv',
    'High': 'high.csv',
    'Low': 'low.csv',
    'Close': 'close.csv',
    'Adjusted Close': 'adj_close.csv',
    'Volatility': 'vol.csv'
}

IMAGE_SEED_KEYS = list(data_descriptor.keys())[0:2]

# sets the reference folder
DATA_FOLDER = os.path.abspath('../data/processed/')
OUTPUT_FOLDER = os.path.abspath('../data/concat/')
DATA_LEN_FILE = os.path.abspath("../data/processed/aapl/close.csv")
BLOCK_SIZE = 1000  # Each data file is chunked into smaller pieces for efficient working

def load_symbols():
    temp = None
    symbols = os.listdir(DATA_FOLDER)
    try:
        temp = symbols.remove('.DS_Store')  # this is a weird macosx thing
    except Exception as e:
        print('Could not remove .DS_Store', e)

    symbols = symbols if temp is None else temp
    return symbols
    # symbols = ('goog',)

def construct_path_to_descriptor(symbol, descriptor):
    return os.path.join(DATA_FOLDER, symbol, descriptor)

def resource_heavy_way(symbol):
    if os.path.exists(OUTPUT_FOLDER) == False:
        os.mkdir(OUTPUT_FOLDER)

    # needed later
    data = {}

    print('Loading data for:', symbol)
    # read the data
    for descriptor in data_descriptor:
        path = construct_path_to_descriptor(symbol, data_descriptor[descriptor])
        df = pd.read_csv(path)
        dates = pd.DataFrame(df['Date'])
        df = df.drop(columns='Date')
        data[descriptor] = df

    # build the initial images
    images = pd.concat([data[IMAGE_SEED_KEYS[0]], data[IMAGE_SEED_KEYS[1]]], axis=1)

    # for each descriptor concat that on to the images and reshape into final shape
    for descriptor in data_descriptor:
        if descriptor in IMAGE_SEED_KEYS:
            continue
        images = pd.concat([images, data[descriptor]], axis=1)

    images = images.values.reshape(images.shape[0], 1, 30, 180)
    print('Done processing data for:', symbol)

    output_path = os.path.join(OUTPUT_FOLDER, symbol + '.npy')
    dates_path = os.path.join(OUTPUT_FOLDER, symbol + '_dates.csv')
    np.save(output_path, images)
    dates.to_csv(dates_path, index=False)
    print('Done saving data for:', symbol)
    print('Output saved to:', output_path)

def concat_images():
    symbols = load_symbols()

    with Pool(cpu_count()) as p:
        p.map(resource_heavy_way, symbols)

    print('Completed Image Concatenation!')
