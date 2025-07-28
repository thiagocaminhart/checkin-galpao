import os
import json
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, timedelta, date, timezone
from collections import defaultdict
from models import db, Aluno, Checkin, Admin
from sqlalchemy import func, and_

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chave-secreta-padrao")

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco
db.init_app(app)

HORARIOS = ["18:00-20:00", "20:00-22:00"]
LIMITE_VAGAS = 12
SENHA_ADMIN = "bolinha"

def init_db():
    """Inicializa o banco de dados com tabelas e dados padrão"""
    with app.app_context():
        db.create_all()
        
        # Verificar se já existe configuração admin
        admin_senha = Admin.query.filter_by(chave='senha_admin').first()
        if not admin_senha:
            admin_config = Admin(chave='senha_admin', valor=SENHA_ADMIN)
            db.session.add(admin_config)
            db.session.commit()

def migrar_dados_json():
    """Migra dados existentes do JSON para o banco de dados"""
    try:
        # Migrar alunos
        with open("data/alunos.json", "r", encoding="utf-8") as f:
            alunos_json = json.load(f)
            
        for nome, dados in alunos_json.items():
            aluno_existente = Aluno.query.filter_by(nome=nome).first()
            if not aluno_existente:
                aluno = Aluno(
                    nome=nome,
                    senha=dados.get('senha', nome.lower().replace(" ", "")[:8]),
                    pagamento=dados.get('pagamento', ''),
                    creditos=dados.get('creditos', 0)
                )
                db.session.add(aluno)
        
        # Migrar check-ins
        try:
            with open("data/checkins.json", "r", encoding="utf-8") as f:
                checkins_json = json.load(f)
                
            for data_str, horarios in checkins_json.items():
                data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
                
                for horario, nomes in horarios.items():
                    for nome in nomes:
                        aluno = Aluno.query.filter_by(nome=nome).first()
                        if aluno:
                            # Verificar se já existe o check-in
                            checkin_existente = Checkin.query.filter_by(
                                aluno_id=aluno.id,
                                data=data_obj,
                                horario=horario
                            ).first()
                            
                            if not checkin_existente:
                                checkin = Checkin(
                                    aluno_id=aluno.id,
                                    data=data_obj,
                                    horario=horario
                                )
                                db.session.add(checkin)
        except FileNotFoundError:
            pass  # Arquivo de check-ins não existe ainda
            
        db.session.commit()
        
    except FileNotFoundError:
        pass  # Arquivos JSON não existem ainda

@app.route("/")
def home():
    """Página inicial com login dual"""
    return render_template("login.html")

@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    """Login do administrador"""
    if request.method == "POST":
        senha = request.form.get("senha", "").strip()
        
        # Buscar senha admin no banco
        admin_config = Admin.query.filter_by(chave='senha_admin').first()
        senha_correta = admin_config.valor if admin_config else SENHA_ADMIN
        
        if senha == senha_correta:
            session["admin"] = True
            flash("Login administrativo realizado com sucesso!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Senha administrativa incorreta", "error")
    
    return render_template("admin_login.html")

@app.route("/admin", methods=["POST", "GET"])
def admin():
    """Painel administrativo para gerenciar alunos"""
    if not session.get("admin"):
        flash("Acesso negado. Faça login como administrador.", "error")
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        pagamento = request.form.get("pagamento", "").strip()
        creditos = request.form.get("creditos", "0")
        
        # Validação dos dados
        if not nome:
            flash("Nome é obrigatório", "error")
            return render_template("admin.html")
        
        if not pagamento:
            flash("Informação de pagamento é obrigatória", "error")
            return render_template("admin.html")
        
        try:
            creditos = int(creditos)
            if creditos < 0:
                flash("Créditos deve ser um número positivo", "error")
                return render_template("admin.html")
        except ValueError:
            flash("Créditos deve ser um número válido", "error")
            return render_template("admin.html")
        
        # Gerar senha padrão se não existir
        senha_usuario = request.form.get("senha", "").strip()
        if not senha_usuario:
            senha_usuario = nome.lower().replace(" ", "")[:8]  # Primeiros 8 chars do nome em minúscula
        
        # Verificar se aluno já existe
        aluno_existente = Aluno.query.filter_by(nome=nome).first()
        if aluno_existente:
            flash("Aluno já cadastrado. Atualizando informações.", "info")
            aluno_existente.pagamento = pagamento
            aluno_existente.creditos = creditos
            aluno_existente.senha = senha_usuario
        else:
            # Criar novo aluno
            novo_aluno = Aluno(
                nome=nome,
                senha=senha_usuario,
                pagamento=pagamento,
                creditos=creditos
            )
            db.session.add(novo_aluno)
        
        db.session.commit()
        flash(f"Aluno {nome} cadastrado com sucesso!", "success")
    
    # Carregar lista de alunos para exibição
    alunos = Aluno.query.order_by(Aluno.nome).all()
    
    # Gerar resumo de check-ins
    resumo_checkins = gerar_resumo_checkins()
    
    return render_template("admin.html", alunos=alunos, resumo=resumo_checkins)

@app.route("/usuario", methods=["POST", "GET"])
def usuario():
    """Login de usuário"""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "").strip()
        
        if not nome or not senha:
            flash("Nome e senha são obrigatórios", "error")
            return render_template("usuario.html")
        
        # Buscar aluno no banco de dados
        aluno = Aluno.query.filter_by(nome=nome).first()
        if not aluno:
            flash("Usuário não cadastrado. Entre em contato com a administração.", "error")
            return render_template("usuario.html")
        
        # Verificar senha
        if aluno.senha != senha:
            flash("Senha incorreta", "error")
            return render_template("usuario.html")
        
        session["usuario"] = nome
        flash(f"Bem-vindo(a), {nome}!", "success")
        return redirect(url_for("painel_usuario"))
    
    return render_template("usuario.html")

@app.route("/painel_usuario", methods=["GET", "POST"])
def painel_usuario():
    """Painel do usuário com status dos horários"""
    nome = session.get("usuario")
    if not nome:
        flash("Faça login para acessar o painel", "error")
        return redirect(url_for("usuario"))
    
    # Buscar aluno no banco
    aluno = Aluno.query.filter_by(nome=nome).first()
    if not aluno:
        flash("Usuário não encontrado", "error")
        session.pop("usuario", None)
        return redirect(url_for("usuario"))
    
    hoje = date.today()
    status = {}

    for h in HORARIOS:
        # Contar check-ins para hoje neste horário
        checkins_horario = Checkin.query.filter_by(
            data=hoje,
            horario=h
        ).all()
        
        # Verificar se usuário já tem reserva
        usuario_reservado = any(c.aluno.nome == nome for c in checkins_horario)
        
        status[h] = {
            "vagas_restantes": LIMITE_VAGAS - len(checkins_horario),
            "reservado": usuario_reservado,
            "lotado": len(checkins_horario) >= LIMITE_VAGAS
        }

    # Verificar se é antes das 15h no horário do Brasil (GMT-3) para permitir cancelamentos
    # 15:00 Brasil = 18:00 UTC
    agora_utc = datetime.now(timezone.utc).time()
    pode_cancelar = agora_utc <= time(18, 0)  # 18:00 UTC = 15:00 Brasil
    
    return render_template(
        "painel_usuario.html", 
        nome=nome, 
        status=status, 
        creditos=aluno.creditos,
        hoje=hoje.strftime("%Y-%m-%d"),
        pode_cancelar=pode_cancelar
    )

@app.route("/checkin/<horario>")
def checkin(horario):
    """Realiza check-in do usuário"""
    nome = session.get("usuario")
    if not nome:
        flash("Faça login para fazer check-in", "error")
        return redirect(url_for("usuario"))
    
    if horario not in HORARIOS:
        flash("Horário inválido", "error")
        return redirect(url_for("painel_usuario"))
    
    hoje = date.today()
    
    # Buscar aluno no banco
    aluno = Aluno.query.filter_by(nome=nome).first()
    if not aluno:
        flash("Usuário não encontrado", "error")
        return redirect(url_for("usuario"))

    if aluno.creditos <= 0:
        flash("Sem créditos disponíveis. Entre em contato com a administração.", "error")
        return redirect(url_for("painel_usuario"))

    # Verificar se já tem reserva para este horário
    checkin_existente = Checkin.query.filter_by(
        aluno_id=aluno.id,
        data=hoje,
        horario=horario
    ).first()
    
    if checkin_existente:
        flash("Você já tem reserva para este horário", "info")
        return redirect(url_for("painel_usuario"))

    # Verificar se horário está lotado
    total_checkins = Checkin.query.filter_by(
        data=hoje,
        horario=horario
    ).count()
    
    if total_checkins >= LIMITE_VAGAS:
        flash("Horário lotado. Tente outro horário.", "error")
        return redirect(url_for("painel_usuario"))

    # Criar check-in e debitar crédito
    novo_checkin = Checkin(
        aluno_id=aluno.id,
        data=hoje,
        horario=horario
    )
    
    aluno.creditos -= 1
    
    db.session.add(novo_checkin)
    db.session.commit()
    
    flash(f"Check-in realizado com sucesso para {horario}!", "success")

    return redirect(url_for("painel_usuario"))

@app.route("/cancelar/<horario>")
def cancelar(horario):
    """Cancela reserva do usuário"""
    nome = session.get("usuario")
    if not nome:
        flash("Faça login para cancelar reserva", "error")
        return redirect(url_for("usuario"))
    
    if horario not in HORARIOS:
        flash("Horário inválido", "error")
        return redirect(url_for("painel_usuario"))
    
    # Verificar se ainda é possível cancelar (antes das 15h no horário do Brasil)
    # 15:00 Brasil = 18:00 UTC
    agora_utc = datetime.now(timezone.utc).time()
    if agora_utc > time(18, 0):  # 18:00 UTC = 15:00 Brasil
        flash("Cancelamento não permitido após 15:00h (horário de Brasília)", "error")
        return redirect(url_for("painel_usuario"))

    hoje = date.today()
    
    # Buscar aluno no banco
    aluno = Aluno.query.filter_by(nome=nome).first()
    if not aluno:
        flash("Usuário não encontrado", "error")
        return redirect(url_for("usuario"))

    # Buscar check-in para cancelar
    checkin = Checkin.query.filter_by(
        aluno_id=aluno.id,
        data=hoje,
        horario=horario
    ).first()
    
    if not checkin:
        flash("Você não tem reserva para este horário", "info")
        return redirect(url_for("painel_usuario"))

    # Cancelar check-in e reembolsar crédito
    db.session.delete(checkin)
    aluno.creditos += 1
    db.session.commit()
    
    flash(f"Reserva cancelada para {horario}. Crédito reembolsado!", "success")

    return redirect(url_for("painel_usuario"))

@app.route("/logout")
def logout():
    """Logout do usuário"""
    session.pop("usuario", None)
    session.pop("admin", None)
    flash("Logout realizado com sucesso", "info")
    return redirect(url_for("home"))

def gerar_resumo_checkins():
    """Gera resumo dos check-ins do dia e da semana"""
    hoje = date.today()
    
    # Check-ins de hoje
    checkins_hoje = Checkin.query.filter_by(data=hoje).all()
    total_hoje = len(checkins_hoje)
    
    # Organizar por horário
    checkins_hoje_detalhado = {}
    for horario in HORARIOS:
        nomes = [c.aluno.nome for c in checkins_hoje if c.horario == horario]
        checkins_hoje_detalhado[horario] = nomes
    
    # Check-ins da semana (últimos 7 dias)
    data_inicio = hoje - timedelta(days=6)
    checkins_semana = Checkin.query.filter(
        Checkin.data >= data_inicio,
        Checkin.data <= hoje
    ).all()
    
    total_semana = len(checkins_semana)
    
    # Contar por aluno
    checkins_por_aluno = defaultdict(int)
    for checkin in checkins_semana:
        checkins_por_aluno[checkin.aluno.nome] += 1
    
    return {
        "hoje": {
            "total": total_hoje,
            "por_horario": checkins_hoje_detalhado,
            "data": hoje.strftime("%Y-%m-%d")
        },
        "semana": {
            "total": total_semana,
            "por_aluno": dict(checkins_por_aluno),
            "periodo": f"{data_inicio.strftime('%d/%m')} - {hoje.strftime('%d/%m')}"
        }
    }

# Inicializar banco de dados
init_db()

# Tentar migrar dados existentes do JSON (se existirem)
try:
    with app.app_context():
        migrar_dados_json()
except Exception as e:
    print(f"Aviso: Erro ao migrar dados JSON: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
