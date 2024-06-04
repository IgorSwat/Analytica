import pandas as pd
from numpy import int64
from datetime import datetime
from data_properties import FeatureType
from math import ceil, log2

def select_types(df: pd.DataFrame) -> list[FeatureType]:
    feature_types = []

    for column in df:
        if detect_id(df, column) or detect_timestamp(df, column):
            feature_types.append(FeatureType.NONE.value)
            continue

        # Old code, might still be useful in some cases
        #
        # numeric_df = df[column].apply(pd.to_numeric, errors='coerce')
        # row_nan_count = numeric_df.isna().sum()
        #
        # if row_nan_count > int(len(df[column])/2):
        #     feature_types.append(FeatureType.CATEGORICAL.value)
        # else:
        #     feature_types.append(FeatureType.NUMERIC.value)

        # New code
        feature_types.append(get_type(df, column).value)
        print(column, "done")

    return feature_types


def detect_id(df: pd.DataFrame, column: str) -> bool:
    if column.lower() == "id":
        return True

    real_indices = set()
    for value in df[column]:
        if not isinstance(value, int):
            return False
        else:
            real_indices.add(int(value))

    data_size = len(df[column])
    percent = 95.0          # Measure of level of identity two sets must fulfill to be considered as index sets
    expected_indices = set(range(1, data_size))
    common_part = real_indices.intersection(expected_indices)

    return len(common_part) / data_size * 100 >= percent


def detect_timestamp(df: pd.DataFrame, column: str) -> bool:
    if column.lower() in ["timestamp", "date", "datetime", "date-time"]:
        return True

    first_value = df[column].dropna().iloc[0]
    return isinstance(first_value, str) and is_timestamp(first_value)


def is_timestamp(string: str) -> bool:
    formats = [
        "%Y-%m-%d",        # YYYY-MM-DD
        "%d-%m-%Y",        # DD-MM-YYYY
        "%d.%m.%Y",        # DD.MM.YYYY
        "%m/%d/%Y",        # MM/DD/YYYY
        "%Y-%m-%d %H:%M",  # YYYY-MM-DD HH:MM:SS
        "%d-%m-%Y %H:%M",  # DD-MM-YYYY HH:MM:SS
        "%d.%m.%Y %H:%M",  # DD.MM.YYYY HH:MM:SS
        "%m/%d/%Y %H:%M",  # MM/DD/YYYY HH:MM:SS
        "%H:%M %Y-%m-%d",  # HH:MM:SS YYYY-MM-DD
        "%H:%M %d-%m-%Y",  # HH:MM:SS DD-MM-YYYY
        "%H:%M %d.%m.%Y",  # HH:MM:SS DD.MM.YYYY
        "%H:%M %m/%d/%Y"   # HH:MM:SS MM/DD/YYYY
    ]

    for fmt in formats:
        try:
            datetime.strptime(string, fmt)
            return True
        except ValueError:
            pass

    return False


def get_type(df: pd.DataFrame, column: str) -> FeatureType:
    df_drop_na = df[column].dropna()
    first_value = df_drop_na.iloc[0]
    print("hello!")

    # Customizable parameters
    unique_factor = 2
    unique_threshold = unique_factor * ceil(log2(len(df_drop_na)))
    print("hello!")

    if isinstance(first_value, str):
        non_numeric_chars = [c for c in first_value if not c.isnumeric() and c not in [',', '-']]
        if len(non_numeric_chars) > 0:
            return FeatureType.CATEGORICAL
        else:
            return FeatureType.NUMERIC
    else:
        n_unique = df_drop_na.nunique()
        return FeatureType.NUMERIC if n_unique >= unique_threshold else FeatureType.CATEGORICAL