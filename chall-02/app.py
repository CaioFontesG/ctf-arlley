import os
from flask import Flask, render_template

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    return render_template('index.html', flag=FLAG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
