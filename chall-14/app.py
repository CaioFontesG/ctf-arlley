import os
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')
UPLOAD_DIR = '/app/uploads'
SHELL_MARKERS = [b'<?php', b'#!/', b'import os', b'exec(', b'eval(', b'system(', b'passthru(']

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('index.html')

    f = request.files.get('file')
    if not f or not f.filename:
        return render_template('index.html', message='Nenhum arquivo enviado.')

    filename = f.filename
    if not filename.lower().endswith('.jpg'):
        return render_template('index.html', message='Apenas arquivos .jpg são permitidos!')

    save_path = os.path.join(UPLOAD_DIR, filename)
    f.save(save_path)

    return render_template('index.html',
                           message=f'Upload concluído.',
                           file_url=f'uploads/{filename}')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        return render_template('index.html', message='Arquivo não encontrado.'), 404

    with open(filepath, 'rb') as f:
        content = f.read(512)

    if any(marker in content for marker in SHELL_MARKERS):
        return render_template('flag.html', filename=filename, flag=FLAG)

    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
