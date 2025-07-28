from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Aluno(db.Model):
    """Modelo para representar um aluno"""
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(50), nullable=False)
    pagamento = db.Column(db.String(200), nullable=False)
    creditos = db.Column(db.Integer, default=0, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com check-ins
    checkins = db.relationship('Checkin', backref='aluno', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'senha': self.senha,
            'pagamento': self.pagamento,
            'creditos': self.creditos,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

class Checkin(db.Model):
    """Modelo para representar um check-in"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(20), nullable=False)  # "18:00-20:00" ou "20:00-22:00"
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices para melhor performance
    __table_args__ = (
        db.Index('idx_checkin_data_horario', 'data', 'horario'),
        db.Index('idx_checkin_aluno_data', 'aluno_id', 'data'),
    )
    
    def __repr__(self):
        return f'<Checkin {self.aluno.nome} - {self.data} {self.horario}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'aluno_nome': self.aluno.nome,
            'data': self.data.isoformat() if self.data else None,
            'horario': self.horario,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

class Admin(db.Model):
    """Modelo para configurações administrativas"""
    __tablename__ = 'admin_config'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.String(200), nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminConfig {self.chave}: {self.valor}>'