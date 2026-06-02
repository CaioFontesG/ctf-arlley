#!/usr/bin/env python3
"""
Popula o CTFd com todos os 10 desafios e flags automaticamente.

Uso:
  1. Suba os containers: docker compose up --build -d
  2. Acesse http://localhost e complete o wizard de setup do CTFd
  3. Vá em Settings > Access Tokens e gere um token de admin
  4. Execute: python3 setup_ctfd.py --token SEU_TOKEN
"""

import argparse
import sys
import requests

CTFD_URL = "http://localhost"

CHALLENGES = [
    {
        "name": "#01 - Reconhecimento",
        "category": "Recon",
        "description": (
            "Um serviço está rodando neste servidor, mas não na porta padrão.\n\n"
            "Alvo: localhost\n\n"
            "Escaneie o host em busca de portas abertas no range 9000–9200."
        ),
        "value": 100,
        "flag": "FLAG{sem_scanner_sem_ganho}",
        "hint": "nmap -p 9000-9200 <host> ou use um script Python com socket.",
        "hint_cost": 20,
    },
    {
        "name": "#02 - Enumeração",
        "category": "Web",
        "description": (
            "Esta aplicação tem rotas não linkadas. Use uma ferramenta de enumeração de diretórios.\n\n"
            "Acesse o desafio em: http://localhost/chall-02/\n\n"
            "Wordlist recomendada: SecLists/Discovery/Web-Content/common.txt"
        ),
        "value": 100,
        "flag": "FLAG{mestre_da_enumeracao}",
        "hint": "gobuster dir -u http://localhost/chall-02/ -w common.txt",
        "hint_cost": 20,
    },
    {
        "name": "#03 - Credenciais Padrão",
        "category": "Web",
        "description": (
            "Sistema implantado às pressas. O desenvolvedor pode não ter alterado as configurações padrão.\n\n"
            "Acesse o desafio em: http://localhost/chall-03/"
        ),
        "value": 100,
        "flag": "FLAG{credenciais_padrao_sao_perigosas}",
        "hint": "Tente as combinações mais comuns: admin/admin, admin/password, root/root.",
        "hint_cost": 20,
    },
    {
        "name": "#04 - Validação no Front é só UX",
        "category": "Web",
        "description": (
            "Esta loja valida o saldo do cliente em JavaScript antes de enviar o formulário.\n"
            "Mas o servidor confia cegamente no preço recebido.\n\n"
            "Acesse o desafio em: http://localhost/chall-04/\n\n"
            "Endpoint de compra: POST /comprar com campo preco"
        ),
        "value": 150,
        "flag": "FLAG{validacao_no_front_e_so_ux}",
        "hint": "DevTools → Elements → edite o <input type='hidden' name='preco'> para um valor menor que R$ 1,00.",
        "hint_cost": 30,
    },
    {
        "name": "#05 - Chave Exposta no Frontend",
        "category": "Web",
        "description": (
            "Este dashboard carrega dados de uma API interna.\n"
            "Inspecione o código e o tráfego de rede — a autenticação da API pode estar visível.\n\n"
            "Acesse o desafio em: http://localhost/chall-05/\n\n"
            "Endpoint da flag: /api/flag"
        ),
        "value": 200,
        "flag": "FLAG{chave_api_no_codigo_frontend}",
        "hint": "DevTools → Sources. Procure por arquivos .js carregados pela página.",
        "hint_cost": 40,
    },
    {
        "name": "#06 - Header Manipulation",
        "category": "Web",
        "description": (
            "O painel administrativo está restrito à rede interna.\n"
            "O servidor usa um cabeçalho HTTP para determinar a origem da requisição.\n\n"
            "Acesse o desafio em: http://localhost/chall-06/\n\n"
            "Rota protegida: /admin"
        ),
        "value": 200,
        "flag": "FLAG{manipulacao_de_cabecalhos}",
        "hint": "Qual cabeçalho HTTP indica o IP real do cliente em ambientes com proxy?",
        "hint_cost": 40,
    },
    {
        "name": "#07 - Fuzzing de Parâmetros",
        "category": "Web",
        "description": (
            "O endpoint /search aceita parâmetros não documentados que ativam funcionalidades ocultas.\n\n"
            "Acesse o desafio em: http://localhost/chall-07/\n\n"
            "Wordlist recomendada: SecLists/Discovery/Web-Content/burp-parameter-names.txt"
        ),
        "value": 200,
        "flag": "FLAG{fuzzing_de_parametros}",
        "hint": "ffuf -u http://localhost/chall-07/search?FUZZ=true -w burp-parameter-names.txt",
        "hint_cost": 40,
    },
    {
        "name": "#08 - LFI / Path Traversal",
        "category": "Web",
        "description": (
            "O endpoint /terms?doc= lê arquivos do servidor sem validar o caminho informado.\n\n"
            "Acesse o desafio em: http://localhost/chall-08/\n\n"
            "A flag está em /var/secrets/flag.txt."
        ),
        "value": 300,
        "flag": "FLAG{travessia_de_diretorio}",
        "hint": "Tente /terms?doc=../../../../var/secrets/flag.txt",
        "hint_cost": 60,
    },
    {
        "name": "#09 - SQL Injection",
        "category": "Web",
        "description": (
            "O campo de busca de produtos concatena o input diretamente na query SQL.\n"
            "A flag está em uma tabela diferente da de produtos.\n\n"
            "Acesse o desafio em: http://localhost/chall-09/\n\n"
            "Endpoint: /search?q="
        ),
        "value": 300,
        "flag": "FLAG{injecao_sql_dominada}",
        "hint": "sqlmap -u 'http://localhost/chall-09/search?q=test' --tables --dump",
        "hint_cost": 60,
    },
    {
        "name": "#10 - Upload Bypass",
        "category": "Web",
        "description": (
            "O servidor aceita apenas .jpg, mas a validação verifica somente a última extensão.\n"
            "Faça upload de um arquivo com código executável e acesse-o em /uploads/.\n\n"
            "Acesse o desafio em: http://localhost/chall-10/\n\n"
            "Endpoint de upload: /upload"
        ),
        "value": 500,
        "flag": "FLAG{bypass_de_upload}",
        "hint": "Envie um arquivo nomeado shell.php.jpg contendo código PHP. Depois acesse /uploads/shell.php.jpg.",
        "hint_cost": 100,
    },
    {
        "name": "#11 - Cadeia Completa",
        "category": "Web",
        "description": (
            "Desafio encadeado com múltiplos passos:\n\n"
            "1. Enumere as rotas da aplicação\n"
            "2. Autentique-se em /legacy — qualquer credencial funciona\n"
            "3. Analise o JWT recebido e forge um token com role admin\n"
            "4. Acesse /management com o token forjado\n"
            "5. Explore o endpoint de diagnóstico de rede em /management/network\n\n"
            "Acesse o desafio em: http://localhost/chall-11/"
        ),
        "value": 500,
        "flag": "FLAG{vulnerabilidades_encadeadas}",
        "hint": "O JWT usa HS256 com uma chave fraca. Use jwt_tool ou PyJWT para forjar. O endpoint de rede executa comandos do sistema.",
        "hint_cost": 100,
    },
]


def api(session, method, path, **kwargs):
    url = f"{CTFD_URL}/api/v1{path}"
    resp = getattr(session, method)(url, **kwargs)
    data = resp.json()
    if not data.get("success"):
        print(f"  ERRO em {method.upper()} {path}: {data}")
        return None
    return data.get("data")


def main():
    parser = argparse.ArgumentParser(description="Setup automático do CTFd")
    parser.add_argument("--token", required=True, help="Token de admin do CTFd")
    parser.add_argument("--url", default=CTFD_URL, help=f"URL do CTFd (padrão: {CTFD_URL})")
    args = parser.parse_args()

    global CTFD_URL
    CTFD_URL = args.url.rstrip("/")

    session = requests.Session()
    session.headers["Authorization"] = f"Token {args.token}"
    session.headers["Content-Type"] = "application/json"

    print("Verificando conexão com o CTFd...")
    try:
        resp = session.get(f"{CTFD_URL}/api/v1/challenges")
        resp.raise_for_status()
    except Exception as e:
        print(f"Não foi possível conectar ao CTFd: {e}")
        sys.exit(1)

    print(f"Conectado! Criando {len(CHALLENGES)} desafios...\n")

    for chall in CHALLENGES:
        print(f"Criando: {chall['name']}")

        chall_data = api(session, "post", "/challenges", json={
            "name": chall["name"],
            "category": chall["category"],
            "description": chall["description"],
            "value": chall["value"],
            "type": "standard",
            "state": "visible",
        })

        if chall_data is None:
            print("  Pulando (erro ao criar desafio)\n")
            continue

        chall_id = chall_data["id"]

        api(session, "post", "/flags", json={
            "challenge_id": chall_id,
            "content": chall["flag"],
            "type": "static",
            "data": "",
        })
        print(f"  Flag adicionada: {chall['flag']}")

        api(session, "post", "/hints", json={
            "challenge_id": chall_id,
            "content": chall["hint"],
            "cost": chall["hint_cost"],
            "type": "standard",
        })
        print(f"  Dica adicionada (custo: {chall['hint_cost']} pts)")
        print()

    print("=" * 50)
    print("Setup concluído!")
    print(f"Acesse {CTFD_URL} para ver os desafios no CTFd.")


if __name__ == "__main__":
    main()
