import pandas as pd
from processor_base import Processor

# PROCESSOR
# Provides raw data based on loaded .csv file
class DataProvider(Processor):

    def __init__(self, data_source: pd.DataFrame):
        super().__init__()
        self.df = data_source


    def __call__(self, *args, **kwargs):
        return self.df
