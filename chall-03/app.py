import os
from flask import Flask, render_template, request

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    if username == 'admin' and password == 'admin':
        return render_template('flag.html', flag=FLAG)
    return render_template('index.html', error='Credenciais inválidas.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
