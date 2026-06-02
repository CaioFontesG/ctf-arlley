import os
from flask import Flask, render_template, request

app = Flask(__name__)
DOCS_DIR = '/app/docs'
FLAG_PATH = '/var/secrets/flag.txt'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    doc = request.args.get('doc', 'terms')
    path = os.path.join(DOCS_DIR, doc)
    try:
        with open(path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = None
        error = f'Documento "{doc}" não encontrado.'
        return render_template('index.html', error=error, doc=doc)
    except Exception as e:
        content = None
        error = str(e)
        return render_template('index.html', error=error, doc=doc)

    return render_template('index.html', content=content, doc=doc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
