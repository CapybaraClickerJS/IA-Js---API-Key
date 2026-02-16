#!/usr/bin/env python3
import os
import secrets
from flask import Flask, request, session, jsonify, abort

app = Flask(__name__)
app.secret_key = "iajs_secret_key_super_segura"  # troque por algo forte se quiser

# Pastas/arquivos
os.makedirs("usuarios", exist_ok=True)
os.makedirs("apis_criadas", exist_ok=True)

USERS_FILE = "usuarios/users.txt"
API_FILE = "apis_criadas/api_keys.txt"

# garante arquivos vazios
if not os.path.exists(USERS_FILE):
    open(USERS_FILE, "w").close()

if not os.path.exists(API_FILE):
    open(API_FILE, "w").close()


# -----------------------
# Funções utilitárias
# -----------------------
def usuario_existe(username: str, senha: str) -> bool:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                user, pwd = linha.split("|", 1)
            except ValueError:
                continue
            if user == username and pwd == senha:
                return True
    return False


def usuario_ja_existe(username: str) -> bool:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                user, _ = linha.split("|", 1)
            except ValueError:
                continue
            if user == username:
                return True
    return False


def criar_usuario(username: str, senha: str) -> None:
    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username}|{senha}\n")


def gerar_api_key() -> str:
    return "sk-iajs-" + secrets.token_hex(24)


def api_key_valida(key: str) -> bool:
    # procura a key nas linhas do arquivo (linha pode conter "usuario | key")
    with open(API_FILE, "r", encoding="utf-8") as f:
        for linha in f:
            if key in linha:
                return True
    return False


def gravar_api_do_usuario(username: str, key: str) -> None:
    with open(API_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username} | {key}\n")


# -----------------------
# Rotas
# -----------------------
@app.route("/")
def home():
    return "IA Js API ONLINE"


@app.route("/criar_conta", methods=["POST"])
def criar_conta():
    # aceita tanto form-data quanto JSON
    data = request.form if request.form else request.get_json(silent=True) or {}
    username = data.get("username")
    senha = data.get("senha")

    if not username or not senha:
        return jsonify({"error": "preencha todos os campos (username e senha)"}), 400

    if usuario_ja_existe(username):
        return jsonify({"error": "usuário já existe"}), 400

    # validação de senha
    numeros = sum(c.isdigit() for c in senha)
    if len(senha) < 8:
        return jsonify({"error": "a senha precisa ter pelo menos 8 caracteres"}), 400
    if numeros < 3:
        return jsonify({"error": "a senha precisa ter pelo menos 3 números"}), 400

    criar_usuario(username, senha)
    session["usuario"] = username
    return jsonify({"status": "success", "message": "Conta criada com sucesso!"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.form if request.form else request.get_json(silent=True) or {}
    username = data.get("username")
    senha = data.get("senha")

    if not username or not senha:
        return jsonify({"error": "preencha username e senha"}), 400

    if usuario_existe(username, senha):
        session["usuario"] = username
        return jsonify({"status": "success", "message": "Login realizado com sucesso!"})
    else:
        return jsonify({"error": "usuário ou senha incorretos"}), 401


@app.route("/criar_api", methods=["POST"])
def criar_api():
    # cria API para o usuário logado
    if "usuario" not in session:
        return jsonify({"error": "faça login primeiro"}), 401

    username = session["usuario"]
    key = gerar_api_key()
    gravar_api_do_usuario(username, key)
    return jsonify({"status": "success", "api_key": key}), 201


# rota apenas para testes locais: gera chave sem login (ACESSO LOCAL APENAS)
@app.route("/gerar_api_teste", methods=["GET"])
def gerar_api_teste():
    # permite somente chamadas do localhost para segurança
    ip = request.remote_addr
    if ip not in ("127.0.0.1", "localhost", "::1"):
        return jsonify({"error": "rota de teste acessível somente localmente"}), 403
    key = gerar_api_key()
    gravar_api_do_usuario("LOCAL_TEST", key)
    return jsonify({"api_key": key})


# -----------------------
# API real (autenticada por Bearer token)
# -----------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "API key ausente"}), 401

    api_key = auth_header.split(" ", 1)[1].strip()
    if not api_key_valida(api_key):
        return jsonify({"error": "API key inválida"}), 403

    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Envie JSON com 'message'"}), 400

    mensagem = data["message"]
    # Simulação (substitua por integração com OpenAI/Outro se quiser)
    resposta = f"Você disse: {mensagem}. IA Js ainda está em desenvolvimento."

    return jsonify({"reply": resposta})


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("usuario", None)
    return jsonify({"status": "success", "message": "Logout realizado com sucesso!"})


# -----------------------
# Start
# -----------------------
if __name__ == "__main__":
    # debug=False por segurança; se quiser ver reload set debug=True
    app.run(host="0.0.0.0", port=5000, debug=False)