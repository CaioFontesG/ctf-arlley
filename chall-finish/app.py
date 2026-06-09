import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)
CTFD_URL         = os.environ.get('CTFD_URL', 'http://ctfd:8000')
TOTAL_CHALLENGES = int(os.environ.get('TOTAL_CHALLENGES', '17'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    username = request.form.get('username', '').strip()
    if not username:
        return render_template('index.html', error='Digite seu nome de usuário do CTFd.')

    try:
        r = requests.get(
            f'{CTFD_URL}/api/v1/users',
            params={'q': username, 'field': 'name', 'limit': 1000},
            timeout=5,
        )
        r.raise_for_status()
        users = r.json().get('data', [])
    except Exception:
        return render_template('index.html', error='Não foi possível conectar ao CTFd. Tente novamente.')

    user = next((u for u in users if u['name'].lower() == username.lower()), None)
    if not user:
        return render_template('index.html', error=f'Usuário "{username}" não encontrado no CTFd.')

    try:
        r = requests.get(f'{CTFD_URL}/api/v1/users/{user["id"]}/solves', timeout=5)
        r.raise_for_status()
        solves = r.json().get('data', [])
    except Exception:
        return render_template('index.html', error='Não foi possível verificar as conquistas. Tente novamente.')

    solve_count = len(solves)
    return render_template('result.html',
                           username=user['name'],
                           completed=solve_count >= TOTAL_CHALLENGES,
                           solve_count=solve_count,
                           total=TOTAL_CHALLENGES)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
