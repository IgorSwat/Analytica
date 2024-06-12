import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, OPTICS
from sklearn.metrics import silhouette_score as shs
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import io
import base64


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
        # TODO: add PCA
        df_normalized = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)

        pca = self.extract_arg(kwargs, "pca_data", np.ndarray)
        if df_normalized is None:
            return None

        df_copy: pd.DataFrame = df_normalized.copy()
        params = None

        params = self.find_best_params_cluster(pca, self.cluster_method)
        df_copy["Class"] = params["best_labels"]

        return (df_copy, params)

    def __debbug_class(self, data):
        new_data = [1, 2, 3] * 30 + [4] * 20
        np.random.shuffle(new_data)

        data = {"kolumna_kategorii": [1, 2, 3, 4] + new_data}
        df = pd.DataFrame(data)

        # Skalowanie danych
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[["kolumna_kategorii"]])
        scaled_data = np.array(
            [
                [
                    1.79276228,
                    0.31981877,
                    -1.21090716,
                    0.31910894,
                    1.20241874,
                    -1.07486725,
                    -1.49876045,
                    -0.93532085,
                    1.57422674,
                    -1.29311266,
                    2.98768075,
                    -0.97542984,
                    2.49573253,
                    -0.90308144,
                    -1.8631027,
                    -0.1283429,
                    3.71229062,
                    -0.74173547,
                    1.48633775,
                    -1.56635032,
                    -1.06990453,
                    -3.07245271,
                    -3.51392582,
                    1.7034762,
                    2.11037837,
                    3.25562525,
                    -1.06851086,
                    0.83228577,
                    2.87142709,
                    -0.35743958,
                    -1.08897199,
                    -2.11052118,
                    -3.22668036,
                    3.56902693,
                    2.79703077,
                    1.9460592,
                    -0.58876499,
                    3.3266728,
                    4.31208106,
                    1.79067676,
                    -1.17197905,
                    -2.10227855,
                    0.21963484,
                    0.79694344,
                    1.75373601,
                    -2.98239545,
                    1.59381407,
                    1.82548311,
                    -0.62483782,
                    -1.21033533,
                    0.96366347,
                    -1.61330878,
                    0.28826046,
                    -1.08538669,
                    -1.78998265,
                    1.5061013,
                    1.28934217,
                    3.73210836,
                    -2.52679271,
                    -0.6516782,
                    3.46292409,
                    -1.63022721,
                    1.46327398,
                    3.44364567,
                    3.13132824,
                    2.02724597,
                    0.32252993,
                    -1.37377685,
                    -1.79281826,
                    -1.12442276,
                    3.06893467,
                    1.67586998,
                    -0.6516782,
                    -0.96767581,
                    -0.93791157,
                    -3.35415438,
                    -1.87251998,
                    -1.05367747,
                    -1.23333797,
                    -1.94926692,
                    2.36553038,
                    -2.81196433,
                    -2.54453544,
                    -1.20339313,
                    0.78020649,
                    -1.88924437,
                    -1.1960918,
                    -1.21090716,
                    -0.52536372,
                    0.68572154,
                    -0.46502779,
                    1.97539499,
                    -3.25739187,
                    -1.50482761,
                    2.029958,
                    -0.95456991,
                    -1.64963283,
                    0.67099748,
                    -2.51745425,
                    -1.75873607,
                ],
                [
                    0.47422352,
                    -0.06924601,
                    -1.0361919,
                    0.29384464,
                    0.65079231,
                    -0.48914144,
                    0.35688926,
                    -1.19068237,
                    0.07048566,
                    -1.33877317,
                    -0.17763381,
                    -1.07800043,
                    0.07697995,
                    -0.58857001,
                    1.09865781,
                    -0.46264715,
                    -0.3802908,
                    -1.54402431,
                    1.31707324,
                    0.27820279,
                    0.35729346,
                    -0.54569016,
                    -0.37154153,
                    -0.29590999,
                    0.72156032,
                    0.16870588,
                    -1.31939462,
                    0.19368119,
                    -0.35760323,
                    -1.04523542,
                    0.04422996,
                    0.3762856,
                    0.12242961,
                    -0.75639735,
                    -0.28753827,
                    -0.82751557,
                    0.84376441,
                    0.41675534,
                    -0.30897356,
                    0.16538864,
                    -1.23618512,
                    0.33100353,
                    0.34633384,
                    0.15549407,
                    0.70173719,
                    -0.55962659,
                    0.57920192,
                    0.40365882,
                    -1.40862101,
                    0.46330047,
                    1.27662338,
                    0.06559512,
                    -0.17955492,
                    -0.52591107,
                    1.13597899,
                    0.19188205,
                    0.91434276,
                    -0.70092687,
                    0.95258551,
                    -1.55796074,
                    0.17396234,
                    0.3850374,
                    1.53401451,
                    -0.51246314,
                    0.21977761,
                    0.01586557,
                    -0.07316215,
                    0.73529267,
                    0.07399805,
                    -0.14947389,
                    -0.48402217,
                    1.25064716,
                    -1.55796074,
                    0.77492894,
                    -0.70073588,
                    -0.16382421,
                    1.13721081,
                    -1.61571108,
                    -0.26428827,
                    2.19441156,
                    0.14209997,
                    0.57984634,
                    1.37044189,
                    -0.98656799,
                    0.39707671,
                    -0.57553095,
                    0.68414432,
                    -1.0361919,
                    -1.46111021,
                    0.67061178,
                    -1.35500769,
                    -0.13761421,
                    -0.21239707,
                    0.40928807,
                    0.01194899,
                    0.85895158,
                    0.43811573,
                    0.29120024,
                    1.0449548,
                    0.98704069,
                ],
            ]
        )
        # dbscan_dict = self.find_best_params_cluster(scaled_data, 'dbscan')
        # kmeans_dict = self.find_best_params_cluster(scaled_data, 'k-means')
        hierarchy_dict = self.find_best_params_cluster(scaled_data, "hierarchy")
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


class ClusterPlotter(Processor):
    # Customizable parameters
    available_plots = [
        ("k-means", 2),
        ("dbscan", 2),
        ("hierarchy", 2),
    ]  # plot_name and n_components
    plot_size = (9, 7)

    def __init__(self, pca, plot_id=0):
        super().__init__()

        plot_id = plot_id % len(self.available_plots)
        self.pca = pca
        self.plot_type = self.available_plots[plot_id][0]

    def __ne__(self, other):
        return self.plot_type != other.plot_type

    def __call__(self, *args, **kwargs):
        # Draw plot
        df, _ = self.extract_arg(kwargs, "df_clustered", tuple)
        # pca = self.extract_arg(kwargs, "pca_data", np.ndarray)

        if df is None:
            return None

        df_copy: pd.DataFrame = df.copy()

        n_clusters = max(df_copy["Class"])
        colors = self.__get_colors_list(n_clusters)

        df_copy["Segment"] = df_copy["Class"].map(self.__get_clusters_name(n_clusters))
        # print(self.pca)
        self.__draw_plot(df_copy, self.pca, colors, self.plot_type)

        # Save plot as bytes
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()
        return base64.b64encode(img.read()).decode("utf-8")

    def __get_colors_list(self, n: int):
        color_list = cm.rainbow(np.linspace(0, 1, n))
        return color_list
        color_dict = {}

        for i in range(n):
            color_dict[i] = color_list[i]

        return color_dict

    def __get_clusters_name(self, n: int):
        new_dict = {}
        for i in range(n):
            new_dict[i] = str(i)

        return new_dict

    def __draw_plot(self, df, pca, colors, title):
        plt.figure(figsize=self.plot_size)
        sns.scatterplot(x=pca[:, 0], y=pca[:, 1], hue=df["Segment"], palette=colors)
        plt.title(title)
        plt.xlabel("Główna składowa 1")
        plt.ylabel("Główna składowa 2")
        plt.grid()

if __name__ == "__main__":
    data_clusterizer = DataClusterizer("k-means")
    # data_clusterizer.__debbug_class([1])
    scaled_data = np.array(
            [
                [
                    1.79276228,
                    0.31981877,
                    -1.21090716,
                    0.31910894,
                    1.20241874,
                    -1.07486725,
                    -1.49876045,
                    -0.93532085,
                    1.57422674,
                    -1.29311266,
                    2.98768075,
                    -0.97542984,
                    2.49573253,
                    -0.90308144,
                    -1.8631027,
                    -0.1283429,
                    3.71229062,
                    -0.74173547,
                    1.48633775,
                    -1.56635032,
                    -1.06990453,
                    -3.07245271,
                    -3.51392582,
                    1.7034762,
                    2.11037837,
                    3.25562525,
                    -1.06851086,
                    0.83228577,
                    2.87142709,
                    -0.35743958,
                    -1.08897199,
                    -2.11052118,
                    -3.22668036,
                    3.56902693,
                    2.79703077,
                    1.9460592,
                    -0.58876499,
                    3.3266728,
                    4.31208106,
                    1.79067676,
                    -1.17197905,
                    -2.10227855,
                    0.21963484,
                    0.79694344,
                    1.75373601,
                    -2.98239545,
                    1.59381407,
                    1.82548311,
                    -0.62483782,
                    -1.21033533,
                    0.96366347,
                    -1.61330878,
                    0.28826046,
                    -1.08538669,
                    -1.78998265,
                    1.5061013,
                    1.28934217,
                    3.73210836,
                    -2.52679271,
                    -0.6516782,
                    3.46292409,
                    -1.63022721,
                    1.46327398,
                    3.44364567,
                    3.13132824,
                    2.02724597,
                    0.32252993,
                    -1.37377685,
                    -1.79281826,
                    -1.12442276,
                    3.06893467,
                    1.67586998,
                    -0.6516782,
                    -0.96767581,
                    -0.93791157,
                    -3.35415438,
                    -1.87251998,
                    -1.05367747,
                    -1.23333797,
                    -1.94926692,
                    2.36553038,
                    -2.81196433,
                    -2.54453544,
                    -1.20339313,
                    0.78020649,
                    -1.88924437,
                    -1.1960918,
                    -1.21090716,
                    -0.52536372,
                    0.68572154,
                    -0.46502779,
                    1.97539499,
                    -3.25739187,
                    -1.50482761,
                    2.029958,
                    -0.95456991,
                    -1.64963283,
                    0.67099748,
                    -2.51745425,
                    -1.75873607,
                ],
                [
                    0.47422352,
                    -0.06924601,
                    -1.0361919,
                    0.29384464,
                    0.65079231,
                    -0.48914144,
                    0.35688926,
                    -1.19068237,
                    0.07048566,
                    -1.33877317,
                    -0.17763381,
                    -1.07800043,
                    0.07697995,
                    -0.58857001,
                    1.09865781,
                    -0.46264715,
                    -0.3802908,
                    -1.54402431,
                    1.31707324,
                    0.27820279,
                    0.35729346,
                    -0.54569016,
                    -0.37154153,
                    -0.29590999,
                    0.72156032,
                    0.16870588,
                    -1.31939462,
                    0.19368119,
                    -0.35760323,
                    -1.04523542,
                    0.04422996,
                    0.3762856,
                    0.12242961,
                    -0.75639735,
                    -0.28753827,
                    -0.82751557,
                    0.84376441,
                    0.41675534,
                    -0.30897356,
                    0.16538864,
                    -1.23618512,
                    0.33100353,
                    0.34633384,
                    0.15549407,
                    0.70173719,
                    -0.55962659,
                    0.57920192,
                    0.40365882,
                    -1.40862101,
                    0.46330047,
                    1.27662338,
                    0.06559512,
                    -0.17955492,
                    -0.52591107,
                    1.13597899,
                    0.19188205,
                    0.91434276,
                    -0.70092687,
                    0.95258551,
                    -1.55796074,
                    0.17396234,
                    0.3850374,
                    1.53401451,
                    -0.51246314,
                    0.21977761,
                    0.01586557,
                    -0.07316215,
                    0.73529267,
                    0.07399805,
                    -0.14947389,
                    -0.48402217,
                    1.25064716,
                    -1.55796074,
                    0.77492894,
                    -0.70073588,
                    -0.16382421,
                    1.13721081,
                    -1.61571108,
                    -0.26428827,
                    2.19441156,
                    0.14209997,
                    0.57984634,
                    1.37044189,
                    -0.98656799,
                    0.39707671,
                    -0.57553095,
                    0.68414432,
                    -1.0361919,
                    -1.46111021,
                    0.67061178,
                    -1.35500769,
                    -0.13761421,
                    -0.21239707,
                    0.40928807,
                    0.01194899,
                    0.85895158,
                    0.43811573,
                    0.29120024,
                    1.0449548,
                    0.98704069,
                ],
            ]
        )

    print(scaled_data.reshape((100, 2)).shape)
    # print(find_best_params_cluster(scaled_data.reshape((100, 2))))
