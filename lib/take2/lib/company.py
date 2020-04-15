from lib import data_pipeline
from lib import position

class StepData:
    def __init__(self, image, prices, action):
        self.image = image
        self.action = action
        self.is_weekend_or_none = False
        self.next_prices = prices[1]
        self.current_prices = prices[0]

    @property
    def frame(self):
        return self.image.squeeze(axis=0)

    @property
    def is_hold(self):
        return (self.action == position.PositionTypes.hold)

    @property
    def is_weekend(self):
        return self.next_prices is None or self.current_prices is None

    @property
    def should_skip(self):
        return self.is_hold or self.is_weekend

class Company:
    def __init__(self, symbol, paths, helper):
        self.symbol = symbol
        self.helper = helper
        self.data_dir, self.price_dir = paths
        self.load_data()

    def load_data(self):
        pipeline = data_pipeline.DataPipeline(self.helper)
        self.dates = pipeline.load_dates(self.symbol, self.data_dir)
        self.images = pipeline.load_images(self.symbol, self.data_dir)
        self.prices = pipeline.load_prices(self.symbol, self.price_dir)

    @property
    def data_length(self):
        return len(self.images) - 1 #because we are
        # using tomorrows prices to evaluate the reward each round

    def get_prices(self, index):
        current_prices = self.get_price_w_date_index(index)
        tomorrows_prices = self.get_price_w_date_index(index + 1)
        return current_prices, tomorrows_prices

    def get_price_w_date_index(self, date_index):
        try:
            date = self.dates.iloc[date_index]
            date = date['Date']
            price = self.prices[self.prices['Date'] == date]
            return price
        except ValueError as e:
            return None

    def get_image(self, index):
        return self.images[index + 1]

    def get_first_observation(self):
        return self.images[0].squeeze(axis=0)

    def get_data_for_step(self, index, action):
        image = self.get_image(index)
        prices = self.get_prices(index)
        return StepData(image, prices, action)



