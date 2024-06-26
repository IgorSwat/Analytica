import io
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from math import ceil
from enum import Enum
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score

from app.data_flow.processor_base import Processor


class ClusteringQuality(Enum):
    BAD = 1
    MID = 2
    GOOD = 3
    EXCELLENT = 4


# PROCESSOR
# Performs given clustering and returns cluster labels
class DataClusterizer(Processor):

    available_methods = ["k-means", "dbscan", "agglomerate"]

    def __init__(self, clustering_method : str = "k-means", first_param=None, second_param=None):
        super().__init__()

        if clustering_method not in self.available_methods:
            print("[DataClusterizer] Invalid clustering method: " + clustering_method)
            print("[DataClusterizer] Setting 'k-means' clustering method...")
            self.clustering_method = "k-means"
        else:
            self.clustering_method = clustering_method

        self.first_param = first_param
        self.second_param = second_param


    def __ne__(self, other):
        return (self.clustering_method != other.clustering_method or
                self.first_param != other.first_param or
                self.second_param != other.second_param)


    def __call__(self, *args, **kwargs):
        _, df = self.extract_arg(kwargs, "pca_data", tuple)
        if df is None:
            return None

        if self.clustering_method == "k-means":
            labels = self.__perform_kmeans(df)
        elif self.clustering_method == "dbscan":
            labels = self.__perform_dbscan(df)
        else:
            labels = self.__perform_agglomerate(df)
        if labels is None:
            print("[DataClusterizer]: " + self.error)

        return labels


    def __perform_kmeans(self, df: pd.DataFrame):
        if self.first_param is None or not isinstance(self.first_param, int):
            return self.set_error(f"Invalid value for 'n_clusters' param: {self.first_param}")

        kmeans = KMeans(n_clusters=self.first_param)
        kmeans.fit(df)

        return kmeans.labels_


    def __perform_dbscan(self, df: pd.DataFrame):
        if self.first_param is None or not isinstance(self.first_param, float):
            return self.set_error(f"Invalid value for 'eps' param: {self.first_param}")
        if self.second_param is None or not isinstance(self.second_param, int):
            return self.set_error(f"Invalid value for 'min_samples' param: {self.second_param}")

        dbscan = DBSCAN(eps=self.first_param, min_samples=self.second_param)
        labels = dbscan.fit_predict(df)

        return labels


    def __perform_agglomerate(self, df: pd.DataFrame):
        if self.first_param is None or not isinstance(self.first_param, int):
            return self.set_error(f"Invalid value for 'n_clusters' param: {self.first_param}")
        if self.second_param is None or not isinstance(self.second_param, str):
            return self.set_error(f"Invalid value for 'linkage' param: {self.second_param}")

        agg_clustering = AgglomerativeClustering(n_clusters=self.first_param, linkage=self.second_param)
        labels = agg_clustering.fit_predict(df)

        return labels


# PROCESSOR
# Calculates statistics measuring clusters` quality
class ClusterAnalyzer(Processor):

    def __init__(self):
        super().__init__()


    def __call__(self, *args, **kwargs):
        # df after PCA transformation
        _, df = self.extract_arg(kwargs, "pca_data", tuple)
        labels = self.extract_arg(kwargs, "labels", np.ndarray)
        if df is None or labels is None:
            return None

        try:
            silhouette = self.__compute_silhouette(df, labels)
            davies_bouldin = self.__compute_davies_bouldin(df, labels)
        except ValueError:
            silhouette = 0
            davies_bouldin = 999.9
        quality = self.__get_clusters_quality(silhouette, davies_bouldin)

        return silhouette, davies_bouldin, quality


    def __compute_silhouette(self, df, labels):
        return silhouette_score(df, labels)


    def __compute_davies_bouldin(self, df, labels):
        return davies_bouldin_score(df, labels)


    # sh for silhouette and db for Davies-Bouldin
    def __get_clusters_quality(self, sh_score, db_score) -> ClusteringQuality:
        score = 0.0

        # Compute average quality of both metrics
        if sh_score <= 0.25:
            score += 0.5 * ClusteringQuality.BAD.value
        elif sh_score <= 0.5:
            score += 0.5 * ClusteringQuality.MID.value
        elif sh_score <= 0.7:
            score += 0.5 * ClusteringQuality.GOOD.value
        else:
            score += 0.5 * ClusteringQuality.EXCELLENT.value

        if db_score > 2.0:
            score += 0.5 * ClusteringQuality.BAD.value
        elif db_score > 1.0:
            score += 0.5 * ClusteringQuality.MID.value
        elif db_score > 0.5:
            score += 0.5 * ClusteringQuality.GOOD.value
        else:
            score += 0.5 * ClusteringQuality.EXCELLENT.value

        return ClusteringQuality(ceil(score))


# PROCESSOR
# Visualizes clustering with plots and returns plot binary data
class ClusterPlotter(Processor):

    plot_size = (10, 9)

    def __init__(self, clustering_label: str = "k-means"):
        super().__init__()
        self.clustering_label = clustering_label


    def __ne__(self, other):
        return self.clustering_label != other.clustering_label


    def __call__(self, *args, **kwargs):
        _, df = self.extract_arg(kwargs, "pca_data", tuple)
        labels = self.extract_arg(kwargs, "labels", np.ndarray)
        if df is None or labels is None:
            return None

        n_features = df.shape[1]
        if n_features == 1:
            self.__draw_empty_scatter()
        elif n_features == 2:
            self.__draw_scatter_2d(df, labels)
        else:
            self.__draw_scatter_3d(df, labels)

        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        return base64.b64encode(img.read()).decode("utf-8")


    def __draw_scatter_2d(self, df, labels):
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1], c=labels, cmap="rainbow")
        plt.xlabel('Cecha 1')
        plt.ylabel('Cecha 2')
        plt.title(f"Klasteryzacja {self.clustering_label}")
        plt.grid()


    def __draw_scatter_3d(self, df, labels):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(df.iloc[:, 0], df.iloc[:, 1], df.iloc[:, 2], c=labels, cmap="rainbow")
        ax.set_xlabel('Cecha 1')
        ax.set_ylabel('Cecha 2')
        ax.set_zlabel('Cecha 3')
        plt.title(f"Klasteryzacja {self.clustering_label}")


    def __draw_empty_scatter(self):
        fig, ax = plt.subplots()
        ax.set_title('Pusty wykres - dane o niedostatecznej wymiarowości')
        ax.set_xlabel('Cecha 1')
        ax.set_ylabel('Cecha 2')
        ax.set_xlim(0, self.plot_size[0])
        ax.set_ylim(0, self.plot_size[1])