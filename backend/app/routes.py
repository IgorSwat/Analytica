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
    rowAmt = df.shape[0]
    cols = df.columns.values.tolist()
    head = df.head(5).values.tolist()
    tail = df.tail(5).values.tolist()
    head = [[str(x) for x in row] for row in head]
    tail = [[str(x) for x in row] for row in tail]
    return jsonify(length=rowAmt,columns=cols,head=head,tail=tail),200
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
