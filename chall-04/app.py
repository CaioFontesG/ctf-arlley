import os
from flask import Flask, render_template, request

app = Flask(__name__)
FLAG       = os.environ.get('FLAG', 'FLAG_NOT_SET')
PRECO_REAL = 99.90

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/comprar', methods=['POST'])
def comprar():
    try:
        preco = float(request.form.get('preco', PRECO_REAL))
    except ValueError:
        preco = PRECO_REAL

    if preco < 1.0:
        return render_template('flag.html', flag=FLAG, preco=preco)

    return render_template('index.html',
                           aviso=f'Compra de R$ {preco:.2f} processada. Mas a flag não está aqui...')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
