# -*- coding: utf-8 -*-
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
    _initialized_paths = set()

    def __init__(self, db_name=DB_PATH):
        self.db_name = db_name
        self._manual_transaction = False

        self._ensure_directory()
        self.connection = self.connect()

        if self.db_name not in Database._initialized_paths:
            self.create_tables()
            Database._initialized_paths.add(self.db_name)

    # =====================================================
    # CONNECTION
    # =====================================================
    def connect(self):
        try:
            conn = sqlite3.connect(self.db_name)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            return conn

        except sqlite3.Error as e:
            raise DatabaseError(
                f"Erro ao conectar: {str(e)}",
                original_exception=e
            )

    def close(self):
        if getattr(self, "connection", None):
            self.connection.close()

    def _ensure_directory(self):
        directory = os.path.dirname(self.db_name)

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    # =====================================================
    # SCHEMA
    # =====================================================
    def create_tables(self):
        self.connection.executescript("""
-- =====================================================
-- USUÁRIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS usuarios (
    ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    DataNascimento TEXT,
    Sexo TEXT CHECK (
        Sexo IN ('Masculino','Feminino','Outro')
    ),
    CPF TEXT,
    Email TEXT UNIQUE,
    Login TEXT UNIQUE,
    Senha TEXT NOT NULL,
    Telefone TEXT,
    Celular TEXT,
    Nivel_Acesso TEXT CHECK (
        Nivel_Acesso IN ('admin','usuario')
    ),
    Tema TEXT DEFAULT 'Claro',
    Idioma TEXT DEFAULT 'pt_BR'
);

-- =====================================================
-- RECUPERAÇÃO DE SENHA
-- =====================================================
CREATE TABLE IF NOT EXISTS recuperacao_senha (
    ID_Recuperacao INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Usuario INTEGER NOT NULL,
    Token TEXT NOT NULL UNIQUE,
    Codigo TEXT,
    Expira_Em TEXT NOT NULL,
    Utilizado INTEGER DEFAULT 0,
    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,
    IP TEXT,
    User_Agent TEXT,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

-- =====================================================
-- CATEGORIAS
-- =====================================================
CREATE TABLE IF NOT EXISTS categorias (
    ID_Categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Tipo TEXT CHECK (
        Tipo IN ('Despesa','Receita')
    ),
    ID_Usuario INTEGER NOT NULL,
    ID_Categoria_Pai INTEGER,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE,

    FOREIGN KEY(ID_Categoria_Pai)
        REFERENCES categorias(ID_Categoria)
);

-- =====================================================
-- CONTAS
-- =====================================================
CREATE TABLE IF NOT EXISTS contas (
    ID_Conta INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome_Conta TEXT NOT NULL,
    Instituicao TEXT,
    Tipo TEXT,
    Saldo_Atual REAL DEFAULT 0,
    ID_Usuario INTEGER,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

-- =====================================================
-- CARTÕES
-- =====================================================
CREATE TABLE IF NOT EXISTS credito (
    ID_Cartao INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Limite REAL NOT NULL DEFAULT 0,
    Dia_Fechamento INTEGER NOT NULL,
    Dia_Vencimento INTEGER NOT NULL,
    Ativo INTEGER DEFAULT 1,
    ID_Usuario INTEGER,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

-- =====================================================
-- FAVORECIDOS
-- =====================================================
CREATE TABLE IF NOT EXISTS favorecido (
    ID_Favorecido INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    Tipo TEXT CHECK (
        Tipo IN ('PF','PJ')
    ),
    ID_Usuario INTEGER NOT NULL,
    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pessoa_fisica (
    ID_Favorecido INTEGER PRIMARY KEY,
    CPF TEXT UNIQUE,
    Telefone TEXT,

    FOREIGN KEY(ID_Favorecido)
        REFERENCES favorecido(ID_Favorecido)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pessoa_juridica (
    ID_Favorecido INTEGER PRIMARY KEY,
    CNPJ TEXT UNIQUE,
    Razao_Social TEXT,
    Telefone TEXT,

    FOREIGN KEY(ID_Favorecido)
        REFERENCES favorecido(ID_Favorecido)
        ON DELETE CASCADE
);

-- =====================================================
-- TRANSAÇÕES
-- =====================================================
CREATE TABLE IF NOT EXISTS transacoes (
    ID_Transacao INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Conta INTEGER NOT NULL,

    Tipo TEXT CHECK (
        Tipo IN ('Receita','Despesa','Transferência')
    ),

    Descricao TEXT NOT NULL,
    Valor REAL NOT NULL,
    Data TEXT NOT NULL,
    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,
    Notas TEXT,
    ID_Usuario INTEGER NOT NULL,

    FOREIGN KEY(ID_Conta)
        REFERENCES contas(ID_Conta)
        ON DELETE CASCADE,

    FOREIGN KEY(ID_Categoria)
        REFERENCES categorias(ID_Categoria),

    FOREIGN KEY(ID_Favorecido)
        REFERENCES favorecido(ID_Favorecido),

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

-- =====================================================
-- AGENDAMENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS agendamentos (
    ID_Agendamento INTEGER PRIMARY KEY AUTOINCREMENT,

    Tipo TEXT CHECK (
        Tipo IN (
            'Contas a Receber',
            'Contas a Pagar',
            'Transferências',
            'Cartao',
            'Cartão'
        )
    ),

    Data TEXT NOT NULL,
    Valor REAL NOT NULL,
    Descricao TEXT,

    Status TEXT CHECK (
        Status IN (
            'AGENDADO',
            'EXECUTADO',
            'CANCELADO',
            'ATRASADO',
            'INATIVO'
        )
    ),

    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,
    ID_Conta INTEGER,
    ID_Cartao INTEGER,
    ID_Usuario INTEGER NOT NULL,

    Recorrente INTEGER DEFAULT 0,
    Periodicidade TEXT,
    Ativo INTEGER DEFAULT 1,
    ID_Pai INTEGER,
    Parcelas INTEGER DEFAULT 1,

    FOREIGN KEY(ID_Categoria)
        REFERENCES categorias(ID_Categoria),

    FOREIGN KEY(ID_Favorecido)
        REFERENCES favorecido(ID_Favorecido),

    FOREIGN KEY(ID_Conta)
        REFERENCES contas(ID_Conta),

    FOREIGN KEY(ID_Cartao)
        REFERENCES credito(ID_Cartao),

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE
);

-- =====================================================
-- LANÇAMENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS lancamentos (
    ID_Lancamento INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_Cartao INTEGER NOT NULL,
    Data TEXT NOT NULL,
    Competencia_Mes INTEGER NOT NULL,
    Competencia_Ano INTEGER NOT NULL,
    Descricao TEXT,
    Valor REAL NOT NULL,
    ID_Categoria INTEGER,
    ID_Favorecido INTEGER,
    Num_Parcelas INTEGER,
    Parcela_Atual INTEGER,
    Paga INTEGER DEFAULT 0,
    Notas TEXT,
    Previsto INTEGER DEFAULT 0,
    ID_Usuario INTEGER,
    ID_Conta INTEGER,
    ID_Transacao INTEGER,

    FOREIGN KEY(ID_Cartao)
        REFERENCES credito(ID_Cartao)
        ON DELETE CASCADE,

    FOREIGN KEY(ID_Categoria)
        REFERENCES categorias(ID_Categoria),

    FOREIGN KEY(ID_Favorecido)
        REFERENCES favorecido(ID_Favorecido),

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE,

    FOREIGN KEY(ID_Conta)
        REFERENCES contas(ID_Conta),

    FOREIGN KEY(ID_Transacao)
        REFERENCES transacoes(ID_Transacao)
);

-- =====================================================
-- METAS
-- =====================================================
CREATE TABLE IF NOT EXISTS metas (
    ID_Meta INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,

    Tipo TEXT CHECK (
        Tipo IN ('Categoria','Economia','Objetivo')
    ),

    Valor_Alvo REAL NOT NULL,
    Valor_Atual REAL DEFAULT 0,
    ID_Categoria INTEGER,
    Data_Inicio TEXT,
    Data_Fim TEXT,
    ID_Usuario INTEGER NOT NULL,
    Status TEXT DEFAULT 'ATIVA',
    Criado_Em TEXT DEFAULT CURRENT_TIMESTAMP,
    Atualizado_Em TEXT,
    Concluido_Em TEXT,

    FOREIGN KEY(ID_Usuario)
        REFERENCES usuarios(ID_Usuario)
        ON DELETE CASCADE,

    FOREIGN KEY(ID_Categoria)
        REFERENCES categorias(ID_Categoria)
);

-- =====================================================
-- ÍNDICES
-- =====================================================
CREATE UNIQUE INDEX IF NOT EXISTS idx_cpf
ON pessoa_fisica(CPF)
WHERE CPF IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_cnpj
ON pessoa_juridica(CNPJ)
WHERE CNPJ IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_recuperacao_token
ON recuperacao_senha(Token);

CREATE INDEX IF NOT EXISTS idx_recuperacao_usuario
ON recuperacao_senha(ID_Usuario);
""")

        self._run_migrations()
        self.connection.commit()

    # =====================================================
    # MIGRATIONS SIMPLES
    # =====================================================
    def _table_columns(self, table):
        rows = self.connection.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()

        return {row["name"] for row in rows}

    def _add_column_if_missing(self, table, column, definition):
        if column not in self._table_columns(table):
            self.connection.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )

    def _run_migrations(self):
        try:
            self._add_column_if_missing(
                "recuperacao_senha",
                "Codigo",
                "TEXT"
            )

            self._add_column_if_missing(
                "recuperacao_senha",
                "Utilizado",
                "INTEGER DEFAULT 0"
            )

            self._add_column_if_missing(
                "recuperacao_senha",
                "Criado_Em",
                "TEXT"
            )

            self._add_column_if_missing(
                "recuperacao_senha",
                "IP",
                "TEXT"
            )

            self._add_column_if_missing(
                "recuperacao_senha",
                "User_Agent",
                "TEXT"
            )

            self._add_column_if_missing(
                "metas",
                "Concluido_Em",
                "TEXT"
            )

            self._add_column_if_missing(
                "agendamentos",
                "ID_Cartao",
                "INTEGER"
            )

            self._add_column_if_missing(
                "agendamentos",
                "Parcelas",
                "INTEGER DEFAULT 1"
            )

            self._add_column_if_missing(
                "agendamentos",
                "Recorrente",
                "INTEGER DEFAULT 0"
            )

            self._add_column_if_missing(
                "agendamentos",
                "Periodicidade",
                "TEXT"
            )

            self._add_column_if_missing(
                "agendamentos",
                "Ativo",
                "INTEGER DEFAULT 1"
            )

            self._add_column_if_missing(
                "agendamentos",
                "ID_Pai",
                "INTEGER"
            )

        except sqlite3.Error as e:
            raise DatabaseError(
                f"Erro ao executar migrations: {str(e)}",
                original_exception=e
            )

    # =====================================================
    # TRANSACTIONS
    # =====================================================
    def begin(self):
        if self._manual_transaction:
            return

        self._manual_transaction = True
        self.connection.execute("BEGIN")

    def commit(self):
        self.connection.commit()
        self._manual_transaction = False

    def rollback(self):
        self.connection.rollback()
        self._manual_transaction = False

    # =====================================================
    # QUERY
    # =====================================================
    def execute_query(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params or ())

            if not self._manual_transaction:
                self.connection.commit()

            return cur

        except sqlite3.Error as e:
            logging.error(
                f"Erro Query: {query} | {str(e)}"
            )

            raise DatabaseError(
                str(e),
                query,
                params,
                e
            )

    def execute_insert(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params or ())

            if not self._manual_transaction:
                self.connection.commit()

            return cur.lastrowid

        except sqlite3.Error as e:
            logging.error(
                f"Erro Insert: {query} | {str(e)}"
            )

            raise DatabaseError(
                str(e),
                query,
                params,
                e
            )

    def fetch_all(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params or ())

            return [
                dict(row)
                for row in cur.fetchall()
            ]

        except sqlite3.Error as e:
            logging.error(
                f"Erro FetchAll: {query} | {str(e)}"
            )

            raise DatabaseError(
                str(e),
                query,
                params,
                e
            )

    def fetch_one(self, query, params=None):
        try:
            cur = self.connection.cursor()
            cur.execute(query, params or ())

            row = cur.fetchone()

            return dict(row) if row else None

        except sqlite3.Error as e:
            logging.error(
                f"Erro FetchOne: {query} | {str(e)}"
            )

            raise DatabaseError(
                str(e),
                query,
                params,
                e
            )


class DatabaseError(Exception):
    """
    Exceção padrão da camada de persistência.
    Guarda query, parâmetros e erro original para facilitar debug.
    """

    def __init__(
        self,
        message,
        query=None,
        params=None,
        original_exception=None
    ):
        super().__init__(message)

        self.message = message
        self.query = query
        self.params = params
        self.original_exception = original_exception

        self.error_type = (
            type(original_exception).__name__
            if original_exception is not None
            else None
        )

    def __str__(self):
        return self.message

    def to_dict(self):
        return {
            "message": self.message,
            "query": self.query,
            "params": self.params,
            "error_type": self.error_type,
        }
