import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import gym
import gym.spaces
import locale
from data_manager import DataManager

class Stockpup(gym.Env):
    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.env_name = 'stockpup-environment-0'
        self.cash = 100000
        

    


