import sqlite3
import logging
import os
from core.config import DB_PATH


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

    # =====================================================
    # GARANTE DIRETÓRIO
    # =====================================================

    def _ensure_directory(self):
        directory = os.path.dirname(self.db_name)

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    # =====================================================
    # CONEXÃO
    # =====================================================

    def connect(self):

        try:
            conn = sqlite3.connect(self.db_name)

            conn.execute("PRAGMA foreign_keys = ON;")

            conn.row_factory = sqlite3.Row

            return conn

        except sqlite3.Error as e:

            logging.error(f"Erro ao conectar: {e}")

            raise DatabaseError(str(e))

    # =====================================================
    # CREATE TABLES
    # =====================================================

    def create_tables(self):

        try:

            with self.connect() as conn:

                cursor = conn.cursor()

                script = """

-- =====================================================
-- USUARIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS usuarios (

    ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome TEXT NOT NULL,
    DataNascimento TEXT,
    Sexo TEXT,
    CPF TEXT,

    Telefone TEXT,
    Celular TEXT,

    Email TEXT NOT NULL UNIQUE,
    Login TEXT NOT NULL UNIQUE,
    Senha TEXT NOT NULL,

    Nivel_Acesso TEXT NOT NULL
        CHECK (Nivel_Acesso IN ('admin','usuario')),

    Tema TEXT DEFAULT 'Claro',
    Idioma TEXT DEFAULT 'pt_BR'

);

CREATE INDEX IF NOT EXISTS idx_usuario_email
ON usuarios(Email);



-- =====================================================
-- RECUPERAÇÃO SENHA
-- =====================================================

CREATE TABLE IF NOT EXISTS recuperacao_senha (

    ID_Recuperacao INTEGER PRIMARY KEY AUTOINCREMENT,

    ID_Usuario INTEGER NOT NULL,

    Token TEXT NOT NULL,
    Expira_Em TEXT NOT NULL,

    Usado INTEGER DEFAULT 0,

    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE
);



-- =====================================================
-- CATEGORIAS
-- =====================================================

CREATE TABLE IF NOT EXISTS categorias (

    ID_Categoria INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome TEXT NOT NULL,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('Despesa','Receita')),

    ID_Usuario INTEGER NOT NULL,

    ID_Categoria_Pai INTEGER NULL,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE,

    FOREIGN KEY (ID_Categoria_Pai)
    REFERENCES categorias(ID_Categoria)

);

CREATE INDEX IF NOT EXISTS idx_categoria_usuario
ON categorias(ID_Usuario);



-- =====================================================
-- CONTAS
-- =====================================================

CREATE TABLE IF NOT EXISTS contas (

    ID_Conta INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome_Conta TEXT NOT NULL,

    Instituicao TEXT,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('Corrente','Poupança','Investimento')),

    Saldo_Atual REAL NOT NULL,

    ID_Usuario INTEGER,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE

);

CREATE INDEX IF NOT EXISTS idx_contas_usuario
ON contas(ID_Usuario);



-- =====================================================
-- CARTÃO CRÉDITO
-- =====================================================

CREATE TABLE IF NOT EXISTS credito (

    ID_Cartao INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome TEXT NOT NULL,

    Limite REAL NOT NULL DEFAULT 0.0,

    Dia_Fechamento INTEGER NOT NULL,
    Dia_Vencimento INTEGER NOT NULL,

    Ativo INTEGER DEFAULT 1,

    ID_Usuario INTEGER,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE

);



-- =====================================================
-- FAVORECIDOS
-- =====================================================

CREATE TABLE IF NOT EXISTS favorecidos (

    ID_Favorecido INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome TEXT NOT NULL,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('PF','PJ')),

    ID_Usuario INTEGER NOT NULL,

    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE

);

CREATE INDEX IF NOT EXISTS idx_favorecidos_usuario
ON favorecidos(ID_Usuario);



-- =====================================================
-- PESSOA FÍSICA
-- =====================================================

CREATE TABLE IF NOT EXISTS pessoa_fisica (

    ID_Favorecido INTEGER PRIMARY KEY,

    CPF TEXT,
    Telefone TEXT,

    FOREIGN KEY (ID_Favorecido)
    REFERENCES favorecidos(ID_Favorecido)
    ON DELETE CASCADE

);



-- =====================================================
-- PESSOA JURÍDICA
-- =====================================================

CREATE TABLE IF NOT EXISTS pessoa_juridica (

    ID_Favorecido INTEGER PRIMARY KEY,

    CNPJ TEXT,
    Razao_Social TEXT,
    Telefone TEXT,

    FOREIGN KEY (ID_Favorecido)
    REFERENCES favorecidos(ID_Favorecido)
    ON DELETE CASCADE

);



-- =====================================================
-- TRANSAÇÕES
-- =====================================================

CREATE TABLE IF NOT EXISTS transacoes (

    ID_Transacao INTEGER PRIMARY KEY AUTOINCREMENT,

    ID_Conta INTEGER NOT NULL,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('Receita','Despesa','Transferência')),

    Descricao TEXT NOT NULL,

    Valor REAL NOT NULL,

    Data TEXT NOT NULL,

    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,

    Notas TEXT,

    ID_Usuario INTEGER NOT NULL,

    FOREIGN KEY (ID_Conta)
    REFERENCES contas(ID_Conta)
    ON DELETE CASCADE,

    FOREIGN KEY (ID_Categoria)
    REFERENCES categorias(ID_Categoria),

    FOREIGN KEY (ID_Favorecido)
    REFERENCES favorecidos(ID_Favorecido),

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE

);

CREATE INDEX IF NOT EXISTS idx_transacoes_usuario
ON transacoes(ID_Usuario);



-- =====================================================
-- AGENDAMENTOS
-- =====================================================

CREATE TABLE IF NOT EXISTS agendamentos (

    ID_Agendamento INTEGER PRIMARY KEY AUTOINCREMENT,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('Contas a Receber','Contas a Pagar','Transferências')),

    Data TEXT NOT NULL,
    Valor REAL NOT NULL,

    Descricao TEXT,

    Status TEXT NOT NULL
        CHECK (Status IN ('AGENDADO','EXECUTADO','CANCELADO','ATRASADO')),

    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,

    ID_Conta INTEGER NOT NULL,

    ID_Usuario INTEGER NOT NULL,

    Recorrente INTEGER DEFAULT 0,

    Periodicidade TEXT,

    Ativo INTEGER DEFAULT 1,

    ID_Pai INTEGER,

    FOREIGN KEY (ID_Categoria)
    REFERENCES categorias(ID_Categoria),

    FOREIGN KEY (ID_Favorecido)
    REFERENCES favorecidos(ID_Favorecido),

    FOREIGN KEY (ID_Conta)
    REFERENCES contas(ID_Conta),

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE

);

CREATE INDEX IF NOT EXISTS idx_agendamentos_usuario
ON agendamentos(ID_Usuario);



-- =====================================================
-- LANÇAMENTOS CARTÃO
-- =====================================================

CREATE TABLE IF NOT EXISTS lancamentos (

    ID_Lancamento INTEGER PRIMARY KEY AUTOINCREMENT,

    ID_Cartao INTEGER NOT NULL,

    Data TEXT NOT NULL,

    -- 🔥 NOVO (ESSENCIAL)
    Competencia_Mes INTEGER NOT NULL,
    Competencia_Ano INTEGER NOT NULL,

    Descricao TEXT,

    Valor REAL NOT NULL,

    ID_Categoria INTEGER,

    Parcelado INTEGER DEFAULT 0,
    Num_Parcelas INTEGER,
    Parcela_Atual INTEGER,

    Paga INTEGER DEFAULT 0,

    Notas TEXT,

    ID_Usuario INTEGER,

    ID_Conta INTEGER,
    ID_Transacao INTEGER,
    Previsto INTEGER DEFAULT 0,

    FOREIGN KEY (ID_Cartao)
    REFERENCES credito(ID_Cartao)
    ON DELETE CASCADE,

    FOREIGN KEY (ID_Categoria)
    REFERENCES categorias(ID_Categoria),

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE,

    FOREIGN KEY (ID_Conta)
    REFERENCES contas(ID_Conta),

    FOREIGN KEY (ID_Transacao)
    REFERENCES transacoes(ID_Transacao)
    
);



-- =====================================================
-- METAS
-- =====================================================

CREATE TABLE IF NOT EXISTS metas (

    ID_Meta INTEGER PRIMARY KEY AUTOINCREMENT,

    Nome TEXT NOT NULL,

    Tipo TEXT NOT NULL
        CHECK (Tipo IN ('Categoria','Economia','Objetivo')),

    Valor_Alvo REAL NOT NULL,

    ID_Categoria INTEGER NULL,

    Data_Inicio TEXT,
    Data_Fim TEXT,

    ID_Usuario INTEGER NOT NULL,

    Status TEXT NOT NULL DEFAULT 'ATIVA'
        CHECK (Status IN ('ATIVA','CONCLUIDA','CANCELADA')),

    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,
    Concluido_Em TEXT,

    FOREIGN KEY (ID_Usuario)
    REFERENCES usuarios(ID_Usuario)
    ON DELETE CASCADE,

    FOREIGN KEY (ID_Categoria)
    REFERENCES categorias(ID_Categoria)

);

CREATE INDEX IF NOT EXISTS idx_metas_usuario
ON metas(ID_Usuario);

"""

                cursor.executescript(script)

                conn.commit()

        except sqlite3.Error as e:

            logging.error(f"Erro ao criar tabelas: {e}")

            raise DatabaseError(str(e))

    # =====================================================
    # CREATE TRIGGERS
    # =====================================================

    def create_triggers(self):

        try:

            with self.connect() as conn:

                cursor = conn.cursor()

                script = """

CREATE TRIGGER IF NOT EXISTS trg_insert_pf
AFTER INSERT ON favorecidos
WHEN NEW.Tipo = 'PF'
BEGIN
    INSERT INTO pessoa_fisica (ID_Favorecido)
    VALUES (NEW.ID_Favorecido);
END;



CREATE TRIGGER IF NOT EXISTS trg_insert_pj
AFTER INSERT ON favorecidos
WHEN NEW.Tipo = 'PJ'
BEGIN
    INSERT INTO pessoa_juridica (ID_Favorecido)
    VALUES (NEW.ID_Favorecido);
END;

"""

                cursor.executescript(script)

                conn.commit()

        except sqlite3.Error as e:

            logging.error(f"Erro ao criar triggers: {e}")

            raise DatabaseError(str(e))

    # =====================================================
    # MÉTODOS AUXILIARES
    # =====================================================

    def execute_query(self, query, params=None):

        try:

            with self.connect() as conn:

                cur = conn.cursor()

                cur.execute(query, params or ())

                conn.commit()

        except sqlite3.Error as e:

            logging.error(f"Erro execute_query: {e}")

            raise DatabaseError(str(e))

    def execute_insert(self, query, params=None):

        try:

            with self.connect() as conn:

                cur = conn.cursor()

                cur.execute(query, params or ())

                conn.commit()

                return cur.lastrowid

        except sqlite3.Error as e:

            logging.error(f"Erro execute_insert: {e}")

            raise DatabaseError(str(e))

    def fetch_all(self, query, params=None):

        try:

            with self.connect() as conn:

                cur = conn.cursor()

                cur.execute(query, params or ())

                return [dict(row) for row in cur.fetchall()]

        except sqlite3.Error as e:

            logging.error(f"Erro fetch_all: {e}")

            raise DatabaseError(str(e))

    def fetch_one(self, query, params=None):

        try:

            with self.connect() as conn:

                cur = conn.cursor()

                cur.execute(query, params or ())

                row = cur.fetchone()

                return dict(row) if row else None

        except sqlite3.Error as e:

            logging.error(f"Erro fetch_one: {e}")

            raise DatabaseError(str(e))


# =====================================================
# EXCEÇÃO
# =====================================================

class DatabaseError(Exception):

    def __init__(self, message, query=None, params=None, original_exception=None):
        super().__init__(message)

        self.message = message
        self.query = query
        self.params = params
        self.original_exception = original_exception

        self.error_type = self._detect_sqlite_error(original_exception)

    def __str__(self):

        base = f"DatabaseError: {self.message}"

        if self.error_type:
            base += f"\nTipo: {self.error_type}"

        if self.query:
            base += f"\nQuery: {self.query}"

        if self.params:
            base += f"\nParams: {self.params}"

        return base

    # --------------------------------------------------
    # DETECTA TIPO DO ERRO SQLITE
    # --------------------------------------------------

    def _detect_sqlite_error(self, exc):

        if not exc:
            return None

        sqlite_errors = {

            sqlite3.IntegrityError:
                "Violação de integridade (FK ou UNIQUE)",

            sqlite3.OperationalError:
                "Erro operacional (SQL inválido ou tabela inexistente)",

            sqlite3.ProgrammingError:
                "Erro de programação (uso incorreto da API)",

            sqlite3.DataError:
                "Erro de dados",

            sqlite3.InterfaceError:
                "Erro de interface SQLite",

            sqlite3.DatabaseError:
                "Erro geral do banco de dados",

        }

        return sqlite_errors.get(type(exc), str(exc))
