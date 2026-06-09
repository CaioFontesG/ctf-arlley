import os
import subprocess
import time
import jwt
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
FLAG       = os.environ.get('FLAG', 'FLAG_NOT_SET')
JWT_SECRET = 'secret'

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/legacy', methods=['GET', 'POST'])
def legacy():
    if request.method == 'GET':
        return render_template('legacy.html')

    username = request.form.get('username', 'guest')
    payload = {
        'user': username,
        'role': 'user',
        'exp':  int(time.time()) + 3600,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return render_template('legacy.html', token=token, username=username)

@app.route('/management')
def management():
    token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return render_template('index.html', error='Token JWT obrigatório. Acesse /legacy primeiro.'), 401

    claims = decode_token(token)
    if not claims:
        return render_template('index.html', error='Token inválido ou expirado.'), 401

    if claims.get('role') != 'admin':
        return render_template('index.html',
                               error=f'Acesso negado. Role atual: "{claims.get("role")}". Role necessária: "admin".'), 403

    return render_template('management.html', user=claims.get('user'))

@app.route('/management/network')
def network():
    token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    claims = decode_token(token) if token else None
    if not claims or claims.get('role') != 'admin':
        return jsonify({'error': 'Admin JWT obrigatório.'}), 401

    host = request.args.get('host', '')
    if not host:
        return jsonify({'error': 'Parâmetro host obrigatório.'}), 400

    try:
        result = subprocess.run(
            f'ping -c 2 {host}',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        output = 'Timeout.'
    except Exception as e:
        output = str(e)

    return render_template('management.html',
                           user=claims.get('user'),
                           host=host,
                           output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
