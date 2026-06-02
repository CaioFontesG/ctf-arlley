import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return (
        "User-agent: *\n"
        "Disallow: /backup\n"
        "Disallow: /.git\n"
    ), 200, {'Content-Type': 'text/plain'}

@app.route('/.git/config')
def git_config():
    return (
        "[core]\n"
        "\trepositoryformatversion = 0\n"
        "\tfilemode = true\n"
        "\tbare = false\n"
        "[remote \"origin\"]\n"
        "\turl = git@github.com:internal/webapp-prod.git\n"
        "\tfetch = +refs/heads/*:refs/remotes/origin/*\n"
        "[branch \"main\"]\n"
        "\tremote = origin\n"
        "\tmerge = refs/heads/main\n"
    ), 200, {'Content-Type': 'text/plain'}

@app.route('/api')
def api():
    return jsonify({"status": "ok", "version": "1.4.2", "env": "production"})

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/backup')
def backup():
    return render_template('flag.html', flag=FLAG)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
