# backup/backup_model.py

import os
import json
from datetime import datetime

from database.database import Database
from utilitarios.crypto_util import encrypt_bytes, decrypt_bytes


class BackupModel:
    """
    Backup lógico (.kp)
    - NÃO copia o .db
    - extrai dados das tabelas
    - criptografa
    - restaura via INSERT
    """

    def __init__(self, database_path: str):
        self.database_path = database_path
        self.db = Database(database_path)

    # =====================================================
    # EXTRAÇÃO DE DADOS
    # =====================================================
    def _extrair_dados(self):

        tabelas = [
            "usuarios",
            "categorias",
            "contas",
            "credito",
            "favorecido",
            "pessoa_fisica",
            "pessoa_juridica",
            "transacoes",
            "agendamentos",
            "lancamentos",
            "metas",
            "recuperacao_senha"
        ]

        dados = {}

        for tabela in tabelas:
            dados[tabela] = self.db.fetch_all(f"SELECT * FROM {tabela}")

        return dados

    # =====================================================
    # BACKUP (.kp)
    # =====================================================
    def criar_backup(self, destino: str, senha: str) -> str:

        if not os.path.isdir(destino):
            raise FileNotFoundError("Pasta de destino inválida.")

        if not senha:
            raise ValueError("Senha obrigatória.")

        # 1️⃣ extrair dados
        dados = self._extrair_dados()

        # 2️⃣ converter para JSON
        json_bytes = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        # 3️⃣ criptografar
        criptografado = encrypt_bytes(json_bytes, senha)

        # 4️⃣ montar estrutura final
        estrutura = {
            "meta": {
                "version": 1,
                "tipo": "kp_logico",
                "data": datetime.now().isoformat()
            },
            "payload": criptografado
        }

        # 5️⃣ salvar arquivo
        nome = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.kp"
        caminho = os.path.join(destino, nome)

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estrutura, f)

        return caminho

    # =====================================================
    # RESTAURAÇÃO (.kp)
    # =====================================================
    def restaurar_backup(self, arquivo: str, senha: str):

        if not os.path.isfile(arquivo):
            raise FileNotFoundError("Backup não encontrado.")

        with open(arquivo, "r", encoding="utf-8") as f:
            estrutura = json.load(f)

        # valida estrutura
        if "payload" not in estrutura:
            raise ValueError("Backup inválido.")

        try:
            # 1️⃣ descriptografar
            json_bytes = decrypt_bytes(estrutura["payload"], senha)

        except Exception:
            raise Exception("Senha inválida ou backup corrompido.")

        # 2️⃣ carregar dados
        dados = json.loads(json_bytes.decode("utf-8"))

        # 3️⃣ restaurar no banco
        with self.db.connect() as conn:
            cursor = conn.cursor()

            # ⚠️ ordem IMPORTANTE (FK)
            ordem_delete = [
                "lancamentos",
                "transacoes",
                "agendamentos",
                "metas",
                "recuperacao_senha",
                "pessoa_fisica",
                "pessoa_juridica",
                "favorecido",
                "credito",
                "contas",
                "categorias",
                "usuarios"
            ]

            for tabela in ordem_delete:
                cursor.execute(f"DELETE FROM {tabela}")

            # inserir dados
            for tabela, registros in dados.items():

                for row in registros:
                    colunas = ", ".join(row.keys())
                    placeholders = ", ".join(["?"] * len(row))

                    cursor.execute(
                        f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})",
                        tuple(row.values())
                    )

            conn.commit()

        return True

    # =====================================================
    # VALIDAR
    # =====================================================
    def validar_backup(self, arquivo: str, senha: str) -> bool:

        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                estrutura = json.load(f)

            decrypt_bytes(estrutura.get("payload"), senha)
            return True

        except Exception:
            return False

    # =====================================================
    # LISTAR
    # =====================================================
    def listar_backups(self, diretorio: str):

        if not os.path.isdir(diretorio):
            return []

        backups = []

        for f in os.listdir(diretorio):
            if f.endswith(".kp"):
                caminho = os.path.join(diretorio, f)

                backups.append({
                    "nome": f,
                    "caminho": caminho,
                    "tamanho": os.path.getsize(caminho),
                    "data": datetime.fromtimestamp(
                        os.path.getmtime(caminho)
                    ).strftime("%d/%m/%Y %H:%M")
                })

        return backups

    # =====================================================
    # EXCLUIR
    # =====================================================
    def excluir_backup(self, arquivo: str):

        if not os.path.exists(arquivo):
            raise FileNotFoundError("Arquivo não encontrado.")

        os.remove(arquivo)
