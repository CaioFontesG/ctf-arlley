import os
from flask import Flask, render_template, request

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')
INTERNAL_PREFIXES = ('127.', '10.', '172.16.', '192.168.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    xff = request.headers.get('X-Forwarded-For', '')
    first_ip = xff.split(',')[0].strip()
    if any(first_ip.startswith(p) for p in INTERNAL_PREFIXES):
        return render_template('flag.html', flag=FLAG)
    return render_template('index.html', error=f'Acesso negado. IP detectado: {first_ip or "não informado"}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
