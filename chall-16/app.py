import os
from flask import Flask, render_template, request, Response

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    content = (
        "Parabéns! Você identificou uma página de phishing.\n\n"
        "Sinais de alerta que você deveria ter notado:\n"
        "  - A URL não era a do CTFd real\n"
        "  - Nunca insira credenciais sem verificar o endereço na barra do navegador\n\n"
        f"Flag: {FLAG}\n"
    )
    return Response(
        content,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=flag.txt'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
