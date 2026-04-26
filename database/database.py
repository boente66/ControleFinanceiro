# -*- coding: utf-8 -*-
import sqlite3
import logging
import os
from core.config import DB_PATH

# Configuração de Log para erros de banco
logging.basicConfig(
    filename="database.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class Database:

    def __init__(self, db_name=DB_PATH):
        self.db_name = db_name
        self._ensure_directory()
        self.create_tables()
        self.create_triggers()

    def _ensure_directory(self):
        directory = os.path.dirname(self.db_name)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_name)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Erro ao conectar: {str(e)}", original_exception=e)

    # =====================================================
    # SCHEMA DEFINITION
    # =====================================================
    def create_tables(self):
        with self.connect() as conn:
            conn.executescript("""
-- USUARIOS
CREATE TABLE IF NOT EXISTS usuarios (
    ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    DataNascimento TEXT,
    Sexo TEXT CHECK (Sexo IN ('Masculino','Feminino','Outro')),
    CPF TEXT,                                          
    Email TEXT UNIQUE,
    Login TEXT UNIQUE,
    Senha TEXT NOT NULL,
    Telefone TEXT,
    Celular TEXT,
    Nivel_Acesso TEXT CHECK (Nivel_Acesso IN ('admin','usuario')),
    Tema TEXT DEFAULT 'Claro',
    Idioma TEXT DEFAULT 'pt_BR'
);

-- CATEGORIAS
CREATE TABLE IF NOT EXISTS categorias (
    ID_Categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Tipo TEXT CHECK (Tipo IN ('Despesa','Receita')),
    ID_Usuario INTEGER NOT NULL,
    ID_Categoria_Pai INTEGER,
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
    FOREIGN KEY(ID_Categoria_Pai) REFERENCES categorias(ID_Categoria)
);
CREATE INDEX IF NOT EXISTS idx_categoria_usuario ON categorias(ID_Usuario);

-- CONTAS
CREATE TABLE IF NOT EXISTS contas (
    ID_Conta INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome_Conta TEXT NOT NULL,
    Instituicao TEXT,
    Tipo TEXT,
    Saldo_Atual REAL DEFAULT 0,
    ID_Usuario INTEGER,
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE
);

-- CARTÕES
CREATE TABLE IF NOT EXISTS credito (
    ID_Cartao INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Limite REAL NOT NULL DEFAULT 0,
    Dia_Fechamento INTEGER NOT NULL,
    Dia_Vencimento INTEGER NOT NULL,
    Ativo INTEGER DEFAULT 1,
    ID_Usuario INTEGER,
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE
);

-- FAVORECIDO E ENTIDADES RELACIONADAS
CREATE TABLE IF NOT EXISTS favorecido (
    ID_Favorecido INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Tipo TEXT CHECK (Tipo IN ('PF','PJ')),
    ID_Usuario INTEGER NOT NULL,
    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pessoa_fisica (
    ID_Favorecido INTEGER PRIMARY KEY,
    CPF TEXT,
    Telefone TEXT,
    FOREIGN KEY(ID_Favorecido) REFERENCES favorecido(ID_Favorecido) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pessoa_juridica (
    ID_Favorecido INTEGER PRIMARY KEY,
    CNPJ TEXT,
    Razao_Social TEXT,
    Telefone TEXT,
    FOREIGN KEY(ID_Favorecido) REFERENCES favorecido(ID_Favorecido) ON DELETE CASCADE
);

-- TRANSAÇÕES
CREATE TABLE IF NOT EXISTS transacoes (
    ID_Transacao INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Conta INTEGER NOT NULL,
    Tipo TEXT CHECK (Tipo IN ('Receita','Despesa','Transferência')),
    Descricao TEXT NOT NULL,
    Valor REAL NOT NULL,
    Data TEXT NOT NULL,
    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,
    Notas TEXT,
    ID_Usuario INTEGER NOT NULL,
    FOREIGN KEY(ID_Conta) REFERENCES contas(ID_Conta) ON DELETE CASCADE,
    FOREIGN KEY(ID_Categoria) REFERENCES categorias(ID_Categoria),
    FOREIGN KEY(ID_Favorecido) REFERENCES favorecido(ID_Favorecido),
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE
);

-- AGENDAMENTOS
CREATE TABLE IF NOT EXISTS agendamentos (
    ID_Agendamento INTEGER PRIMARY KEY AUTOINCREMENT,
    Tipo TEXT CHECK (Tipo IN ('Contas a Receber','Contas a Pagar','Transferências')),
    Data TEXT NOT NULL,
    Valor REAL NOT NULL,
    Descricao TEXT,
    Status TEXT CHECK (Status IN ('AGENDADO','EXECUTADO','CANCELADO','ATRASADO')),
    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,
    ID_Conta INTEGER NOT NULL,
    ID_Usuario INTEGER NOT NULL,
    Recorrente INTEGER DEFAULT 0,
    Periodicidade TEXT,
    Ativo INTEGER DEFAULT 1,
    ID_Pai INTEGER,
    FOREIGN KEY(ID_Categoria) REFERENCES categorias(ID_Categoria),
    FOREIGN KEY(ID_Favorecido) REFERENCES favorecido(ID_Favorecido),
    FOREIGN KEY(ID_Conta) REFERENCES contas(ID_Conta),
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE
);

-- LANÇAMENTOS CARTÃO
CREATE TABLE IF NOT EXISTS lancamentos (
    ID_Lancamento INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Cartao INTEGER NOT NULL,
    Data TEXT NOT NULL,
    Competencia_Mes INTEGER NOT NULL,
    Competencia_Ano INTEGER NOT NULL,
    Descricao TEXT,
    Valor REAL NOT NULL,
    ID_Categoria INTEGER,
    Num_Parcelas INTEGER,
    Parcela_Atual INTEGER,
    Paga INTEGER DEFAULT 0,
    Previsto INTEGER DEFAULT 0,
    ID_Usuario INTEGER,
    ID_Conta INTEGER,
    ID_Transacao INTEGER,
    FOREIGN KEY(ID_Cartao) REFERENCES credito(ID_Cartao) ON DELETE CASCADE,
    FOREIGN KEY(ID_Categoria) REFERENCES categorias(ID_Categoria),
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
    FOREIGN KEY(ID_Conta) REFERENCES contas(ID_Conta),
    FOREIGN KEY(ID_Transacao) REFERENCES transacoes(ID_Transacao)
);

-- METAS
CREATE TABLE IF NOT EXISTS metas (
    ID_Meta INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Tipo TEXT CHECK (Tipo IN ('Categoria','Economia','Objetivo')),
    Valor_Alvo REAL NOT NULL,
    Valor_Atual REAL DEFAULT 0,
    ID_Categoria INTEGER,
    Data_Inicio TEXT,
    Data_Fim TEXT,
    ID_Usuario INTEGER NOT NULL,
    Status TEXT DEFAULT 'ATIVA' CHECK (Status IN ('ATIVA','CONCLUIDA','CANCELADA')),
    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,
    Atualizado_Em TEXT,
    FOREIGN KEY(ID_Usuario) REFERENCES usuarios(ID_Usuario) ON DELETE CASCADE,
    FOREIGN KEY(ID_Categoria) REFERENCES categorias(ID_Categoria)
);
            """)

    def create_triggers(self):
        with self.connect() as conn:
            conn.executescript("""
CREATE TRIGGER IF NOT EXISTS trg_pf AFTER INSERT ON favorecido WHEN NEW.Tipo = 'PF'
BEGIN INSERT INTO pessoa_fisica(ID_Favorecido) VALUES (NEW.ID_Favorecido); END;

CREATE TRIGGER IF NOT EXISTS trg_pj AFTER INSERT ON favorecido WHEN NEW.Tipo = 'PJ'
BEGIN INSERT INTO pessoa_juridica(ID_Favorecido) VALUES (NEW.ID_Favorecido); END;
            """)

    # =====================================================
    # CRUD OPERATIONS
    # =====================================================
    def execute_query(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Erro Query: {query} | {str(e)}")
            raise DatabaseError(str(e), query, params, e)
        finally:
            conn.close()

    def execute_insert(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            last_id = cur.lastrowid
            conn.commit()
            return last_id
        except Exception as e:
            conn.rollback()
            logging.error(f"Erro Insert: {query} | {str(e)}")
            raise DatabaseError(str(e), query, params, e)
        finally:
            conn.close()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"Erro FetchAll: {query} | {str(e)}")
            raise DatabaseError(str(e), query, params, e)
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logging.error(f"Erro FetchOne: {query} | {str(e)}")
            raise DatabaseError(str(e), query, params, e)
        finally:
            conn.close()


    def begin(self):
        self.connect().execute("BEGIN")

    def commit(self):
        self.connect().commit()

    def rollback(self):
        self.connect().rollback()

# =====================================================
# ERROR HANDLING
# =====================================================
class DatabaseError(Exception):
    def __init__(self, message, query=None, params=None, original_exception=None):
        super().__init__(message)
        self.message = message
        self.query = query
        self.params = params
        self.error_type = self._detect_sqlite_error(original_exception)

    def _detect_sqlite_error(self, exc):
        if not exc: return None
        import sqlite3
        errors = {
            sqlite3.IntegrityError: "Integridade (FK/UNIQUE)",
            sqlite3.OperationalError: "Operacional (Lock/SQL)",
            sqlite3.ProgrammingError: "Programação (API)",
        }
        return errors.get(type(exc), str(exc))

    def __str__(self):
        return f"DatabaseError: {self.message} | Tipo: {self.error_type} | Query: {self.query}"
