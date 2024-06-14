import io
import base64
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA

from app.data_flow.processor_base import Processor


# PROCESSOR
# Main PCA processor to transform data and extract statistics
class PcaTransformer(Processor):

    # Allows to choose the number of components
    def __init__(self, n_components=2):
        super().__init__()
        self.n_components = n_components
        self.pca = PCA(n_components=n_components)


    def __ne__(self, other):
        return self.n_components != other.n_components


    def __call__(self, *args, **kwargs):
        df = self.extract_arg(kwargs, "df_normalized", pd.DataFrame)
        if df is None:
            return None

        # Perform PCA transformation
        data_transformed = self.pca.fit_transform(df)
        df_transformed = pd.DataFrame(data_transformed, columns=[f"PC{i+1}" for i in range(self.n_components)])

        return self.pca, df_transformed


# PROCESSOR
# Draws various types of plots to visualize PCA and returns them as binary data
class PcaPlotter(Processor):

    # Customizable parameters
    available_plots = ["scatter-2D", "heatmap", "screeplot"]     # plot_names
    plot_size = (8, 8)

    # Allows you to specify plot type by given id and feature_labels
    def __init__(self, plot_id=0, feature_labels=None):
        super().__init__()

        plot_id = plot_id % len(self.available_plots)
        self.plot_type = self.available_plots[plot_id]
        self.feature_labels = feature_labels


    def __ne__(self, other):
        return self.plot_type != other.plot_type


    def __call__(self, *args, **kwargs):
        pca, df = self.extract_arg(kwargs, "pca_data", tuple)
        if pca is None or df is None:
            return None

        n_components = pca.components_.shape[0]
        loadings = pca.components_.T
        explained_variance = pca.explained_variance_ratio_

        # Draw plot
        if self.plot_type == "scatter-2D":
            if n_components < 2:
                self.__draw_empty_scatter()
            else:
                self.__draw_scatter_2d(df)
        elif self.plot_type == "heatmap":
            if loadings is None:
                return self.set_error("Invalid PCA statistics returned from PCA transformation")
            self.__draw_heatmap(n_components, loadings)
        else:
            if explained_variance is None:
                return self.set_error("Invalid PCA statistics returned from PCA transformation")
            self.__draw_screeplot(explained_variance)

        # Save plot as bytes
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plt.close()

        return base64.b64encode(img.read()).decode("utf-8")


    def __draw_scatter_2d(self, df_transformed):
        plt.figure(figsize=self.plot_size)
        plt.scatter(df_transformed["PC1"], df_transformed["PC2"], s=50)
        plt.title("PCA - Dwie pierwsze główne składowe")
        plt.xlabel("Główna składowa 1")
        plt.ylabel("Główna składowa 2")
        plt.grid()


    def __draw_heatmap(self, n_components, loadings):
        plt.figure(figsize=self.plot_size)
        labels = self.feature_labels if self.feature_labels is not None else [f"Label {i+1}" for i in range(loadings.shape[0])]
        sns.heatmap(loadings, annot=True, cmap="coolwarm",
                    xticklabels=labels,
                    yticklabels=[f"PC{i+1}" for i in range(n_components)])
        plt.title("Heatmapa współczynników obciążenia (Loading Factors)")
        plt.xlabel("Cechy")
        plt.ylabel("Główne składowe")


    # Might cause some errors
    def __draw_screeplot(self, explained_variance):
        plt.figure(figsize=self.plot_size)
        plt.plot(np.arange(1, len(explained_variance) + 1), explained_variance, marker='o', linestyle='--', color='b')
        plt.title('Stosunek wyjaśnialnej wariancji składowych głównych')
        plt.xlabel('Składowa główna')
        plt.ylabel('Współczynnik wyjaśnialnej wariancji')
        plt.xticks(np.arange(1, len(explained_variance) + 1))
        plt.grid()


    def __draw_empty_scatter(self):
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.plot_size[0])
        ax.set_ylim(0, self.plot_size[1])
        ax.set_title("PCA - Dwie pierwsze główne składowe")
        ax.set_xlabel("Główna składowa 1")
        ax.set_ylabel("Główna składowa 2")
        plt.grid()