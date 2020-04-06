import enum
from lib import helper

class TradeTypes(enum.Enum):
    buy = 0
    sell = 1
    hold = 2

class Trade():
    def __init__(self, type_, open_date, close_date, open_price, close_price):
        self.open_date = open_date
        self.close_date = close_date
        self.open = open_price
        self.close = close_price
        self.type = type_
        self.helper = helper.Helper()

    @property
    def return_(self):
        delta = self.calculate_delta()
        return delta / self.open

    def calculate_delta(self):
        return self.close - self.open if self.type == TradeTypes.buy \
            else self.open - self.close
