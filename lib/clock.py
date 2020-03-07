class Clock:
    def __init__(self, initial_value=0):
        self.initial_value = initial_value
        self.index = initial_value
        self.symbol_index = 0
        self.len = None
        self.SYMBOL_INCR_FLAG = -1

    def tick(self):
        self.index += 1

    def done(self):
        if self.index == self.len_images:
            if self.symbol_index + 1 == self.len_symbols:
                self.is_done = True
                return True
            else:
                self.index = self.initial_value
                self.symbol_index += 1
                return self.SYMBOL_INCR_FLAG
        else:
            return False

    def reset(self):
        self.index = self.initial_value
        self.symbol_index = 0

    def set_params(self, len_images, len_symbols):
        self.len_images = len_images
        self.len_symbols = len_symbols