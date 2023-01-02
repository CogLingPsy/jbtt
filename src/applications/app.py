import os
import sys

from flask import Flask, request, jsonify, redirect

current: str = os.path.dirname(os.path.realpath(__file__))
parent: str = os.path.dirname(current)
grandparent: str = os.path.dirname(parent)
sys.path.append(grandparent)
from src.processing.run_processing import process_text

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def main_page():
    return redirect("http://127.0.0.1:5000/static/index.html", code=302)


@app.post('/api/processText')
def post_process_text():
    """
    Endpoint to process text e.g. in Postman
    """
    data = request.json
    result = process_text(data['text'])
    return jsonify(result)


@app.get('/alive')
def get_status():
    return jsonify('Active')


if __name__ == '__main__':
    app.run()
