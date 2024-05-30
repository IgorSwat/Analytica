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

df = {}

@app.route('/upload', methods=["POST"])
def uploadFile():

    f = request.files.get('file')
 
    dialect = csv.Sniffer().sniff(f.stream.readline().decode('utf-8'))
    
    df["data"] = pd.read_csv(filepath_or_buffer=f, delimiter=dialect.delimiter)
    df["delimiter"] = dialect.delimiter

    return jsonify({"message": dialect.delimiter}) 
    

if __name__ == "__main__":
    app.run(debug=True, host="localhost")
