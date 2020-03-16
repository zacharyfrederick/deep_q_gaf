from actions import Actions
import random

class Position:
    def __init__(self, type_, open_index, \
        close_index, open_price, close_price):
        self.type = type_
        self.open_index = open_index
        self.close_index = close_index
        self.open_price = open_price
        self.close_price = close_price

class PositionQueue:
    def __init__(self):
        self.queue = []

    def add(self, position):
        self.queue.append(position)

    def peek(self):
        if len(self.queue) is 0:
            return None
        else:
            return self.queue[0]

    def __str__(self):
        for pos in self.queue:
            return '{} {} {} {} {}'.format(pos.type, pos.open_index, pos.close_index, pos.open_price, pos.close_price)

    def remove(self): 
        current = self.peek()

        if current is not None:
            self.queue.remove(current)
            return current
        else:
            return None

class PositionManager:
    def __init__(self,clock, dm, cash, holding_period=1):
        self.clock = clock
        self.dm = dm #the data manager, needed for pricing data
        self.cash = cash
        self.pq = PositionQueue()
        self.holding_period = holding_period #how long before the position is closed
        self.is_open = False
        self.is_long = False

    def reset(self):
        self.pq = PositionQueue()

    def open_position(self, type_, open_index):
        close_index = open_index + self.holding_period
        open_ = self.dm.get_price_w_index(open_index, 'Open')
        close = self.dm.get_price_w_index(close_index, 'Open')
        position = Position(type_, open_index, close_index,\
           open_, close)
        self.pq.add(position)

    def close_position(self):
        return random.uniform(-.0003, 0.003)
        position = self.pq.remove()

        if position is None:
            return 0

        open_ = position.open_price
        close = position.close_price

        return_ = ((close - open_) / open_)
        if Actions(position.type) == Actions.HOLD:
            return 0
        elif Actions(position.type) == Actions.BUY:
            return return_
        elif Actions(position.type) == Actions.SELL:
            return -1 * return_
        else:
            return 0

    def position_expired(self, close_index):
        return True if self.pq.peek().close_index is close_index else False
