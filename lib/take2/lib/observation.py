from tools import helper

class Observation():
    def __init__(self, image, row):
        self.row = row
        self.image = image
        self.helper = helper.Helper()

    @property
    def open(self):
        return self.helper.get_value_from_row(self.row, 'Open')

    @property
    def high(self):
        return self.helper.get_value_from_row(self.row, 'High')

    @property
    def low(self):
        return self.helper.get_value_from_row(self.row, 'Low')

    @property
    def close(self):
        return self.helper.get_value_from_row(self.row, 'Close')

    @property
    def adj_close(self):
        return self.helper.get_value_from_row(self.row, 'Adj Close')

    def volume(self):
        return self.helper.get_value_from_row(self.row, 'Volume')
