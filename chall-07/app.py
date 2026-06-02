import os
from flask import Flask, render_template, request

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    q = request.args.get('q', '')
    debug = request.args.get('debug', '').lower() == 'true'
    verbose = request.args.get('verbose', '').lower() == 'true'

    if debug and verbose:
        return render_template('index.html', q=q, flag=FLAG, debug=True, verbose=True)

    if debug:
        return render_template('index.html', q=q, debug=True, verbose=False,
                               hint='Debug mode ativo. Tente adicionar mais parâmetros de diagnóstico.')

    results = [
        {'name': 'Produto Alpha', 'desc': 'Descrição do produto alpha'},
        {'name': 'Produto Beta',  'desc': 'Descrição do produto beta'},
    ] if q else []

    return render_template('index.html', q=q, results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
