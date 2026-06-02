# CTF Arlley - Laboratorio Web com CTFd

Projeto de laboratorio de seguranca web para treino em ambiente local, com:

- 10 desafios web em Flask (um container por desafio)
- CTFd para placar, submissao de flags e gerenciamento
- Nginx como reverse proxy unico em `http://localhost`
- Inicializacao automatica do CTFd e carga dos desafios

## Visao geral da arquitetura

- `nginx` exposto na porta `80`
- `ctfd` interno na porta `8000` (acessado via proxy)
- `chall-01` ate `chall-10` internos na porta `5000`
- `ctfd-init` roda uma vez para configurar o CTFd e criar desafios/flags/dicas

Fluxo de rotas:

- `/chall-01/` ... `/chall-10/` -> containers dos desafios
- `/` (catch-all) -> CTFd

## Pre-requisitos

- Docker
- Docker Compose (plugin `docker compose`)

Para validar:

```bash
docker --version
docker compose version
```

## Configuracao

O projeto usa variaveis em `.env`:

- `CTF_NAME`
- `CTF_DESCRIPTION`
- `USER_MODE`
- `ADMIN_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `SECRET_KEY`
- `CHALLENGE_BASE_URL`

No ambiente local, mantenha `CHALLENGE_BASE_URL=http://localhost`.

## Subida rapida (recomendada)

1. Build e subida dos servicos:

```bash
docker compose up --build -d
```

2. Acompanhe os logs de inicializacao automatica:

```bash
docker compose logs -f ctfd-init
```

3. Abra no navegador:

- `http://localhost` (CTFd)

4. Entre com o admin definido no `.env`.

Se o `ctfd-init` finalizar com sucesso, o setup inicial e os 10 desafios ja estarao criados no CTFd.

## Validacao rapida

Confira containers ativos:

```bash
docker ps
```

Teste uma rota de desafio:

```bash
curl -I http://localhost/chall-06/
```

## Operacao

Parar o ambiente:

```bash
docker compose down
```

Parar e remover volumes do CTFd (reset completo de dados):

```bash
docker compose down -v
```

Rebuild completo:

```bash
docker compose up --build -d
```

## Setup manual alternativo (quando necessario)

Se voce preferir popular desafios via API manualmente:

1. Suba os containers:

```bash
docker compose up --build -d
```

2. Acesse `http://localhost`, conclua o wizard do CTFd e gere um Access Token de admin.

3. Execute o script:

```bash
python3 setup_ctfd.py --token SEU_TOKEN
```

Opcional (URL custom):

```bash
python3 setup_ctfd.py --token SEU_TOKEN --url http://localhost
```

## Estrutura do repositorio

```text
.
├── docker-compose.yml
├── .env
├── ctfd_init.py
├── setup_ctfd.py
├── nginx/
│   └── nginx.conf
├── chall-01/
├── chall-02/
├── chall-03/
├── chall-04/
├── chall-05/
├── chall-06/
├── chall-07/
├── chall-08/
├── chall-09/
└── chall-10/
```

Cada pasta `chall-XX` possui:

- `app.py`
- `Dockerfile`
- `templates/`
- `static/` (quando aplicavel)

## Lista de desafios (temas)

1. Codigo-fonte HTML e comentarios expostos
2. Descoberta de rotas ocultas
3. Enumeracao via `robots.txt`
4. Credenciais padrao
5. Segredos em JavaScript cliente
6. Vazamento via headers HTTP
7. Confianca indevida em cookies
8. Bypass por dupla extensao em upload
9. Exposicao de arquivo `.env`
10. SQL Injection em autenticacao

## Troubleshooting

Se `http://localhost` nao abrir:

- Verifique conflito na porta `80`
- Rode `docker compose ps`
- Veja logs: `docker compose logs -f nginx ctfd`

Se desafios nao aparecerem no CTFd:

- Inspecione logs do init: `docker compose logs ctfd-init`
- Reinicie apenas o init:

```bash
docker compose up --force-recreate --no-deps ctfd-init
```

Se quiser reiniciar do zero:

```bash
docker compose down -v
docker compose up --build -d
```

## Aviso

Este projeto e educacional, para laboratorio local e ambientes autorizados.
Nao use tecnicas de exploracao em sistemas sem permissao explicita.
# ctf-arlley
