import pandas as pd

from typing import List, Dict, Callable


def df_to_json(df: pd.DataFrame):
    serialized_data = df.values.tolist()
    return [[str(x) for x in row] for row in serialized_data]


def f_properties_to_list(f_properties: Dict, df: pd.DataFrame, mapping: Callable = lambda x: x):
    return [mapping(f_properties[col]) for col in df]


def f_properties_from_list(values: List, df:pd.DataFrame, mapping: Callable = lambda x: x):
    return {col: mapping(values[i]) for i, col in enumerate(df)}
