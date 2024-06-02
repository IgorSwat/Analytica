import pandas as pd
import numpy as np
from flask import Flask, request, session, redirect, make_response, jsonify, send_file, render_template
from flask_cors import CORS, cross_origin
from io import StringIO
import sys
import csv

from data_selection import parse_ranges, merge_ranges

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = "TEST"

df = pd.DataFrame()


@app.route('/upload', methods=["POST"])
def upload_file():
    global df
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
        return jsonify(length=row_amt, columns=cols, data=[], error=True),200

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

    return jsonify(length=row_amt,columns=cols,data=data, error=False),200
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
