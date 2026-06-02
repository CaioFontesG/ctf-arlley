import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
FLAG    = os.environ.get('FLAG', 'FLAG_NOT_SET')
API_KEY = 'dev-internal-key-2024'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    key = request.args.get('key', '') or request.headers.get('X-Api-Key', '')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'status': 'online', 'env': 'production', 'uptime': '99.97%'})

@app.route('/api/flag')
def api_flag():
    key = request.args.get('key', '') or request.headers.get('X-Api-Key', '')
    if key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'flag': FLAG})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
