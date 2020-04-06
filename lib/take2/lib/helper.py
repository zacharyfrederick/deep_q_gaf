import os
import pandas as pd
from . import unsafe_helper

class Helper:
    def __init__(self):
        self.unsafe = unsafe_helper.Unsafe()

    def format_path_w_symbol(self, path, symbol):
        return os.path.join(path, symbol)

    def format_df_dates(self, df, column_name):
        df[column_name] = pd.to_datetime(df[column_name])

    def get_row_w_value(self, df, column, value):
        return self.unsafe.get_row_w_value(df, column, value)

    def get_row_w_index(self, df, index):
        return self.unsafe.get_row_w_index(df, index)

    def get_value_from_row(self, row, column):
        return row[column].values[0]

    def format_date_file(self, symbol, path):
        filename =  '{}_dates.csv'.format(symbol)
        return os.path.join(path, filename)

    def format_image_file(self, symbol, path):
        filename = '{}.npy'.format(symbol)
        return os.path.join(path, filename)

    def format_price_file(self, symbol, path):
        filename= '{}.csv'.format(symbol)
        return os.path.join(path, filename)