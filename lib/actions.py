import enum

class Actions(enum.Enum):
    BUY = 0
    SELL = 1
    HOLD = 2
    CIRCUIT_BREAKER_UP = 3
    CIRCUIT_BREAKER_DOWN = 4