from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
            return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        else:
            return "Invalid file format. Please upload an Excel file."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)