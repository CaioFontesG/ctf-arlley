#!/usr/bin/env python3
"""
Inicializa o CTFd automaticamente.
Lê configuração de variáveis de ambiente (definidas no .env).
Executado pelo serviço ctfd-init no docker-compose.
"""

import os
import re
import sys
import time
import requests

CTFD_URL      = os.environ.get("CTFD_URL",            "http://ctfd:8000")
CTF_NAME      = os.environ.get("CTF_NAME",             "CTF")
CTF_DESC      = os.environ.get("CTF_DESCRIPTION",      "")
USER_MODE     = os.environ.get("USER_MODE",             "users")
ADMIN_NAME    = os.environ.get("ADMIN_NAME",            "admin")
ADMIN_EMAIL   = os.environ.get("ADMIN_EMAIL",           "admin@ctf.local")
ADMIN_PASS    = os.environ.get("ADMIN_PASSWORD",        "admin123")
BASE_URL      = os.environ.get("CHALLENGE_BASE_URL",    "http://localhost")

_FLAG_VARS = [
    "FLAG_HTML_COMMENT",     # 1
    "FLAG_COOKIE",           # 2
    "FLAG_CONSOLE",          # 3
    "FLAG_NETWORK",          # 4
    "FLAG_CREDENCIAIS",      # 5
    "FLAG_RECONHECIMENTO",   # 6
    "FLAG_ENUMERACAO",       # 7
    "FLAG_VALIDACAO_FRONT",  # 8
    "FLAG_DEVTOOLS",         # 9
    "FLAG_HEADER",           # 10
    "FLAG_FUZZING",          # 11
    "FLAG_LFI",              # 12
    "FLAG_SQL_INJECTION",    # 13
    "FLAG_UPLOAD",           # 14
    "FLAG_CADEIA",           # 15
]
FLAGS = {i + 1: os.environ.get(v, f"FLAG_NOT_SET_{v}") for i, v in enumerate(_FLAG_VARS)}

CHALLENGES = [
    {
        "name": "#01 - Comentário HTML",
        "category": "Web",
        "description": (
            f"Às vezes informações sensíveis ficam escondidas no código-fonte da página.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-02/]({BASE_URL}/chall-02/)\n\n"
            f"Dica de ferramenta: Ctrl+U no navegador ou DevTools → Elements."
        ),
        "value": 50,
        "flag": FLAGS[1],
        "hint": "Ctrl+U abre o código-fonte da página. Procure por comentários HTML.",
        "hint_cost": 0,
        "mitigation": "Nunca inclua dados sensíveis em comentários HTML — o cliente recebe o código-fonte completo. Use variáveis de servidor e nunca exponha segredos no template.",
    },
    {
        "name": "#02 - Cookie Exposto",
        "category": "Web",
        "description": (
            f"Esta aplicação armazena uma informação importante no navegador.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-03/]({BASE_URL}/chall-03/)\n\n"
            f"Dica de ferramenta: DevTools → Application → Cookies."
        ),
        "value": 50,
        "flag": FLAGS[2],
        "hint": "DevTools (F12) → aba Application → Storage → Cookies → selecione o site.",
        "hint_cost": 0,
        "mitigation": "Nunca armazene dados sensíveis em cookies sem criptografia. Use as flags HttpOnly (impede acesso via JS) e Secure (só HTTPS). Prefira armazenar apenas um identificador de sessão opaco no cookie.",
    },
    {
        "name": "#03 - Console.log",
        "category": "Web",
        "description": (
            f"Desenvolvedores às vezes deixam informações de debug visíveis no console JavaScript.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-04/]({BASE_URL}/chall-04/)\n\n"
            f"Dica de ferramenta: DevTools → Console."
        ),
        "value": 50,
        "flag": FLAGS[3],
        "hint": "DevTools (F12) → aba Console. Recarregue a página se necessário.",
        "hint_cost": 0,
        "mitigation": "Remova todos os console.log com dados sensíveis antes de ir para produção. Use ferramentas de build (webpack, Vite) para eliminar logs automaticamente no bundle de produção.",
    },
    {
        "name": "#04 - Header HTTP",
        "category": "Web",
        "description": (
            f"Uma resposta HTTP tem mais do que só o corpo da página — os headers também carregam informações.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-05/]({BASE_URL}/chall-05/)\n\n"
            f"Dica de ferramenta: DevTools → Network → selecione a requisição → Response Headers."
        ),
        "value": 50,
        "flag": FLAGS[4],
        "hint": "DevTools → Network → clique na requisição da página → aba Headers → Response Headers.",
        "hint_cost": 0,
        "mitigation": "Nunca exponha dados sensíveis em headers de resposta. Remova headers que revelem tecnologia, versão ou informações internas do servidor (X-Powered-By, Server, etc.).",
    },
    {
        "name": "#05 - Credenciais Padrão",
        "category": "Web",
        "description": (
            f"Sistema implantado às pressas. O desenvolvedor pode não ter alterado as configurações padrão.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-01/]({BASE_URL}/chall-01/)"
        ),
        "value": 100,
        "flag": FLAGS[5],
        "hint": "Tente as combinações mais comuns: admin/admin, admin/password, root/root.",
        "hint_cost": 20,
        "mitigation": "Sempre altere credenciais padrão antes de implantar em produção. Use senhas fortes e únicas. Considere implementar bloqueio após tentativas falhas (rate limiting) e autenticação multifator.",
    },
    {
        "name": "#06 - Reconhecimento",
        "category": "Recon",
        "description": (
            f"Um serviço está rodando neste servidor, mas não na porta padrão.\n\n"
            f"Alvo: `{BASE_URL.split('://')[1] if '://' in BASE_URL else BASE_URL}`\n\n"
            f"Escaneie o host em busca de portas abertas no range 9000–9200."
        ),
        "value": 100,
        "flag": FLAGS[6],
        "hint": "nmap -p 9000-9200 <host> ou use um script Python com socket.",
        "hint_cost": 20,
        "mitigation": "Use firewall para bloquear portas não necessárias ao público. Exponha apenas as portas estritamente necessárias (princípio do menor privilégio). Monitore portas abertas regularmente com ferramentas de inventário.",
    },
    {
        "name": "#07 - Enumeração",
        "category": "Web",
        "description": (
            f"Esta aplicação tem rotas não linkadas. Use uma ferramenta de enumeração de diretórios.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-07/]({BASE_URL}/chall-07/)\n\n"
            f"Wordlist recomendada: `SecLists/Discovery/Web-Content/common.txt`"
        ),
        "value": 100,
        "flag": FLAGS[7],
        "hint": "gobuster dir -u <url> -w common.txt",
        "hint_cost": 20,
        "mitigation": "Não deixe rotas sensíveis acessíveis por obscuridade. Retorne 404 genérico para rotas inexistentes sem revelar estrutura interna. Implemente autenticação nas rotas que contêm dados sensíveis.",
    },
    {
        "name": "#08 - Validação no Front é só UX",
        "category": "Web",
        "description": (
            f"Esta loja valida o saldo do cliente em JavaScript antes de enviar o formulário.\n"
            f"Mas o servidor confia cegamente no preço recebido.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-08/]({BASE_URL}/chall-08/)\n\n"
            f"Endpoint de compra: `POST /comprar` com campo `preco`"
        ),
        "value": 150,
        "flag": FLAGS[8],
        "hint": "DevTools → Elements → edite o <input type='hidden' name='preco'> para um valor menor que R$ 1,00.",
        "hint_cost": 30,
        "mitigation": "Nunca confie em dados vindos do cliente (preço, quantidade, role, etc.). Sempre valide e recalcule valores sensíveis no servidor. Validação no frontend é apenas UX — a segurança real fica no backend.",
    },
    {
        "name": "#09 - Chave Exposta no Frontend",
        "category": "Web",
        "description": (
            f"Este dashboard carrega dados de uma API interna.\n"
            f"Inspecione o código e o tráfego de rede — a autenticação da API pode estar visível.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-09/]({BASE_URL}/chall-09/)\n\n"
            f"Endpoint da flag: `/api/flag`"

        ),
        "value": 200,
        "flag": FLAGS[9],
        "hint": "DevTools → Sources. Procure por arquivos .js carregados pela página.",
        "hint_cost": 40,
        "mitigation": "Nunca coloque chaves de API, tokens ou secrets em código JavaScript frontend — qualquer usuário pode lê-los. Use um backend como proxy para chamadas autenticadas a APIs externas.",
    },
    {
        "name": "#10 - Header Manipulation",
        "category": "Web",
        "description": (
            f"O painel administrativo está restrito à rede interna.\n"
            f"O servidor usa um cabeçalho HTTP para determinar a origem da requisição.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-10/]({BASE_URL}/chall-10/)\n\n"
            f"Rota protegida: `/admin`"
        ),
        "value": 200,
        "flag": FLAGS[10],
        "hint": "Qual cabeçalho HTTP indica o IP real do cliente em ambientes com proxy?",
        "hint_cost": 40,
        "mitigation": "Nunca use X-Forwarded-For ou X-Real-IP para decisões de segurança — qualquer cliente pode forjar esses headers. Use autenticação real (sessão, JWT) para controle de acesso a recursos restritos.",
    },
    {
        "name": "#11 - Fuzzing de Parâmetros",
        "category": "Web",
        "description": (
            f"O endpoint `/search` aceita parâmetros não documentados que ativam funcionalidades ocultas.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-11/]({BASE_URL}/chall-11/)\n\n"
            f"Wordlist recomendada: `SecLists/Discovery/Web-Content/burp-parameter-names.txt`"
        ),
        "value": 200,
        "flag": FLAGS[11],
        "hint": "ffuf -u <url>/search?FUZZ=true -w burp-parameter-names.txt — depois combine os parâmetros encontrados.",
        "hint_cost": 40,
        "mitigation": "Remova endpoints e parâmetros de debug antes de ir para produção. Não ative funcionalidades ocultas via parâmetros não documentados — qualquer parâmetro aceito pelo servidor é superfície de ataque.",
    },
    {
        "name": "#12 - LFI / Path Traversal",
        "category": "Web",
        "description": (
            f"Esta aplicação possui um endpoint que lê arquivos do disco a partir de um parâmetro de query.\n"
            f"O servidor não valida o caminho informado.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-12/]({BASE_URL}/chall-12/)\n\n"
            f"A flag está em `/var/secrets/flag.txt`."
        ),
        "value": 300,
        "flag": FLAGS[12],
        "hint": "ffuf -u <url>/FUZZ -w common.txt para encontrar o endpoint. Depois use `?doc=` com `../` para sair do diretório.",
        "hint_cost": 60,
        "mitigation": "Sanitize o caminho recebido: use os.path.realpath() e verifique que o resultado começa com o diretório base permitido. Prefira mapear IDs internos para arquivos em vez de aceitar caminhos diretamente do usuário.",
    },
    {
        "name": "#13 - SQL Injection",
        "category": "Web",
        "description": (
            f"O campo de busca de produtos concatena o input diretamente na query SQL.\n"
            f"A flag está em uma tabela diferente da de produtos.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-13/]({BASE_URL}/chall-13/)\n\n"
            f"Endpoint: `/search?q=`"
        ),
        "value": 300,
        "flag": FLAGS[13],
        "hint": "sqlmap -u '<url>/search?q=test' --tables --dump",
        "hint_cost": 60,
        "mitigation": "Use sempre queries parametrizadas (prepared statements) — nunca concatene input do usuário na query. ORMs como SQLAlchemy fazem isso automaticamente. Aplique o princípio do menor privilégio no usuário do banco de dados.",
    },
    {
        "name": "#14 - Upload Bypass",
        "category": "Web",
        "description": (
            f"O servidor aceita apenas `.jpg`, mas a validação verifica somente a última extensão.\n"
            f"Faça upload de um arquivo com código executável e acesse-o em `/uploads/`.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-14/]({BASE_URL}/chall-14/)\n\n"
            f"Endpoint de upload: `/upload`"
        ),
        "value": 500,
        "flag": FLAGS[14],
        "hint": "Envie um arquivo nomeado shell.php.jpg contendo código PHP. Depois acesse /uploads/shell.php.jpg.",
        "hint_cost": 100,
        "mitigation": "Valide o tipo do arquivo pelo conteúdo (magic bytes), não pela extensão. Renomeie o arquivo no servidor. Armazene uploads fora do webroot e nunca sirva arquivos de upload com permissão de execução.",
    },
    {
        "name": "#15 - Cadeia Completa",
        "category": "Web",
        "description": (
            f"Desafio encadeado com múltiplos passos:\n\n"
            f"1. Enumere as rotas da aplicação\n"
            f"2. Autentique-se em `/legacy` — qualquer credencial funciona\n"
            f"3. Analise o JWT recebido e forge um token com role `admin`\n"
            f"4. Acesse `/management` com o token forjado\n"
            f"5. Explore o endpoint de diagnóstico de rede em `/management/network`\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-15/]({BASE_URL}/chall-15/)"
        ),
        "value": 500,
        "flag": FLAGS[15],
        "hint": "O JWT usa HS256 com uma chave fraca. Use jwt_tool ou PyJWT para forjar. O endpoint de rede executa comandos do sistema.",
        "hint_cost": 100,
        "mitigation": "Use chaves JWT longas e aleatórias (mín. 256 bits). Nunca passe input do usuário para subprocess, os.system ou eval. Use allowlist para comandos de diagnóstico e separe redes de produção de ferramentas de manutenção.",
    },
]


def log(msg):
    print(msg, flush=True)


def extract_nonce(html):
    # Hidden input nos forms de setup/login
    for pattern in [
        r'<input[^>]+name=["\']nonce["\'][^>]+value=["\']([^"\']+)["\']',
        r'<input[^>]+value=["\']([^"\']+)["\'][^>]+name=["\']nonce["\']',
    ]:
        m = re.search(pattern, html)
        if m:
            return m.group(1)
    # JS csrfNonce nas páginas autenticadas
    m = re.search(r'["\']csrfNonce["\']\s*:\s*["\']([a-f0-9]+)["\']', html)
    if m:
        return m.group(1)
    return None


def wait_for_ctfd(session, retries=36, delay=10):
    log("Aguardando CTFd iniciar...")
    for attempt in range(1, retries + 1):
        try:
            r = session.get(f"{CTFD_URL}/", timeout=5)
            if r.status_code < 500:
                log("CTFd disponível!")
                return True
        except Exception:
            pass
        log(f"  tentativa {attempt}/{retries}, aguardando {delay}s...")
        time.sleep(delay)
    return False


def needs_setup(session):
    r = session.get(f"{CTFD_URL}/setup", allow_redirects=False, timeout=10)
    return r.status_code == 200


def do_setup(session):
    log(f'Configurando CTFd: "{CTF_NAME}"...')
    r = session.get(f"{CTFD_URL}/setup", timeout=10)
    nonce = extract_nonce(r.text)
    if not nonce:
        log("ERRO: nonce não encontrado na página de setup.")
        log(r.text[:800])
        sys.exit(1)

    r = session.post(f"{CTFD_URL}/setup", data={
        "nonce":           nonce,
        "ctf_name":        CTF_NAME,
        "ctf_description": CTF_DESC,
        "user_mode":       USER_MODE,
        "name":            ADMIN_NAME,
        "email":           ADMIN_EMAIL,
        "password":        ADMIN_PASS,
        "ctf_theme":       "core",
    }, timeout=30)

    if "setup" in r.url:
        log(f"ERRO: setup falhou (status {r.status_code}, url {r.url}).")
        sys.exit(1)

    log("Setup concluído!")


def do_login(session):
    r = session.get(f"{CTFD_URL}/login", timeout=10)
    nonce = extract_nonce(r.text)
    session.post(f"{CTFD_URL}/login", data={
        "nonce":    nonce,
        "name":     ADMIN_NAME,
        "password": ADMIN_PASS,
    }, timeout=10)


def get_csrf_nonce(session):
    r = session.get(f"{CTFD_URL}/admin/challenges", timeout=10)
    nonce = extract_nonce(r.text)
    if not nonce:
        log("ERRO: CSRF nonce não encontrado na página admin.")
        sys.exit(1)
    return nonce


def api(session, nonce, method, path, payload):
    url = f"{CTFD_URL}/api/v1{path}"
    r = getattr(session, method)(url, json=payload, headers={"CSRF-Token": nonce}, timeout=10)
    result = r.json()
    if not result.get("success"):
        log(f"  aviso API {method.upper()} {path}: {result}")
        return None
    return result.get("data")


def existing_challenges(session, nonce):
    r = session.get(f"{CTFD_URL}/api/v1/challenges?view=admin",
                    headers={"CSRF-Token": nonce}, timeout=10)
    data = r.json()
    if data.get("success"):
        return {c["name"]: c["id"] for c in data.get("data", [])}
    return {}


def main():
    session = requests.Session()

    if not wait_for_ctfd(session):
        log("ERRO: CTFd não iniciou a tempo. Encerrando.")
        sys.exit(1)

    if needs_setup(session):
        do_setup(session)
    else:
        log("CTFd já configurado. Fazendo login...")
        do_login(session)

    nonce    = get_csrf_nonce(session)
    existing = existing_challenges(session, nonce)

    log(f"\nPopulando desafios ({len(existing)} já existentes)...\n")

    # IDs na ordem dos desafios (None se falhou ao criar)
    ordered_ids = []

    for chall in CHALLENGES:
        if chall["name"] in existing:
            log(f"  [skip] {chall['name']}")
            ordered_ids.append(existing[chall["name"]])
            continue

        log(f"  [+] {chall['name']}")

        data = api(session, nonce, "post", "/challenges", {
            "name":        chall["name"],
            "category":    chall["category"],
            "description": chall["description"],
            "value":       chall["value"],
            "type":        "standard",
            "state":       "visible",
        })
        if data is None:
            ordered_ids.append(None)
            continue

        chall_id = data["id"]
        ordered_ids.append(chall_id)

        api(session, nonce, "post", "/flags", {
            "challenge_id": chall_id,
            "content":      chall["flag"],
            "type":         "static",
            "data":         "",
        })

        api(session, nonce, "post", "/hints", {
            "challenge_id": chall_id,
            "content":      chall["hint"],
            "cost":         chall["hint_cost"],
            "type":         "standard",
        })

        api(session, nonce, "post", "/hints", {
            "challenge_id": chall_id,
            "content":      "Como evitar: " + chall["mitigation"],
            "cost":         0,
            "type":         "standard",
        })

    # Encadear pré-requisitos: cada desafio exige o anterior
    log("\nConfigurando pré-requisitos (progressão linear)...")
    for i in range(1, len(ordered_ids)):
        curr_id = ordered_ids[i]
        prev_id = ordered_ids[i - 1]
        if curr_id is None or prev_id is None:
            continue
        api(session, nonce, "patch", f"/challenges/{curr_id}", {
            "requirements": {
                "prerequisites": [prev_id],
                "anonymize":     True,   # mostra o título mas bloqueia o conteúdo
            },
        })
        log(f"  [{i+1}] desbloqueado após [{i}]")

    log("\nSetup completo! Acesse http://localhost/ para começar.")


if __name__ == "__main__":
    main()
