from tools import helper
import pandas as pd

class DatePipeline:
    def __init__(self, symbol, data_path):
        self.helper = helper.Helper()
        self.load_dates(symbol, data_path)

    def load_dates(self, symbol, path):
        self.dates = pd.read_csv(self.helper.format_date_file(symbol, path))
        self.helper.format_df_dates(self.dates, 'Date')

    def get_date(self, i):
        row = self.helper.get_row_w_index(self.dates, i)
        return row['Date'] if row is not None else None
