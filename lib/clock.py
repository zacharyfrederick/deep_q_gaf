class Clock:
    def __init__(self, initial_value=0):
        self.initial_value = initial_value
        self.index = initial_value
        self.symbol_index = 0
        self.SYMBOL_INCR_FLAG = -1
        self.is_done = False
        self.episode_count = 3

    def tick(self):
        self.index += 1

    def done(self):
        if self.index + 2 == self.len_images:
            if self.len_symbols == 1:
                self.is_done = True
                return True
            else:
                return self.SYMBOL_INCR_FLAG
        else:
            return False

    def reset(self):
        self.is_done = False
        self.index = self.initial_value

    def set_params(self, len_images, len_symbols):
        self.len_images = len_images
        self.len_symbols = len_symbols