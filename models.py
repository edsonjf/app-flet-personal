from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Date, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date
import os
import psycopg2
from dotenv import load_dotenv

# Conexão com banco SQLite
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, "personal.db")
# engine = create_engine(
#     f"sqlite:///{db_path}",
#     connect_args={"check_same_thread": False},
#     echo=False
#     )
# senha = 'Pds24#!'
# # engine = create_engine(
# uri = f"postgresql+psycopg2://postgres:[{senha}]@db.idxwdmkvhjohzsuevrpu.supabase.co:5432/postgres",
#     # echo=False
# # )

# conn = psycopg2.connect(uri)

# Supabase
# Carrega variáveis de ambiente do .env
load_dotenv()

# Obtém a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada no .env")

# Cria engine e sessão
engine = create_engine(DATABASE_URL, echo=True)
# Sessão para consultas e transações
SessionLocal = sessionmaker(bind=engine)

# Classe base para os modelos
Base = declarative_base()

# Modelo da tabela de usuários
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=False, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(100), unique=False)
    nascimento = Column(Date, unique=False, nullable=True)
    
    treinos = relationship('Treino', back_populates='usuario')
    questionario = relationship('QuestionarioDor', back_populates='usuario')
    
    # Relacionamento 1-para-N com ControlePeso
    medidas = relationship("ControleMedida", back_populates="usuario")

class Exercicio(Base):
    __tablename__ = "exercicios"
    
    id = Column(Integer, primary_key=True)
    
    usuarios = relationship('Treino', back_populates='exercicios')
    
    nome = Column(String(150), unique=False, nullable=True)
    series = Column(Integer, unique=False, nullable=True)
    repeticoes = Column(Integer, unique=False, nullable=True)
    peso = Column(Float, unique=False, nullable=True)
    intervalo = Column(Float, unique=False, nullable=True)
    
# Tabela de associativa
class Treino(Base):
    __tablename__ = "treinos"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'))
    
    nome = Column(String(150), unique=False, nullable=True)
    data = Column(Date, default=date.today)
    descricao = Column(String)
    
    usuario = relationship('Usuario', back_populates='treinos')
    exercicios = relationship('Exercicio', back_populates='usuarios')
    
class QuestionarioDor(Base):
    __tablename__ = 'questionario_dor'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    usuario_id = Column(Integer, ForeignKey('usuarios.id')) 
    
    data = Column(Date, default=date.today)
    pre_pos_treino = Column(String(20), unique=False, nullable=True)
    local = Column(Integer, unique=False, nullable=True)
    intensidade = Column(Integer, unique=False, nullable=True)
    
    usuario = relationship('Usuario', back_populates='questionario')
    
class ControleMedida(Base):
    __tablename__ = 'controle_medidas'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    data = Column(Date, default=date.today)
    peso_corporal = Column(Float)
    altura = Column(Float)

    usuario = relationship("Usuario", back_populates="medidas")
    
# Cria a tabela se ainda não existir
Base.metadata.create_all(bind=engine)

# conn = "sqlite:///db.db"

# engine = create_engine(conn, echo=True)
# Session = sessionmaker(bind=engine)
# Session = Session()
# Base = declarative_base()

# class Usuario(Base):
#     __tablename__ = 'usuarios'
    
#     id = Column(Integer, primary_key=True)
#     nome = Column(String(100))
#     email = Column(String(100))
#     senha = Column(String(100)) 
    
# Base.metadata.create_all(engine)