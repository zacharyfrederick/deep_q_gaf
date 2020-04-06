import pandas as pd
import numpy as np

class DataPipeline():
    def __init__(self, helper):
        self.helper = helper

    def load_prices(self, symbol, path):
        prices = pd.read_csv(self.helper.format_price_file(symbol, path))
        prices['Date'] = pd.to_datetime(prices['Date'])
        return prices

    def load_dates(self, symbol, path):
        dates = pd.read_csv(self.helper.format_date_file(symbol, path))
        dates['Date'] = pd.to_datetime(dates['Date'])
        return dates

    def load_images(self, symbol, path):
        return np.load(self.helper.format_image_file(symbol, path))

