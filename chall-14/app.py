import os
from flask import Flask, render_template, request, Response

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')
UPLOAD_DIR = '/app/uploads'

os.makedirs(UPLOAD_DIR, exist_ok=True)

with open('/app/flag.txt', 'w') as _f:
    _f.write(FLAG + '\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f or not f.filename:
        return render_template('index.html', message='Nenhum arquivo enviado.')

    filename = f.filename
    if not filename.lower().endswith('.jpg'):
        return render_template('index.html', message='Apenas arquivos .jpg são permitidos.')

    filename = os.path.basename(filename)
    if not filename:
        return render_template('index.html', message='Nome de arquivo inválido.')

    f.save(os.path.join(UPLOAD_DIR, filename))

    return render_template('index.html',
                           message='Upload realizado com sucesso.',
                           file_url=f'download?file={filename}')

@app.route('/download')
def download():
    filename = request.args.get('file', '')
    if not filename:
        return render_template('index.html', message='Parâmetro "file" ausente.'), 400

    if os.path.isabs(filename):
        return render_template('index.html', message='Arquivo não encontrado.'), 404

    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(filepath, 'r', errors='replace') as f:
            content = f.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return render_template('index.html', message='Arquivo não encontrado.'), 404

    return Response(content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
