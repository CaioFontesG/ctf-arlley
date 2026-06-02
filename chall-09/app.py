import sqlite3
import os
from flask import Flask, render_template, request, g

app = Flask(__name__)
FLAG    = os.environ.get('FLAG', 'FLAG_NOT_SET')
DB_PATH = '/tmp/chall07.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)"
        )
        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?)",
            [
                (1, 'Teclado Mecânico',  'Switch red, RGB, anti-ghosting',   299.90),
                (2, 'Mouse Gamer',       'DPI ajustável, 6 botões, wireless', 189.90),
                (3, 'Monitor 24"',       'Full HD, 144Hz, IPS',              1299.00),
                (4, 'Headset USB',       'Surround 7.1, cancelamento de ruído', 249.90),
                (5, 'Webcam HD',         '1080p, microfone integrado',         149.90),
            ]
        )
        conn.execute(
            "CREATE TABLE admin_secrets (id INTEGER PRIMARY KEY, secret_name TEXT, secret_value TEXT)"
        )
        conn.execute(
            "INSERT INTO admin_secrets VALUES (1, 'flag', ?)", (FLAG,)
        )
        conn.commit()
        conn.close()

@app.before_request
def before_request():
    init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    q = request.args.get('q', '')
    if not q:
        return render_template('index.html')

    db = get_db()
    query = f"SELECT id, name, description, price FROM products WHERE name LIKE '%{q}%'"
    try:
        rows = db.execute(query).fetchall()
        results = [dict(r) for r in rows]
        error = None
    except Exception as e:
        results = []
        error = str(e)

    return render_template('index.html', q=q, results=results, error=error, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
