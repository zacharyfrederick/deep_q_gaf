import pandas as pd

class Unsafe:
    def __init__(self):
        pass

    def get_row_w_value(self, df, column, value):
        try:
            return df[df[column] == value]
        except Exception as e:
            return None

    def get_row_w_index(self, df, index):
        type_ = type(df)

        if type_ == 'pandas.core.frame.DataFrame':
            return df.iloc[index]
        elif type_ == 'numpy.ndarray':
            return df[index]
