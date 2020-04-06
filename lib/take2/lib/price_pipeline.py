from tools import helper
import pandas as pd

class PricePipeline:
    def __init__(self, symbol, path):
        self.helper = helper.Helper()
        self.load_prices(symbol, path)

    def load_prices(self, symbol, path):
        self.prices = pd.read_csv(self.helper.format_price_file(symbol, path))
        self.helper.format_df_dates(self.prices, 'Date')

    def get_prices(self, timestamp):
        row = self.helper.get_row_w_value(self.prices, 'Date', timestamp)
        return row


