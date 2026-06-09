import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
FLAG = os.environ.get('FLAG', 'FLAG_NOT_SET')

USERS = {
    1:  {"nome": "João Silva",       "email": "joao.silva@email.com",    "cpf": "123.456.789-00", "telefone": "(11) 99999-0001", "plano": "Básico"},
    2:  {"nome": "Maria Souza",      "email": "maria.souza@email.com",   "cpf": "987.654.321-00", "telefone": "(21) 98888-0002", "plano": "Premium"},
    3:  {"nome": "Carlos Lima",      "email": "carlos.lima@email.com",   "cpf": "111.222.333-44", "telefone": "(31) 97777-0003", "plano": "Básico"},
    4:  {"nome": "Ana Costa",        "email": "ana.costa@email.com",     "cpf": "555.666.777-88", "telefone": "(41) 96666-0004", "plano": "Premium"},
    5:  {"nome": "Pedro Alves",      "email": "pedro.alves@email.com",   "cpf": "222.333.444-55", "telefone": "(51) 95555-0005", "plano": "Básico"},
    6:  {"nome": "Fernanda Rocha",   "email": "ferocha@email.com",       "cpf": "333.444.555-66", "telefone": "(61) 94444-0006", "plano": "Premium"},
    7:  {"nome": "Admin",            "email": "admin@sistema.interno",   "cpf": "000.000.000-00", "telefone": "N/A",             "plano": FLAG},
}

@app.route('/')
def index():
    return redirect(url_for('perfil', id=1))

@app.route('/perfil')
def perfil():
    try:
        user_id = int(request.args.get('id', 1))
    except ValueError:
        user_id = 1
    user = USERS.get(user_id)
    return render_template('index.html', user=user, user_id=user_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
