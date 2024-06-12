import pandas as pd
from datetime import datetime
from enum import Enum
from typing import List
from math import ceil, log2

# from backend.app.processor_base import Processor
from processor_base import Processor


class FeatureType(Enum):
    NUMERIC = 1
    CATEGORICAL = 2
    NONE = 3


# PROCESSOR
# Detects and extracts feature types for given DataFrame
class FeatureTypeExtractor(Processor):

    def __init__(self):
        super().__init__()


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df", pd.DataFrame)
        if df is None:
            return None

        feature_types = []
        for column in df:
            if self.__detect_id(df, column) or self.__detect_timestamp(df, column):
                feature_types.append(FeatureType.NONE)
            else:
                feature_types.append(self.__get_type(df, column))

        return feature_types


    def __detect_id(self, df: pd.DataFrame, column: str) -> bool:
        if column.lower() == "id":
            return True

        real_indices = set()
        for value in df[column]:
            if not isinstance(value, int):
                return False
            else:
                real_indices.add(int(value))

        data_size = len(df[column])
        percent = 95.0  # Measure of level of identity two sets must fulfill to be considered as index sets
        expected_indices = set(range(1, data_size))
        common_part = real_indices.intersection(expected_indices)

        return len(common_part) / data_size * 100 >= percent


    def __detect_timestamp(self, df: pd.DataFrame, column: str) -> bool:
        if column.lower() in ["timestamp", "date", "datetime", "date-time"]:
            return True

        first_value = df[column].dropna().iloc[0]
        return isinstance(first_value, str) and self.__is_timestamp(first_value)


    def __is_timestamp(self, string: str) -> bool:
        formats = [
            "%Y-%m-%d",  # YYYY-MM-DD
            "%d-%m-%Y",  # DD-MM-YYYY
            "%d.%m.%Y",  # DD.MM.YYYY
            "%m/%d/%Y",  # MM/DD/YYYY
            "%Y-%m-%d %H:%M",  # YYYY-MM-DD HH:MM:SS
            "%d-%m-%Y %H:%M",  # DD-MM-YYYY HH:MM:SS
            "%d.%m.%Y %H:%M",  # DD.MM.YYYY HH:MM:SS
            "%m/%d/%Y %H:%M",  # MM/DD/YYYY HH:MM:SS
            "%H:%M %Y-%m-%d",  # HH:MM:SS YYYY-MM-DD
            "%H:%M %d-%m-%Y",  # HH:MM:SS DD-MM-YYYY
            "%H:%M %d.%m.%Y",  # HH:MM:SS DD.MM.YYYY
            "%H:%M %m/%d/%Y"  # HH:MM:SS MM/DD/YYYY
        ]

        for fmt in formats:
            try:
                datetime.strptime(string, fmt)
                return True
            except ValueError:
                pass

        return False


    def __get_type(self, df: pd.DataFrame, column: str) -> FeatureType:
        df_drop_na = df[column].dropna()
        first_value = df_drop_na.iloc[0]

        # Customizable parameters
        unique_factor = 2
        unique_threshold = unique_factor * ceil(log2(len(df_drop_na)))

        if isinstance(first_value, str):
            return FeatureType.CATEGORICAL
        else:
            n_unique = df_drop_na.nunique()
            return FeatureType.NUMERIC if n_unique >= unique_threshold else FeatureType.CATEGORICAL


# PROCESSOR
# Serializes list of feature types (enums) into list of pure integers
class FeatureTypeSerializer(Processor):

    def __init__(self):
        super().__init__()


    def __call__(self, *args, **kwargs):
        feature_types = self.extract_arg(kwargs, "f_types", list)
        if feature_types is None:
            return None

        return [f_type.value for f_type in feature_types]