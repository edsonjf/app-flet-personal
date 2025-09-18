from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, Date, ARRAY, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
import pytz
import os
import psycopg2
from dotenv import load_dotenv

# Fuso horário do Brasil
fuso_br = pytz.timezone("America/Sao_Paulo")

load_dotenv()

# Obtém a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada no .env")

# Cria engine e sessão
engine = create_engine(DATABASE_URL, echo=False)
# Sessão para consultas e transações
SessionLocal = sessionmaker(bind=engine)

# Classe base para os modelos
Base = declarative_base()

# Modelo da tabela de usuários
class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(100), unique=False)
    nascimento = Column(Date, unique=False, nullable=True)
    sexo = Column(String(10), unique=False)
    
    # Relacionamento 1-para-N 
    treinos = relationship("Treino", back_populates="usuario")
    questionario = relationship('QuestionarioDor', back_populates='usuario')
    medidas = relationship("ControleMedida", back_populates="usuario")
    controle_acessos = relationship("ControleAcesso", back_populates="usuario")
    pse = relationship("Pse", back_populates="usuario")
    ciclo_menstrual = relationship("CicloMenstrual", back_populates="usuario")

class Treino(Base):
    __tablename__ = 'treinos'

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    descricao = Column(String)

    usuario_id = Column(Integer, ForeignKey('usuarios.id'))

    usuario = relationship("Usuario", back_populates="treinos")
    exercicios_prescritos = relationship("ExercicioPrescrito", back_populates="treino")
    treinos_realizados = relationship("TreinoRealizado", back_populates="treino")
    controle_acessos = relationship("ControleAcesso", back_populates="treino")
    pse = relationship("Pse", back_populates="treino")

class Exercicio(Base):
    __tablename__ = 'exercicios'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    membro = Column(String(10), nullable=True)
    ativacao_muscular = Column(String(100), nullable=True)
    descricao = Column(String)

    exercicios_prescritos = relationship("ExercicioPrescrito", back_populates="exercicio")

class ExercicioPrescrito(Base):
    __tablename__ = 'exercicios_prescritos'

    id = Column(Integer, primary_key=True)
    treino_id = Column(Integer, ForeignKey('treinos.id'))
    exercicio_id = Column(Integer, ForeignKey('exercicios.id'))

    status = Column(String, default='ativo')  # entregue, pendente, etc.
    series = Column(Integer, nullable=True)
    repeticoes = Column(Integer, nullable=True)
    tempo = Column(Float, nullable=True)
    peso = Column(Float, nullable=True)
    intervalo = Column(Float, nullable=True)
    data_prescricao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    treino = relationship("Treino", back_populates="exercicios_prescritos")
    exercicio = relationship("Exercicio", back_populates="exercicios_prescritos")

class QuestionarioDor(Base):
    __tablename__ = 'questionario_dor'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    usuario_id = Column(Integer, ForeignKey('usuarios.id')) 
    
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone("America/Sao_Paulo")))
    pre_pos_treino = Column(String(20), unique=False, nullable=True)
    local = Column(ARRAY(Integer), unique=False, nullable=True)
    intensidade = Column(Integer, unique=False, nullable=True)
    
    usuario = relationship('Usuario', back_populates='questionario')

class ControleMedida(Base):
    __tablename__ = 'controle_medidas'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    peso_corporal = Column(Float)
    altura = Column(Float)

    usuario = relationship("Usuario", back_populates="medidas")

class ControleAcesso(Base):
  __tablename__ = 'controle_acessos'

  id = Column(Integer, primary_key=True)
  usuario_id = Column(Integer, ForeignKey('usuarios.id'))
  treino_id = Column(Integer, ForeignKey('treinos.id'))
  data_acesso = Column(DateTime, default=None)
  treino_inicio = Column(DateTime,default=None)
  treino_fim = Column(DateTime,default=None)
  
  usuario = relationship("Usuario", back_populates="controle_acessos")
  treino = relationship("Treino", back_populates="controle_acessos")
  
class TreinoRealizado(Base):
  __tablename__ = 'treinos_realizados'

  id = Column(Integer, primary_key=True)
  usuario_id = Column(Integer, ForeignKey('usuarios.id'))
  treino_id = Column(Integer, ForeignKey('treinos.id'))
  exercicio_id = Column(Integer, ForeignKey('exercicios.id'))
#   exercicio_nome = Column(String(50), nullable=True)
  serie = Column(Integer, nullable=True)
  repeticoes = Column(Integer, nullable=True)
  tempo = Column(Float, nullable=True)
  carga = Column(Float, nullable=True)
  data = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
  data_fim = Column(DateTime(timezone=True), default=None)

  treino = relationship("Treino", back_populates="treinos_realizados")   

class Pse(Base):
    __tablename__ = 'tabela_pse'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    treino_id = Column(Integer, ForeignKey('treinos.id'))
    intensidade = Column(Integer, unique=False, nullable=True)
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    usuario = relationship("Usuario", back_populates="pse")
    treino = relationship("Treino", back_populates="pse")
    
class CicloMenstrual(Base):
    __tablename__ = 'ciclo_menstrual'
    
    id = Column(Integer, primary_key=True)
    data = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    ciclo = Column(String(3), unique=False, nullable=True)
    
    # Relacionamento 1-para-N 
    usuario = relationship("Usuario", back_populates="ciclo_menstrual")
    
# Cria a tabela se ainda não existir
Base.metadata.create_all(bind=engine)
