
from flask import Flask, render_template, request, redirect, session, url_for
import json
from datetime import datetime, time

app = Flask(__name__)
app.secret_key = "chave-secreta"
HORARIOS = ["18:00-20:00", "20:00-22:00"]
LIMITE_VAGAS = 12

def carregar_dados():
    try:
        with open("data/alunos.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_dados(dados):
    with open("data/alunos.json", "w") as f:
        json.dump(dados, f, indent=4)

def carregar_checkins():
    try:
        with open("data/checkins.json", "r") as f:
            return json.load(f)
    except:
        return {}

def salvar_checkins(dados):
    with open("data/checkins.json", "w") as f:
        json.dump(dados, f, indent=4)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/admin", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        nome = request.form["nome"]
        pagamento = request.form["pagamento"]
        creditos = int(request.form["creditos"])
        alunos = carregar_dados()
        alunos[nome] = {
            "pagamento": pagamento,
            "creditos": creditos
        }
        salvar_dados(alunos)
    return render_template("admin.html")

@app.route("/usuario", methods=["POST", "GET"])
def usuario():
    if request.method == "POST":
        nome = request.form["nome"]
        alunos = carregar_dados()
        if nome not in alunos:
            return "Usuário não cadastrado"
        session["usuario"] = nome
        return redirect(url_for("painel_usuario"))
    return render_template("usuario.html")

@app.route("/painel_usuario", methods=["GET", "POST"])
def painel_usuario():
    nome = session.get("usuario")
    if not nome:
        return redirect(url_for("usuario"))
    
    alunos = carregar_dados()
    checkins = carregar_checkins()
    hoje = datetime.today().strftime("%Y-%m-%d")
    horarios = checkins.get(hoje, {})
    status = {}

    for h in HORARIOS:
        vagas = horarios.get(h, [])
        status[h] = {
            "vagas_restantes": LIMITE_VAGAS - len(vagas),
            "reservado": nome in vagas
        }

    return render_template("painel_usuario.html", nome=nome, status=status, creditos=alunos[nome]["creditos"])

@app.route("/checkin/<horario>")
def checkin(horario):
    nome = session.get("usuario")
    hoje = datetime.today().strftime("%Y-%m-%d")
    alunos = carregar_dados()
    checkins = carregar_checkins()

    if alunos[nome]["creditos"] <= 0:
        return "Sem créditos disponíveis."

    checkins.setdefault(hoje, {})
    checkins[hoje].setdefault(horario, [])

    if nome not in checkins[hoje][horario] and len(checkins[hoje][horario]) < LIMITE_VAGAS:
        checkins[hoje][horario].append(nome)
        alunos[nome]["creditos"] -= 1
        salvar_dados(alunos)
        salvar_checkins(checkins)

    return redirect(url_for("painel_usuario"))

@app.route("/cancelar/<horario>")
def cancelar(horario):
    agora = datetime.now().time()
    if agora > time(15, 0):
        return "Cancelamento não permitido após 15h."

    nome = session.get("usuario")
    hoje = datetime.today().strftime("%Y-%m-%d")
    alunos = carregar_dados()
    checkins = carregar_checkins()

    if nome in checkins.get(hoje, {}).get(horario, []):
        checkins[hoje][horario].remove(nome)
        alunos[nome]["creditos"] += 1
        salvar_dados(alunos)
        salvar_checkins(checkins)

    return redirect(url_for("painel_usuario"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
