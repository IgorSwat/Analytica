import pandas as pd
import numpy as np
from flask import Flask, request, session, redirect, make_response, jsonify, send_file, render_template
from flask_cors import CORS, cross_origin
from io import StringIO
import sys
import csv

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

    n = request.args.get('n', default=row_amt, type=int)
    n = min(n, row_amt)

    data = df.head(n).values.tolist()
    data = [[str(x) for x in row] for row in data]
    return jsonify(length=row_amt,columns=cols,data=data),200
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
