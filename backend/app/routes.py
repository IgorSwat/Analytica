import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import csv


# from backend.app.data_normalization import DataNormalizer
from data_normalization import DataNormalizer
from flow import DataFlow
from data_loading import DataProvider
from types_extraction import FeatureTypeExtractor, FeatureTypeSerializer, FeatureType

from data_selection import DataSelector, FeatureSelector, DataSerializer, parse_ranges
from pca import PcaAnalyzer, PcaPlotter, OnlyPCA
from data_clustering import ClusterPlotter, DataClusterizer


app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "TEST"

# This contains all data and implementation of all data processing methods
flow = DataFlow()


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

        flow.set_processor("raw_data", DataProvider(df))    # You can switch off the comma fixes by using fix_commas=False
        flow.set_processor("extract_f_types", FeatureTypeExtractor())

        # We can apply some of the other processors that do not require any specific parameters
        flow.set_processor("select_data", DataSelector())
        flow.set_processor("select_features_1", FeatureSelector())
        flow.set_processor("serialize_f_types", FeatureTypeSerializer())
        flow.set_processor("serialize_data_1", DataSerializer(input_name="df"))
        flow.set_processor("serialize_data_2", DataSerializer(input_name="df_normalized"))  # Remember to set a correct name!
        flow.set_processor("analyze_pca", PcaAnalyzer())
        flow.set_processor("select_features_2", FeatureSelector(input_name="df_normalized"))
        flow.set_processor("return_pca_data", OnlyPCA())

        # IMPORTANT
        # Process for the first time to load memory in nodes
        flow.process("extract_f_types")
        
        return {"message": "File processed successfully"}

    except Exception as e:
        return {"reason": str(e)}, 500


@app.route("/data/visualize", methods=['GET'])
def visualize_data():
    df = flow.process("raw_data")

    row_amt = df.shape[0]
    cols = df.columns.values.tolist()

    # Process in feature types serialization direction
    serialized_feature_types = flow.process("serialize_f_types")

    selection = request.args.get('selection', default=row_amt, type=str)
    ranges = parse_ranges(selection, row_amt)   # Parse user command
    if ranges is None:                          # If user command is incorrect, return no data
        return jsonify(length=row_amt, columns=cols, types=serialized_feature_types, data=[], error=True),200

    # Apply new processor based on parsed ranges
    flow.set_processor("select_data", DataSelector(ranges))

    # Process in data serialization direction
    serialized_data = flow.process("serialize_data_1")

    # Get feature selection
    states = flow.get_processor("select_features_1").feature_states
    selection = [True for i in range(len(cols))] if states is None else [states[col] for col in cols]

    return jsonify(length=row_amt,columns=cols, types=serialized_feature_types, states=selection, data=serialized_data, error=False),200


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
        feature_types = [FeatureType(t) for t in new_types]
        flow.save_memory("extract_f_types", feature_types)

        # Load new data selection
        selection = {col: new_selection[i] for i, col in enumerate(df.columns)}
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

    # Replace the processor if needed
    flow.set_processor("normalize_data", DataNormalizer(numeric_method))
    results = flow.process("normalize_data")
    if results is None:
        return jsonify({"error": "Unable to normalize given data"}), 400

    row_amt = results.shape[0]
    cols = results.columns.values.tolist()
    results_serialized = flow.process("serialize_data_2")

    return jsonify(length=row_amt, columns=cols, data=results_serialized), 200


@app.route("/data/pca/stats", methods=['GET'])
def get_pca_stats():
    stats = flow.process("analyze_pca")
    df = flow.load_memory("normalize_data")

    if df is None or stats is None:
        return jsonify({"error": "Unable to perform PCA on given data"}), 400

    def serialize_column(column):
        return [str(element) for element in column]

    # Extract and convert separate columns
    cols = df.columns.values.tolist()
    loads1 = serialize_column(stats[:, 0])
    loads2 = serialize_column(stats[:, 1])

    # Update feature selections if needed
    if flow.load_memory("feature_bank") is None:
        # Select 2 most significant features
        indexed_variances = sorted(list(enumerate(stats[:, 0])), key=lambda x: abs(x[1]), reverse=True)
        two_main_components_ids = [item[0] for item in indexed_variances[:2]]
        # Create new selection list and new processor
        auto_selection = {cols[i]: bool(i in two_main_components_ids) for i in range(len(stats[:, 0]))}
        flow.set_processor("select_features_2", FeatureSelector(auto_selection, input_name="df_normalized"))

    states = flow.get_processor("select_features_2").feature_states
    selection = [states[col] for col in cols]

    return jsonify(columns=cols, loads1=loads1, loads2=loads2, selections=selection), 200


@app.route("/data/pca/plot", methods=['GET'])
def get_pca_plot():
    # Obtain plot index
    plot_id = request.args.get("plot_id", default=0, type=int)

    # Generate plot data
    flow.set_processor("plot_pca", PcaPlotter(plot_id))
    binary_data = flow.process("plot_pca")
    if binary_data is None:
        return jsonify({"error": f"Unable to generate plot nr {plot_id}"}), 400

    return jsonify({'image': binary_data}), 200


@app.route("/data/select-features", methods=['PUT'])
def update_feature_selection():
    new_selections = request.get_json()

    if not new_selections:
        return jsonify({"error": "Invalid input"}), 400
    elif isinstance(new_selections, list) and all(isinstance(item, bool) for item in new_selections):
        df = flow.process("normalize_data")
        selection = {col: new_selections[i] for i, col in enumerate(df.columns)}
        flow.set_processor("select_features_2", FeatureSelector(selection, input_name="df_normalized"))
        return jsonify({"received": new_selections}), 200
    else:
        return jsonify({"error": "Data should be a list of boolean values"}), 400


@app.route("/data/cluster/compute", methods=['GET'])
def clusterize_data():
    flow.set_processor("cluster_data", DataClusterizer())

    df_cluster, params = flow.process("cluster_data")
    # print(params['best_num_clusters'])
    pca = flow.load_memory("return_pca_data")

    if df_cluster is None or params is None or pca is None:
        return jsonify({"error": "Unable to perform clustering on given data"}), 400

    def serialize_column(column):
        return [str(element) for element in column]

    # Extract and convert separate columns
    cols = [i for i in range(pca.shape[0])]
    loads1 = serialize_column(pca[:, 0])
    loads2 = serialize_column(pca[:, 1])

    return jsonify(columns=cols, loads1=loads1, loads2=loads2), 200


@app.route("/data/cluster/plot", methods=['GET'])
def plot_clusters():
    plot_id = request.args.get("plot_id", default=0, type=int)
    pca = flow.load_memory("return_pca_data")

    flow.set_processor("plot_cluster", ClusterPlotter(pca, plot_id))
    
    binary_data = flow.process("plot_cluster")
    if binary_data is None:
        return jsonify({"error": f"Unable to generate plot nr {plot_id}"}), 400

    return jsonify({'image': binary_data}), 200
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
