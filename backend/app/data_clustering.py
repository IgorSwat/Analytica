import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, OPTICS
from sklearn.metrics import silhouette_score as shs
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import itertools


def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn

from processor_base import Processor


available_cluster_methods = ["k-means", "dbscan", "hierarchy"]


class DataClusterizer(Processor):

    def __init__(self, cluster_method: str = "k-means", n_clusters: int | None = None):
        super().__init__()

        if cluster_method not in available_cluster_methods:
            print(
                "[DataClusterizer] Invalid numeric normalization method: "
                + cluster_method
            )
            print("[DataClusterizer] Setting k-means cluster analysis method...")
            self.cluster_method = "k-means"
        else:
            self.cluster_method = cluster_method

        self.n_clusters = n_clusters

    # We define this method for each "replaceable" processor to optimize it's replacements and data flow process
    # ( Look at set_processor() method from flow.py for more details )
    def __ne__(self, other):
        return self.cluster_method != other.cluster_method

    def __call__(self, *args, **kwargs):
        df_normalized = self.extract_arg(
            kwargs, "df_normalized", pd.DataFrame
            )

        if df_normalized is None:
            return None

        df_copy: pd.DataFrame = df_normalized.copy()
        params = None

        params = self.find_best_params_cluster(df_copy.values, self.cluster_method)
        df_copy['Class'] = params['best_labels']

        return df_copy, params

    def __debbug_class(self, data):
        new_data = [1, 2, 3] * 30 + [4] * 20
        np.random.shuffle(new_data)

        data = {"kolumna_kategorii": [1, 2, 3, 4] + new_data}
        df = pd.DataFrame(data)

        # Skalowanie danych
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[["kolumna_kategorii"]])

        # dbscan_dict = self.find_best_params_cluster(scaled_data, 'dbscan')
        # kmeans_dict = self.find_best_params_cluster(scaled_data, 'k-means')
        hierarchy_dict = self.find_best_params_cluster(
            scaled_data, 'hierarchy'
        )
        print(hierarchy_dict)

    def find_best_params_cluster(
        self, data: np.ndarray, str_model: str = "k-means"
    ) -> dict | None:
        
        if str_model == "dbscan":
            min_samples = np.arange(2, min(len(data[:, 0]), 25), step=2)
            epsilon = np.linspace(0.01, abs(max(data[:, 0] - min(data[:, 0]))), 30)
            combinations = list(itertools.product(epsilon, min_samples))

        else:
            combinations = np.arange(2, min(len(data[:, 0]), 25), step=2)

        scores = []
        all_labels = []
        num_clusters_list = []

        for i, param in enumerate(combinations):

            if str_model == "k-means":
                model = KMeans(
                    n_clusters=param,
                ).fit(data)

            elif str_model == "dbscan":
                model = DBSCAN(eps=param[0], min_samples=param[1]).fit(data)

            elif str_model == "hierarchy":
                model = AgglomerativeClustering(
                    n_clusters=param, metric="euclidean", linkage="ward"
                ).fit(data)

            else:
                return None

            labels = model.labels_
            labels_set = set(labels)
            num_clusters = len(labels_set)

            if -1 in labels_set:
                num_clusters -= 1
                
            if (num_clusters < 2) or (num_clusters > 25):
                scores.append(-1)
                num_clusters_list.append(-1)
                all_labels.append("Bruh")
                continue

            scores.append(shs(data, labels))
            all_labels.append(labels)
            num_clusters_list.append(num_clusters)

        best_index = np.argmax(scores)

        if str_model == "dbscan":
            best_parameters = combinations[best_index]
            return {
                "best_eps": best_parameters[0],
                "best_min_samples": best_parameters[1],
                "best_labels": all_labels[best_index],
                "best_score": scores[best_index],
                "best_num_clusters": num_clusters_list[best_index],
            }

        else:
            return {
                "best_labels": all_labels[best_index],
                "best_score": scores[best_index],
                "best_num_clusters": num_clusters_list[best_index],
            }


if __name__ == "__main__":
    data_clusterizer = DataClusterizer("k-means")
    data_clusterizer.__debbug_class([1])
