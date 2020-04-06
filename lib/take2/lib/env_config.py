import json

class EnvConfig(object):
    def __init__(self, filepath):
        self.read_file(filepath)
        self.format_paths()

    def read_file(self, config):
        with open(config, 'r') as file:
            raw = self.read_raw(file)
            self.set_keys(raw)

    def read_raw(self, file):
        return json.loads(file.read())

    def set_keys(self, raw):
        for key in raw:
            setattr(self, key, raw[key])

    def format_paths(self):
        self.paths = (self.data_path, self.prices_path)