import csv
import pandas as pd
import numpy as np

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO

from app.conversions import df_to_json, f_properties_to_list, f_properties_from_list
from app.state_control import StateHandler
from app.data_flow.data_normalization import DataNormalizer
from app.data_flow.flow import DataFlow
from app.data_flow.data_loading import DataProvider
from app.data_flow.types_extraction import FeatureTypeExtractor, FeatureType
from app.data_flow.data_selection import DataSelector, FeatureSelector
from app.data_flow.pca import PcaTransformer, PcaPlotter
from app.data_flow.data_clustering import DataClusterizer, ClusterAnalyzer, ClusterPlotter


app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "TEST"

# This contains all data and implementation of all data processing methods
flow = DataFlow()

# Control the current state of app
state_handler = StateHandler(flow)


@app.route("/navbar", methods=["GET"])
def get_navbar_state():
    states = state_handler.get_navbar_state()
    return jsonify(states), 200


@app.route('/upload', methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return {"reason" : "No file selected"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"reason" : "File not named"}, 400
    try:
        content = file.stream.read(1024)
        file.stream.seek(0)
        dialect = csv.Sniffer().sniff(content.decode('utf-8'))
        df = pd.read_csv(file, delimiter=dialect.delimiter)

        # Basic nodes required to init data flow
        flow.set_processor("raw_data", DataProvider(df))    # You can switch off the comma fixes by using fix_commas=False
        flow.set_processor("extract_f_types", FeatureTypeExtractor())

        # We can apply some of the other processors with default parameters
        flow.set_processor("select_data", DataSelector())
        flow.set_processor("select_features_1", FeatureSelector())
        flow.set_processor("normalize_data", DataNormalizer())
        flow.set_processor("transform_pca", PcaTransformer())
        flow.set_processor("analyze_clusters", ClusterAnalyzer())
        
        return {"message": "File processed successfully"}

    except Exception as e:
        return {"reason": str(e)}, 500


@app.route("/data/visualize", methods=['GET'])
def visualize_data():
    df = flow.process("raw_data")

    row_amt = df.shape[0]
    cols = df.columns.values.tolist()

    # Process in feature types  direction
    f_types = flow.process("extract_f_types")
    f_types_converted = f_properties_to_list(f_types, df, lambda x: x.value)

    selection_cmd = request.args.get('selection', default=row_amt, type=str)
    selection_cmd = state_handler.correct_input(selection_cmd, "selection", "select_data")
    if selection_cmd is not None:
        flow.set_processor("select_data", DataSelector(selection_cmd))

    # Process in data selection direction
    data = flow.process("select_data")
    if data is None:    # If user command is incorrect, return no data
        states = [True for i in range(len(cols))]
        return jsonify(length=row_amt, columns=cols, types=f_types_converted, states=states, data=[], error=True), 200
    serialized_data = df_to_json(data)

    # Get feature selection
    states = flow.get_processor("select_features_1").feature_states
    selection = [True for i in range(len(cols))] if states is None else f_properties_to_list(states, df)
    selection_cmd = flow.get_processor("select_data").selection_cmd

    return jsonify(length=row_amt,columns=cols, types=f_types_converted, states=selection,
                   data=serialized_data, selection=selection_cmd, error=False),200


# It's possible to extend this functionality to edit the column names, but as we know, this is an optional feature :)
@app.route("/data/update", methods=['PUT'])
def update_data():
    data = request.get_json()
    new_types = data.get("types")
    new_selection = data.get("states")

    if not new_types or not new_selection:
        return jsonify({"error": "Invalid input"}), 400
    elif isinstance(new_types, list) and isinstance(new_selection, list):
        df = flow.process("raw_data")

        # Load to "extract_f_types" node's memory
        feature_types = f_properties_from_list(new_types, df, lambda x: FeatureType(x))
        flow.set_processor("extract_f_types", FeatureTypeExtractor(feature_types))

        # Load new data selection
        selection = f_properties_from_list(new_selection, df)
        flow.set_processor("select_features_1", FeatureSelector(selection))

        return jsonify({"received": new_types}), 200
    else:
        return jsonify({"error": "Data should be a list of integers"}), 400


# Return a CSV object
@app.route("/data/download", methods=['GET'])
def download_data():
    df = flow.process("select_features_1")
    if df is None:
        return jsonify({"error": "No data"}), 400

    csv_data = df.to_csv(index=False)

    return send_file(
        BytesIO(csv_data.encode("utf-8")),
        mimetype='text/csv',
        download_name='data.csv',
        as_attachment=True
    )


@app.route("/data/normalize", methods=['GET'])
def normalize_data():
    # Get normalization type
    numeric_method = request.args.get('numeric_method', default='standard', type=str)
    numeric_method = state_handler.correct_input(numeric_method, "numeric_method", "normalize_data")
    if numeric_method is not None:
        flow.set_processor("normalize_data", DataNormalizer(numeric_method))

    results = flow.process("normalize_data")
    if results is None:
        return jsonify({"error": "Unable to normalize given data"}), 200

    row_amt = results.shape[0]
    cols = results.columns.values.tolist()
    results_serialized = df_to_json(results)
    numeric_method = flow.get_processor("normalize_data").numeric_method

    return jsonify(length=row_amt, columns=cols, data=results_serialized, numericMethod=numeric_method), 200


@app.route("/data/pca", methods=['GET'])
def get_pca_data():
    # Extract and apply n_components parameter
    n_components = request.args.get('n_components', default=2, type=int)
    n_components = state_handler.correct_input(n_components, "n_components", "transform_pca")
    if n_components is not None:
        # Check for invalid input
        df = flow.process("normalize_data")
        if n_components < 1 or n_components > len(df.columns.tolist()):
            return jsonify(row_amt=0, columns=[], data=[], variances=[], noComponents=n_components, error=True), 200
        flow.set_processor("transform_pca", PcaTransformer(n_components=n_components))

    # Perform PCA
    pca, df = flow.process("transform_pca")
    if pca is None or df is None:
        return jsonify({"error": "Unable to perform PCA on given data"}), 200

    # Extract (and convert) response parameters
    row_amt = df.shape[0]
    cols = df.columns.values.tolist()
    data = df_to_json(df)
    variances = pca.explained_variance_.tolist()
    n_components = flow.get_processor("transform_pca").n_components

    return jsonify(row_amt=row_amt, columns=cols, data=data, variances=variances, noComponents=n_components, error=False), 200


@app.route("/data/pca/plot", methods=['GET'])
def get_pca_plot():
    # Obtain plot index
    plot_id = request.args.get("plot_id", default=0, type=int)
    df = flow.process("normalize_data")
    cols = df.columns.values.tolist()
    flow.set_processor("plot_pca", PcaPlotter(plot_id, feature_labels=cols))

    # Generate plot data
    binary_data = flow.process("plot_pca")
    if binary_data is None:
        return jsonify({"error": f"Unable to generate plot nr {plot_id}"}), 200

    return jsonify({'image': binary_data}), 200


@app.route("/data/clustering", methods=['GET'])
def get_clustering_results():
    # Extract parameters and update processors if needed
    clustering_method = request.args.get("clustering_method", default="k-means", type=str)
    clustering_method = state_handler.correct_input(clustering_method, "clustering_method", "cluster_data")
    if clustering_method is not None:
        if clustering_method == "k-means":
            n_clusters = request.args.get("n_clusters", default=2, type=int)
            flow.set_processor("cluster_data",
                               DataClusterizer(clustering_method, first_param=n_clusters))
        elif clustering_method == "dbscan":
            eps = request.args.get("eps", default=1.5, type=float)
            min_samples = request.args.get("min_samples", default=2, type=int)
            flow.set_processor("cluster_data",
                               DataClusterizer(clustering_method, first_param=eps, second_param=min_samples))
        else:
            n_clusters = request.args.get("n_clusters", default=2, type=int)
            linkage = request.args.get("linkage", default="ward", type=str)
            flow.set_processor("cluster_data",
                               DataClusterizer(clustering_method, first_param=n_clusters, second_param=linkage))

    # Get transformed data
    _, df = flow.process("transform_pca")

    # Perform clustering and link results with data
    labels = flow.process("cluster_data")
    if labels is None:
        return jsonify({"error": "Unable to perform clustering"}), 200

    # Perform cluster analysis and obtain rest of the output values
    clustering_method = flow.get_processor("cluster_data").clustering_method
    n_clusters = flow.get_processor("cluster_data").first_param if clustering_method in ["k-means", "agglomerate"] else 1
    eps = flow.get_processor("cluster_data").first_param if clustering_method == "dbscan" else 1.0
    min_samples = flow.get_processor("cluster_data").second_param if clustering_method == "dbscan" else 2
    linkage = flow.get_processor("cluster_data").second_param if clustering_method == "agglomerate" else "ward"
    silhouette, davies_bouldin, quality = flow.process("analyze_clusters")

    row_amt = df.shape[0]

    # Add extra column
    cluster_feature = "Klaster"
    df[cluster_feature] = labels
    row_amt = df.shape[0]
    columns = df.columns.values.tolist()
    data = df_to_json(df)

    # Format labels column
    for i in range(len(data)):
        data[i][-1] = data[i][-1].split('.')[0]

    # Remove the extra column
    df.drop(cluster_feature, axis=1, inplace=True)

    return jsonify(length=row_amt, columns=columns, data=data, clustering_method=clustering_method,
                   n_clusters=n_clusters, eps=eps, min_samples=min_samples, linkage=linkage,
                   silhouette=silhouette, davies_bouldin=davies_bouldin, quality=quality.value), 200


@app.route("/data/clustering/plot", methods=["GET"])
def get_cluster_plot():
    clustering_method = request.args.get("clustering_method", default="k-means", type=str)
    flow.set_processor("plot_clusters", ClusterPlotter(clustering_method))

    # Generate plot data
    binary_data = flow.process("plot_clusters")
    if binary_data is None:
        return jsonify({"error": f"Unable to generate clusters plot"}), 200

    return jsonify({'image': binary_data}), 200


@app.route("/data/clustering/download", methods=["GET"])
def download_cluster_data():
    raw_flag_str = request.args.get("raw_flag", default="true", type=str)
    raw_flag = raw_flag_str.lower() == "true"

    df = flow.process("select_features_1") if raw_flag is True else flow.process("transform_pca")[1]
    labels = flow.process("cluster_data")
    if df is None or labels is None:
        return jsonify({"error": "No data"}), 400

    # Add extra column
    cluster_feature = "Klaster"
    df[cluster_feature] = labels
    csv_data = df.to_csv(index=False)
    result = BytesIO(csv_data.encode("utf-8"))

    # Remove extra column
    df.drop(cluster_feature, axis=1, inplace=True)

    return send_file(
        result,
        mimetype='text/csv',
        download_name='data.csv',
        as_attachment=True
    )


def main():
    app.run(debug=True, host="localhost")

