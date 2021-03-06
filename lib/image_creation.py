import os
import sys

import pandas as pd
from pyts.image import MarkovTransitionField, GramianAngularField
from multiprocessing import Pool, cpu_count
from image_concat import concat_images

def extract_period(df, column, index, period=10, reversed=True):
    """Extracts a period of data from the dataframe column at the specified index. 
    Index row is NOT included 
    
    Arguments:
        df {dataframe} -- obvious
        column {string} -- specified column
        index {int} -- where the period ends 
        reversed {bool} -- is the dataframe in reverse order and requires output to be reversed 
    
    Keyword Arguments:
        period {int} -- length of period in days (default: {30})
    
    Returns:
        list -- the specified period in the dataframe
    """

    index += 1 #move to the next date
    if (index + period) < len(df):
        output = []

        for offset in range(0, period):
            value = df.iloc[index + offset][column]
            output.append(value)
        return output[::-1] if reversed else output #reverse the period since the dataframe is coming in reversed
    else:
        return None

def create_image(data, date=None, image_size=10, method='summation', field='gaf', strategy='uniform'):
    """Creates an image of the specified size and using the specified field
    
    Arguments:
        data {list} -- [the list of data to transform]
    
    Keyword Arguments:
        image_size {int} -- the size of the output image (default: {30})
        method {str} -- the method for the gramian angular field. Def. is summation (default: {'s'})
        field {sr} -- The specified field to use. GAF or MTF (default: {'g'})
        strategy {str} -- the strategy for MTF

    Returns dataframe if successful or None if not
    """
    if field is 'gaf':
        field = GramianAngularField(image_size=image_size, method=method)
    elif field is 'mtf':
        field = MarkovTransitionField(image_size=image_size, strategy=strategy)
    else:
        return None

    data = pd.DataFrame(data).transpose()
    img = pd.DataFrame(field.transform(data).flatten()).transpose()
    img['Date'] = date
    img = img.set_index('Date')
    return img

def extract_ohlc(df, index):
    """Extracts the open high low close adj_close and volume from a df
    at the specified index
    
    Arguments:
        df {dataframe} -- data
        index {int} -- obvious
    
    Returns:
        tuple -- the values
    """
    open_ = extract_period(df, 'Open', index)
    high = extract_period(df, 'High', index)
    low = extract_period(df, 'Low', index)
    close = extract_period(df, 'Close', index)
    adj_close = extract_period(df, 'Adj Close', index)
    vol = extract_period(df, 'Volume', index)

    if open_ is None:
        return (None, None, None, None, None, None)
    else:
        return (open_, high, low, close, adj_close, vol)

def extract_date(df, index):
    return df.iloc[index]['Date']

def job(symbol):
    raw_data_folder = '../data/raw/'
    output_data_folder = '../data/processed/10/'
    processed_file_list = os.path.abspath('../data/processed_files.txt')
    print('Starting processing for', symbol)
    path = os.path.join(raw_data_folder, symbol)
    output_created = False
    days_processed = 0
    symbol_print = symbol.split('.')[0]

    if not os.path.exists(output_data_folder):
        os.mkdir(output_data_folder)

    df = pd.read_csv(path)
    df = df.iloc[::-1]  # reverse the dataframe for easier working
    df = df.dropna()  # drop any nan
    # df['Date'] = pd.to_datetime(df['Date']) #converts the date to datetime

    for index in range(0, len(df)):  # iterate through each day in the dataframe
        date = extract_date(df, index)

        open_t, high_t, low_t, close_t, adj_close_t, vol_t = extract_ohlc(df, index)  # temporary
        if open_t is None:
            break

        open_img = create_image(open_t, date)
        high_img = create_image(high_t, date)
        low_img = create_image(low_t, date)
        close_img = create_image(close_t, date)
        adj_close_img = create_image(adj_close_t, date)
        vol_img = create_image(vol_t, date)

        date = df.iloc[index]['Date']
        open_img['Date'] = date
        high_img['Date'] = date
        low_img['Date'] = date
        close_img['Date'] = date
        adj_close_img['Date'] = date
        vol_img['Date'] = date

        if not output_created:
            open_ = open_img
            high = high_img
            low = low_img
            close = close_img
            adj_close = adj_close_img
            vol = vol_img
            output_created = True
        else:
            open_ = open_.append(open_img)
            high = high.append(high_img)
            low = low.append(low_img)
            close = close.append(close_img)
            adj_close = adj_close.append(adj_close_img)
            vol = vol.append(vol_img)

        days_processed += 1

    folder = symbol_print
    path = os.path.join(output_data_folder, folder)
    prev_path = os.getcwd()

    if not os.path.exists(path):
        os.mkdir(path)

    open_ = open_.iloc[::-1]
    open_.to_csv(os.path.join(path, 'open.csv'), index=False)

    high = high.iloc[::-1]
    high.to_csv(os.path.join(path, 'high.csv'), index=False)

    low = low.iloc[::-1]
    low.to_csv(os.path.join(path, 'low.csv'), index=False)

    close = close.iloc[::-1]
    close.to_csv(os.path.join(path, 'close.csv'), index=False)

    adj_close = adj_close.iloc[::-1]
    adj_close.to_csv(os.path.join(path, 'adj_close.csv'), index=False)

    vol = vol[::-1]
    vol.to_csv(os.path.join(path, 'vol.csv'), index=False)

    with open(processed_file_list, 'a+') as file:
        file.write(symbol + '\n')
    print('finished processing {} days for {}'.format(days_processed, symbol_print))

if __name__ == "__main__":
    raw_data_folder = os.path.abspath('../data/raw/')
    processed_file_list = os.path.abspath('../data/processed_files.txt')
    symbols = os.listdir(raw_data_folder)

    try:
        symbols.remove('.DS_Store')
    except Exception as e:
        print(e)

    with open(processed_file_list, 'a+') as file:
        processed_files = file.readlines()
        for file in processed_files:
            file = file.strip('\n')
            try:
                symbols.remove(file.strip('\n'))
            except Exception as e:
                #print(file)
                #print(e)
                pass

    with Pool(cpu_count()) as p:
        p.map(job, symbols)

    concat_images()
    print("Completed Image Generation")
