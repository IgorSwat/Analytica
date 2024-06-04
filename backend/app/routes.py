import pandas as pd
import numpy as np
from flask import Flask, request, session, redirect, make_response, jsonify, send_file, render_template
from flask_cors import CORS, cross_origin
from io import StringIO
import sys
import csv

from data_selection import parse_ranges, merge_ranges
from data_properties import FeatureType
from preprocess_types import select_types


app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "TEST"

df = pd.DataFrame()
feature_types = None


@app.route('/upload', methods=["POST"])
def upload_file():
    global df, feature_types

    if 'file' not in request.files:
        return {"reason" : "No file xselected"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"reason" : "File not named"}, 400
    try:
        content = file.stream.read(1024)
        file.stream.seek(0)
        dialect = csv.Sniffer().sniff(content.decode('utf-8'))
        df = pd.read_csv(file, delimiter=dialect.delimiter)

        no_columns = df.shape[1]
        # Only for testing purposes, should be replaced with automatic feature type extraction
        # feature_types = [FeatureType.NUMERIC.value for _ in range(no_columns)]
        # feature_types[0] = FeatureType.NONE.value
        # feature_types[1] = FeatureType.NONE.value
        # feature_types[9] = FeatureType.CATEGORICAL.value
        feature_types = select_types(df)

        return {"message": "File processed successfully"}

    except Exception as e:
        return {"reason": str(e)}, 500


@app.route("/data/visualize", methods=['GET'])
def visualize_data():
    global df
    row_amt = df.shape[0]

    cols = df.columns.values.tolist()

    selection = request.args.get('selection', default=row_amt, type=str)
    ranges = parse_ranges(selection, row_amt)   # Parse user command
    if ranges is None:                          # If user command is incorrect, return no data
        return jsonify(length=row_amt, columns=cols, types=feature_types, data=[], error=True),200

    merged_ranges = merge_ranges(ranges)        # Merge parsed ranges
    data = []
    for data_range in merged_ranges:
        if data_range[1] >= row_amt:            # Be careful to not go beyond df size
            if data_range[0] < row_amt:
                data = data + df.iloc[data_range[0]:row_amt].values.tolist()
            break
        data = data + df.iloc[data_range[0]:data_range[1] + 1].values.tolist()
    if len(data) > 0:
        data = [[str(x) for x in row] for row in data]

    return jsonify(length=row_amt,columns=cols, types=feature_types, data=data, error=False),200


# It's possible to extend this functionality to edit the column names, but as we know, this is an optional feature :)
@app.route("/data/update", methods=['PUT'])
def update_data():
    global df, feature_types

    # Update feature types
    new_types = request.get_json()
    if not new_types:
        return jsonify({"error": "Invalid input"}), 400
    if isinstance(new_types, list) and all(isinstance(item, int) for item in new_types):
        feature_types = new_types
        return jsonify({"received": new_types}), 200
    else:
        return jsonify({"error": "Data should be a list of integers"}), 400
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
