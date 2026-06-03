import os
from flask import Flask, render_template, make_response

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.headers['X-Flag'] = FLAG
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
