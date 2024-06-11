import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
import csv

from backend.app.data_normalization import DataNormalizer
from flow import DataFlow
from data_loading import DataProvider
from types_extraction import FeatureTypeExtractor, FeatureTypeSerializer, FeatureType
from data_selection import DataSelector, DataSerializer, parse_ranges
from pca import PcaAnalyzer, PcaPlotter, FeatureBank, FeatureSelector


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
        flow.set_processor("serialize_f_types", FeatureTypeSerializer())
        flow.set_processor("serialize_data_1", DataSerializer(input_name="df"))
        flow.set_processor("serialize_data_2", DataSerializer(input_name="df_normalized"))  # Remember to set a correct name!

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

    return jsonify(length=row_amt,columns=cols, types=serialized_feature_types, data=serialized_data, error=False),200


# It's possible to extend this functionality to edit the column names, but as we know, this is an optional feature :)
@app.route("/data/update", methods=['PUT'])
def update_data():
    # Update feature types
    new_types = request.get_json()
    if not new_types:
        return jsonify({"error": "Invalid input"}), 400
    if isinstance(new_types, list) and all(isinstance(item, int) for item in new_types):
        # Load to "extract_f_types" node's memory
        feature_types = [FeatureType(t) for t in new_types]
        flow.save_memory("extract_f_types", feature_types)
        return jsonify({"received": new_types}), 200
    else:
        return jsonify({"error": "Data should be a list of integers"}), 400


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

@app.route("/data/clusterize", methods=['GET'])
def clusterize_data():
    ...

@app.route("/data/clusterize/cluster_plot", methods=['POST'])
def plot_clusters():
    ...


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
