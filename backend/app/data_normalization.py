import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder

from processor_base import Processor
from types_extraction import FeatureType


available_numeric_methods = ["standard", "min-max", "robust"]


class DataNormalizer(Processor):

    def __init__(self, numeric_method: str = "standard"):
        super().__init__()

        if numeric_method not in available_numeric_methods:
            print("[DataNormalizer] Invalid numeric normalization method: " + numeric_method)
            print("[DataNormalizer] Setting standard normalization method...")
            self.numeric_method = "standard"
        else:
            self.numeric_method = numeric_method


    # We define this method for each "replaceable" processor to optimize it's replacements and data flow process
    # ( Look at set_processor() method from flow.py for more details )
    def __ne__(self, other):
        return self.numeric_method != other.numeric_method


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df", pd.DataFrame)
        f_types = self.extract_arg(kwargs, "f_types", list)
        if df is None or f_types is None:
            return None

        df_copy = df.copy()
        for i, col in enumerate(df.columns):
            if f_types[i] == FeatureType.NUMERIC:
                df_copy[col] = self.normalize_numeric(df_copy[[col]])
            elif f_types[i] == FeatureType.CATEGORICAL:
                df_copy[col] = self.normalize_categorical(df_copy[[col]])

        # Warning - this is optional and may be remover depending on future requirements
        # Remove 'none' type columns (like IDs or timestamps)
        none_type_features = [i for i in range(len(f_types)) if f_types[i] == FeatureType.NONE]
        df_copy = df_copy.drop(df_copy.columns[none_type_features], axis=1)

        return df_copy


    def normalize_numeric(self, data):
        if self.numeric_method == "standard":
            scaler = StandardScaler()
        elif self.numeric_method == "min-max":
            scaler = MinMaxScaler()
        else:
            scaler = RobustScaler()
        return scaler.fit_transform(data)


    def normalize_categorical(self, data):
        encoder = OneHotEncoder(sparse_output=False, drop="first")
        return encoder.fit_transform(data)