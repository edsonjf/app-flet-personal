from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import json

# Conexão com banco SQLite
engine = create_engine("sqlite:///usuarios.db", echo=False)

# Classe base para os modelos
Base = declarative_base()

# Modelo da tabela de usuários
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=False, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha = Column(String(100), unique=False)
    
    treinos = relationship('Treino', back_populates='usuario')

class Treino(Base):
    __tablename__ = "treinos"
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship('Usuario', back_populates='treinos')
    
    nome = Column(String(150), unique=False, nullable=True)
    exercicios = Column(String)
    
    # Funções para trabalhar com listas json
    def set_exercicios(self, lista):
        self.exercicios = json.dumps(lista)

    def get_exercicios(self):
        return json.loads(self.exercicios)
    
# Cria a tabela se ainda não existir
# def criar_tabelas():
Base.metadata.create_all(bind=engine)

# Sessão para consultas e transações
SessionLocal = sessionmaker(bind=engine)

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