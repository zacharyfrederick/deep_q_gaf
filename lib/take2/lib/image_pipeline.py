import numpy as np
from tools import helper

class ImagePipeline:
    def __init__(self, symbol, data_path):
        self.helper = helper.Helper()
        self.load_images(symbol, data_path)

    def load_images(self, symbol, path):
        self.images = np.load(self.helper.format_image_file(symbol, path))

    def get_image(self, i):
        return self.images[i]

