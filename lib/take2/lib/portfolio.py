from lib import helper
from lib.position import PositionTypes, Position

class Portfolio():
    def __init__(self, cash):
        self.initial_cash = cash
        self.profits = 0
        self.losses = 0

        self.num_wins = 0
        self.num_losses = 0

        self.helper = helper.Helper()
        self.reset()

    def reset(self):
        self.cash = self.initial_cash
        self.total = 0
        self.profits = 0
        self.losses = 0

        self.num_wins = 0
        self.num_losses = 0

    def update_cash(self, return_, prev_action):
        result = self.initial_cash * return_

        if prev_action == PositionTypes.buy.value:
            if result > 0.00:
                self.profits += result
            elif result < 0.00:
                self.losses += result
        elif prev_action == PositionTypes.sell.value:
            if result > 0.00:
                self.losses += result * -1
            elif result < 0.00:
                self.profits += result * -1

    def print_portfolio_results(self):
        print()
        print(self.profits)
        print(self.losses)
        print()

    def execute_action(self, action, price, next_price):
        trade = self.open_position(action, price, next_price)
        return trade.return_

    def get_open_close_prices(self, price, next_price):
        print(price, next_price)
        open_price = self.helper.get_value_from_row(price, 'Close')
        close_price = self.helper.get_value_from_row(next_price, 'Close')
        return open_price, close_price

    def get_open_close_dates(self, price, next_price):
        open_date = self.helper.get_value_from_row(price, 'Date')
        close_date = self.helper.get_value_from_row(next_price, 'Date')
        return open_date, close_date

    def open_position(self, action, price, next_price):
        type_ = PositionTypes(action)
        open_price, close_price = self.get_open_close_prices(price, next_price)
        open_date, close_date = self.get_open_close_dates(price, next_price)
        return Position(type_, open_date, close_date, open_price, close_price)
