from lib import helper
from lib.trade import TradeTypes, Trade

class Portfolio():
    def __init__(self, cash):
        self.initial_cash = cash
        self.helper = helper.Helper()

    def reset(self):
        self.cash = self.initial_cash

    def execute_action(self, action, price, next_price):
        trade = self.create_trade(action, price, next_price)
        return trade.return_

    def get_open_close_prices(self, price, next_price):
        open_price = self.helper.get_value_from_row(price, 'Close')
        close_price = self.helper.get_value_from_row(next_price, 'Close')

        return open_price, close_price

    def get_open_close_dates(self, price, next_price):
        open_date = self.helper.get_value_from_row(price, 'Date')
        close_date = self.helper.get_value_from_row(next_price, 'Date')

        return open_date, close_date

    def create_trade(self, action, price, next_price):
        open_price, close_price = self.get_open_close_prices(price, next_price)
        open_date, close_date = self.get_open_close_dates(price, next_price)
        type_ = TradeTypes(action)

        return Trade(type_, open_date, close_date, open_price, close_price)
