import pandas as pd
from typing import List, Tuple, Dict

from processor_base import Processor

# PROCESSOR
# Provides pieces of data specified by given ranges
class DataSelector(Processor):

    def __init__(self, ranges: List[Tuple[int, int]] = None):
        super().__init__()
        self.ranges = ranges

        if self.ranges is not None:
            self.__merge_ranges()


    def __ne__(self, other):
        return self.ranges != other.ranges


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df", pd.DataFrame)
        if df is None:
            return None

        if self.ranges is None:
            return df

        row_amt = df.shape[0]
        result = pd.DataFrame()
        for data_range in self.ranges:
            if data_range[1] >= row_amt:        # Be careful to not go beyond df size
                if data_range[0] < row_amt:
                    result = pd.concat([result, df.iloc[data_range[0]:data_range[1] + 1]])
                break
            result = pd.concat([result, df.iloc[data_range[0]:data_range[1] + 1]])

        return result


    def __merge_ranges(self):
        # Sort by first value ascending, and then by second value descending
        self.ranges.sort(key=lambda x: (x[0], -x[1]))

        results = []
        error_value = -3
        min_bound, max_bound = error_value, error_value
        for r in self.ranges:
            if r[0] > max_bound + 1:
                if min_bound != error_value:
                    results.append((min_bound, max_bound))
                min_bound = r[0]
                max_bound = r[1]
            elif r[1] > max_bound:
                max_bound = r[1]
        if min_bound != error_value:
            results.append((min_bound, max_bound))

        return results


# PROCESSOR
# Extracts only selected features from given DataFrame
class FeatureSelector(Processor):

    def __init__(self, feature_states: Dict[str, bool] = None, input_name = "df"):
        super().__init__()
        self.feature_states = feature_states
        self.input_name = input_name


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, self.input_name, pd.DataFrame)
        if df is None:
            return None

        if self.feature_states is None:
            return df

        features_to_drop = [col for col in df.columns if not self.feature_states[col]]
        return df.drop(columns=features_to_drop, inplace=False)


# PROCESSOR
# Serializes DataFrame object into list of strings, which fulfills the jsonify() requirements
class DataSerializer(Processor):

    def __init__(self, input_name="df"):
        super().__init__()
        self.input_name = input_name


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, self.input_name, pd.DataFrame)
        if df is None:
            return None

        listed_data = df.values.tolist()
        result = [[str(x) for x in row] for row in listed_data]

        return result


# Ranges parsing
# Returns ranges if command is correct, or None if parsing failed (incorrect command)
def parse_ranges(cmd, data_size):
    if cmd == "#":
        return [(0, data_size - 1)]

    num1, num2 = "", ""
    dash_flag = False
    ranges = []

    cmd += ","
    for c in cmd:
        if c.isdigit():
            num1 += c
        elif c == '-':
            if num2 != "":
                print("[COMMAND PARSER] Incorrect usage of '-'")
                return None
            num1, num2 = num2, num1
        elif c == ',':
            if num2 == "" and num1 == "":
                print("[COMMAND PARSER] Incorrect usage of ','")
                return None
            elif num2 == "":
                if int(num1) <= 0:
                    print("[COMMAND PARSER] Incorrect indices: you can use only positive values")
                    return None
                ranges.append((int(num1) - 1, int(num1) - 1))
            else:
                if num1 == "":
                    print("[COMMAND PARSER] Incorrect usage of '-'")
                    return None
                elif int(num1) <= 0 or int(num2) <= 0:
                    print("[COMMAND PARSER] Incorrect indices: you can use only positive values")
                    return None
                elif int(num2) > int(num1):
                    print("[COMMAND PARSER] Incorrect indices: first index is greater than second")
                    return None
                ranges.append((int(num2) - 1, int(num1) - 1))
            num1, num2 = "", ""
        elif c == ' ':
            continue
        else:
            print("[COMMAND PARSER] Invalid symbol:", c)
            return None

    return ranges
