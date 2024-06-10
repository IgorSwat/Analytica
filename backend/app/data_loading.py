import pandas as pd
import re

from processor_base import Processor


# PROCESSOR
# Provides raw data based on loaded .csv file
class DataProvider(Processor):

    def __init__(self, data_source: pd.DataFrame, fix_commas=True):
        super().__init__()
        self.df = data_source

        if fix_commas:
            self.fix_commas()


    def __call__(self, *args, **kwargs):
        return self.df


    # Fixes all incorrect float number patterns, such as "127,0003, as well as integers classified as strings"
    def fix_commas(self):
        bad_float_pattern = r"(-?\d+),(\d+)"
        int_pattern = r"^-?\d+$"

        is_bad_float = lambda val: isinstance(val, str) and re.match(bad_float_pattern, val) is not None

        def map_bad_floats(val):
            if isinstance(val, str):
                float_match = re.match(bad_float_pattern, val)
                if float_match is not None:
                    correct_val = float_match.group(1) + "." + float_match.group(2)
                    return float(correct_val)

                int_match = re.match(int_pattern, val)
                if int_match is not None:
                    return float(val)

            return val

        for column in self.df.columns:
            has_bad_floats = self.df[column].apply(is_bad_float).any()
            if has_bad_floats:
                self.df[column] = self.df[column].apply(map_bad_floats)

        self.df = self.df.applymap(map_bad_floats)
