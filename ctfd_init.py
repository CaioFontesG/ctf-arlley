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
    "FLAG_PHISHING",         # 16
    "FLAG_LGPD",             # 17
]
FLAGS = {i + 1: os.environ.get(v, f"FLAG_NOT_SET_{v}") for i, v in enumerate(_FLAG_VARS)}

CHALLENGES = [
    {
        "name": "#01 - Comentário HTML",
        "category": "Web",
        "description": (
            f"Às vezes informações sensíveis ficam escondidas no código-fonte da página.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-01/]({BASE_URL}/chall-01/)\n\n"
            f"Dica de ferramenta: Ctrl+U no navegador ou DevTools → Elements."
        ),
        "value": 50,
        "flag": FLAGS[1],
        "hint": "Comentários HTML têm o formato <!-- ... -->. Procure por esse padrão no código-fonte.",
        "hint_cost": 0,
        "mitigation": "Nunca inclua dados sensíveis em comentários HTML — o cliente recebe o código-fonte completo. Use variáveis de servidor e nunca exponha segredos no template.",
    },
    {
        "name": "#02 - Cookie Exposto",
        "category": "Web",
        "description": (
            f"Esta aplicação armazena uma informação importante no navegador.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-02/]({BASE_URL}/chall-02/)\n\n"
            f"Dica de ferramenta: DevTools → Application → Cookies."
        ),
        "value": 50,
        "flag": FLAGS[2],
        "hint": "DevTools (F12) → aba Application → Storage → Cookies → selecione o site.",
        "hint_cost": 10,
        "mitigation": "Nunca armazene dados sensíveis em cookies sem criptografia. Use as flags HttpOnly (impede acesso via JS) e Secure (só HTTPS). Prefira armazenar apenas um identificador de sessão opaco no cookie.",
    },
    {
        "name": "#03 - Console.log",
        "category": "Web",
        "description": (
            f"Desenvolvedores às vezes deixam informações de debug visíveis no console JavaScript.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-03/]({BASE_URL}/chall-03/)\n\n"
            f"Dica de ferramenta: DevTools → Console."
        ),
        "value": 50,
        "flag": FLAGS[3],
        "hint": "DevTools (F12) → aba Console. Recarregue a página se necessário.",
        "hint_cost": 10,
        "mitigation": "Remova todos os console.log com dados sensíveis antes de ir para produção. Use ferramentas de build (webpack, Vite) para eliminar logs automaticamente no bundle de produção.",
    },
    {
        "name": "#04 - Header HTTP",
        "category": "Web",
        "description": (
            f"Uma resposta HTTP tem mais do que só o corpo da página — os headers também carregam informações.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-04/]({BASE_URL}/chall-04/)\n\n"
            f"Dica de ferramenta: DevTools → Network → selecione a requisição → Response Headers."
        ),
        "value": 50,
        "flag": FLAGS[4],
        "hint": "DevTools → Network → clique na requisição da página → aba Headers → Response Headers.",
        "hint_cost": 10,
        "mitigation": "Nunca exponha dados sensíveis em headers de resposta. Remova headers que revelem tecnologia, versão ou informações internas do servidor (X-Powered-By, Server, etc.).",
    },
    {
        "name": "#05 - Credenciais Padrão",
        "category": "Web",
        "description": (
            f"Sistema implantado às pressas. O desenvolvedor pode não ter alterado as configurações padrão.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-05/]({BASE_URL}/chall-05/)"
        ),
        "value": 100,
        "flag": FLAGS[5],
        "hint": "Tente as combinações padrões de fornecedores, equipamentos e serviços.",
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
        "name": "#14 - Upload + LFI",
        "category": "Web",
        "description": (
            f"Um portal permite enviar fotos de perfil. Após o upload, a aplicação fornece um link para acessar o arquivo.\n"
            f"Será que a rota de download está protegida contra path traversal?\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-14/]({BASE_URL}/chall-14/)\n\n"
            f"Endpoint de upload: `/upload`"
        ),
        "value": 500,
        "flag": FLAGS[14],
        "hint": "Observe o parâmetro da rota de download. Tente acessar arquivos fora do diretório de upload usando `../`.",
        "hint_cost": 100,
        "mitigation": "Nunca use input do usuário para construir caminhos de arquivo sem sanitização. Use `os.path.basename()` ou `werkzeug.utils.secure_filename` para limpar nomes de arquivo. Valide que o caminho resolvido está dentro do diretório permitido com `os.path.realpath()`.",
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
    {
        "name": "#16 - Phishing",
        "category": "Social Engineering",
        "description": (
            f"Você recebeu um link suspeito dizendo que sua sessão no CTF expirou.\n"
            f"Acesse e veja o que acontece quando você tenta fazer login.\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-16/]({BASE_URL}/chall-16/)"
        ),
        "value": 100,
        "flag": FLAGS[16],
        "hint": "Antes de inserir credenciais em qualquer site, verifique a URL na barra do navegador.",
        "hint_cost": 20,
        "mitigation": "Sempre verifique a URL antes de inserir credenciais. Phishing imita interfaces legítimas para roubar senhas. Use um gerenciador de senhas — ele só preenche automaticamente no domínio correto, nunca em páginas falsas.",
    },
    {
        "name": "#17 - IDOR / LGPD",
        "category": "Web",
        "description": (
            f"Este portal de clientes exibe dados pessoais pelo parâmetro `id` na URL.\n"
            f"Você está logado como usuário #1 — mas será que só consegue ver seus próprios dados?\n\n"
            f"Acesse o desafio: [{BASE_URL}/chall-17/]({BASE_URL}/chall-17/)\n\n"
            f"Endpoint: `/perfil?id=1`"
        ),
        "value": 150,
        "flag": FLAGS[17],
        "hint": "Tente alterar o parâmetro `id` na URL para outros valores inteiros.",
        "hint_cost": 30,
        "mitigation": "Nunca use IDs sequenciais como controle de acesso. Valide no servidor se o usuário autenticado tem permissão para acessar o recurso solicitado. Essa vulnerabilidade (IDOR) é uma das mais comuns em vazamentos de dados e viola diretamente a LGPD ao expor dados pessoais de terceiros.",
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


def challenges_with_flags(session, nonce):
    """Returns {challenge_id: (flag_id, flag_content)} for challenges that have at least one flag."""
    r = session.get(f"{CTFD_URL}/api/v1/flags",
                    headers={"CSRF-Token": nonce}, timeout=10)
    data = r.json()
    if data.get("success"):
        result = {}
        for f in data.get("data", []):
            cid = f["challenge_id"]
            if cid not in result:
                result[cid] = (f["id"], f["content"])
        return result
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
    flagged  = challenges_with_flags(session, nonce)

    log(f"\nPopulando desafios ({len(existing)} já existentes)...\n")

    for chall in CHALLENGES:
        if chall["name"] in existing:
            chall_id = existing[chall["name"]]

            # Limpa prerequisites de execuções anteriores
            api(session, nonce, "patch", f"/challenges/{chall_id}", {
                "requirements": {"prerequisites": [], "anonymize": False},
            })

            if chall_id not in flagged:
                log(f"  [fix] {chall['name']} — flag faltante, criando...")
                api(session, nonce, "post", "/flags", {
                    "challenge_id": chall_id,
                    "content":      chall["flag"],
                    "type":         "static",
                    "data":         "",
                })
            else:
                flag_id, flag_content = flagged[chall_id]
                if flag_content != chall["flag"]:
                    log(f"  [update] {chall['name']} — rotacionando flag...")
                    api(session, nonce, "delete", f"/flags/{flag_id}", {})
                    api(session, nonce, "post", "/flags", {
                        "challenge_id": chall_id,
                        "content":      chall["flag"],
                        "type":         "static",
                        "data":         "",
                    })
                else:
                    log(f"  [skip] {chall['name']}")
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
            continue

        chall_id = data["id"]

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

    log("\nSetup completo! Acesse http://localhost/ para começar.")


if __name__ == "__main__":
    main()
