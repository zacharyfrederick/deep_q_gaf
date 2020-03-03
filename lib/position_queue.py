from position import Position

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