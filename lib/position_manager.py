from actions import Actions
import queue

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

    def remove(self):
        current = self.peek()

        if current is not None:
            self.queue.remove(current)
            return current
        else:
            return None

class PositionManager:
    def __init__(self, dm, holding_period=1):
        self.dm = dm #the data manager, needed for pricing data
        self.pq = PositionQueue()
        self.holding_period = holding_period #how long before the position is closed
        self.is_open = False
        self.is_long = False

    def open_position(self, type_, open_index):
        close_index = open_index + self.holding_period

        open_ = self.dm.get_value_w_index(open_index, 'Open')
        close = self.dm.get_value_w_index(close_index, 'Open')

        position = Position(type_, open_index, close_index,\
            open_, close)

        self.pq.add(position)
        

    def get_value_w_index(self, index, column):
        self.dm.get_value_w_index(index, column)

    def close_position(self):
        position = self.pq.remove()

        if position is None:
            return 0
            
        open_ = position.open_price
        close = position.close_price
        #print('date', self.dm.get_date_w_index(self.dm._current_index),'type', position.type, 'Open:', open_, "close:", close)

        if Actions(position.type) == Actions.HOLD:
            return 0
        elif Actions(position.type) == Actions.BUY:
            return_ = ((close - open_) / open_)
            return return_
        elif Actions(position.type) == Actions.SELL:
            return_ = ((open_ - close) / close)
            return return_


    def position_expired(self, close_index):
        return True if self.pq.peek().close_index is close_index else False
