class Clock:
    def __init__(self, end):
        self.reset(end)

    def reset(self, end):
        self.end = end
        self.index = 0

    def tick(self):
        self.index += 1

    @property
    def done(self):
        return self.index == self.end

