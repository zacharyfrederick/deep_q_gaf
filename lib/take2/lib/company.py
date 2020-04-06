from lib import data_pipeline

class Company:
    def __init__(self, symbol, paths, helper):
        self.symbol = symbol
        self.helper = helper
        self.data_dir, self.price_dir = paths
        self.load_data()

    def load_data(self):
        pipeline = data_pipeline.DataPipeline(self.helper)

        self.images = pipeline.load_images(self.symbol, self.data_dir)
        self.dates = pipeline.load_dates(self.symbol, self.data_dir)
        self.prices = pipeline.load_prices(self.symbol, self.price_dir)

    @property
    def data_length(self):
        return len(self.images) - 1 #because we are
        # using tomorrows prices to evaluate the reward each round

    def get_prices(self, index):
        current_prices = self.prices.iloc[index]
        tomorrows_prices = self.prices.iloc[index + 1]
        return current_prices, tomorrows_prices

    def get_image(self, index):
        return self.images[index + 1]

    def get_data_for_step(self, index):
        image = self.get_image(index)
        prices = self.get_prices(index)
        return image, prices[0], prices[1]



