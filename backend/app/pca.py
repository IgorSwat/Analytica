import io
import base64
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from processor_base import Processor


# Base class for all PCA-like nodes
class PcaTransformer(Processor):

    # Allows to choose the number of components, as well as choose between fit and fit_transform
    def __init__(self, n_components=None, transform=False):
        super().__init__()
        self.n_components = n_components
        self.transform = transform
        self.pca = PCA(n_components=n_components) if n_components is not None else PCA()


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)
        if df is None:
            return None

        if self.transform:
            return self.pca.fit_transform(df)
        else:
            self.pca.fit(df)
            return None


# PROCESSOR
# Draws various types of plots to visualize PCA and returns them as binary data
class PcaPlotter(PcaTransformer):

    # Customizable parameters
    available_plots = [("scatter-2D", 2), ("heatmap", None), ("screeplot", 2)]     # plot_name and n_components
    plot_size = (9, 7)

    def __init__(self, plot_id=0):
        plot_id = plot_id % len(self.available_plots)

        super().__init__(n_components=self.available_plots[plot_id][1], transform=True)
        self.plot_type = self.available_plots[plot_id][0]


    def __ne__(self, other):
        return self.plot_type != other.plot_type


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)
        principal_components = super().__call__(*args, **kwargs)
        if df is None or principal_components is None:
            return None

        loadings = self.pca.components_
        explained_variance = self.pca.explained_variance_ratio_

        # Draw plot
        if self.plot_type == "scatter-2D":
            if principal_components is None:
                return self.set_error("Invalid configuration for plot: " + self.plot_type)
            self.__draw_scatter_2d(principal_components)
        elif self.plot_type == "heatmap":
            if loadings is None:
                return self.set_error("Invalid configuration for plot: " + self.plot_type)
            self.__draw_heatmap(df.columns.values.tolist(), loadings)
        else:
            if principal_components is None or loadings is None:
                return self.set_error("Invalid configuration for plot: " + self.plot_type)
            self.__draw_screeplot(explained_variance)

        # Save plot as bytes
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        return base64.b64encode(img.read()).decode("utf-8")


    def __draw_scatter_2d(self, principal_components):
        plt.figure(figsize=self.plot_size)
        plt.scatter(principal_components[:, 0], principal_components[:, 1], s=50)
        plt.title("PCA - Dwie pierwsze główne składowe")
        plt.xlabel("Główna składowa 1")
        plt.ylabel("Główna składowa 2")
        plt.grid()


    def __draw_heatmap(self, feature_labels, loadings):
        plt.figure(figsize=self.plot_size)
        sns.heatmap(loadings, annot=True, cmap="coolwarm",
                    xticklabels=feature_labels,
                    yticklabels=[f"PC{i+1}" for i in range(loadings.shape[0])])
        plt.title("Heatmapa współczynników obciążenia (Loading Factors)")
        plt.xlabel("Cechy")
        plt.ylabel("Główne składowe")


    # Might cause some errors
    def __draw_screeplot(self, explained_variance):
        plt.figure(figsize=self.plot_size)
        plt.plot(np.arange(1, len(explained_variance) + 1), explained_variance, marker='o', linestyle='--', color='b')
        plt.title('Scree Plot')
        plt.xlabel('Składowa główna')
        plt.ylabel('Współczynnik wyjaśnialnej wariancji')
        plt.xticks(np.arange(1, len(explained_variance) + 1))
        plt.grid()


# PROCESSOR
# Returns basic PCA stats as a numpy array
class PcaAnalyzer(PcaTransformer):

    # We assume we calculate loading factors corresponding to 2 main components, you can adjust the parameter
    def __init__(self, no_load_factors=2):
        super().__init__(n_components=no_load_factors, transform=False)
        self.no_components = no_load_factors


    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        df = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)
        if df is None:
            return None

        # Calculate basic stats
        loading_factors = self.pca.components_.T

        # Compose them into one matrix (numpy array)
        results = np.zeros((df.shape[1], 2))
        for i in range(df.shape[1]):
            results[i, 0] = loading_factors[i, 0]
            results[i, 1] = loading_factors[i, 1]

        return results

# TODO: DO DEBBUGA
class OnlyPCA(PcaTransformer):
    def __init__(self, plot_id=0):
        super().__init__(n_components=2, transform=True)

    def __ne__(self, other):
        return self.plot_type != other.plot_type


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)
        principal_components = super().__call__(*args, **kwargs)
        
        if df is None or principal_components is None:
            return None
        
        return principal_components
