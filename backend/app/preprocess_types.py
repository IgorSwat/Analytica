import pandas as pd
from data_properties import FeatureType

def select_types(df: pd.DataFrame) -> list[FeatureType]:
    feature_types = []

    for column in df:
        if column == 'ID' or column == 'Timestamp':
            feature_types.append(FeatureType.NONE.value)
            continue

        numeric_df = df[column].apply(pd.to_numeric, errors='coerce')
        row_nan_count = numeric_df.isna().sum()

        if row_nan_count > int(len(df[column])/2):
            feature_types.append(FeatureType.CATEGORICAL.value)
        else:
            feature_types.append(FeatureType.NUMERIC.value)

    return feature_types