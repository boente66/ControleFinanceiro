# -*- coding: utf-8 -*-
import json
import os
import logging
from typing import Any

logger = logging.getLogger(__name__)


class JsonDatabaseError(Exception):
    """
    Exceção padrão para erros de persistência JSON.
    """

    def __init__(self, message, file_path=None, original_exception=None):
        super().__init__(message)
        self.message = message
        self.file_path = file_path
        self.original_exception = original_exception
        self.error_type = (
            type(original_exception).__name__
            if original_exception is not None
            else None
        )

    def __str__(self):
        return self.message


class JsonDatabase:
    """
    Camada genérica de persistência em JSON.

    Usada para arquivos como:
    - configuracoes.json
    - translations.json
    - cache.json
    """

    def __init__(self, file_path: str, default_data: Any = None):
        if not file_path:
            raise ValueError("Caminho do arquivo JSON não informado.")

        self.file_path = file_path
        self.default_data = default_data if default_data is not None else {}

        self._ensure_directory()
        self._ensure_file()

    # ======================================================
    # SETUP
    # ======================================================
    def _ensure_directory(self):
        directory = os.path.dirname(self.file_path)

        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            self.save(self.default_data)

    # ======================================================
    # READ
    # ======================================================
    def load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()

                if not content:
                    return self.default_data

                return json.loads(content)

        except json.JSONDecodeError as e:
            logger.exception("JSON inválido em %s", self.file_path)
            raise JsonDatabaseError(
                "Arquivo JSON inválido.",
                self.file_path,
                e
            )

        except OSError as e:
            logger.exception("Erro ao ler JSON %s", self.file_path)
            raise JsonDatabaseError(
                "Erro ao ler arquivo JSON.",
                self.file_path,
                e
            )

    # ======================================================
    # WRITE
    # ======================================================
    def save(self, data) -> bool:
        try:
            temp_path = f"{self.file_path}.tmp"

            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True
                )

            os.replace(temp_path, self.file_path)
            return True

        except OSError as e:
            logger.exception("Erro ao salvar JSON %s", self.file_path)
            raise JsonDatabaseError(
                "Erro ao salvar arquivo JSON.",
                self.file_path,
                e
            )

    # ======================================================
    # HELPERS
    # ======================================================
    def exists(self) -> bool:
        return os.path.exists(self.file_path)

    def delete(self) -> bool:
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)

            return True

        except OSError as e:
            logger.exception("Erro ao excluir JSON %s", self.file_path)
            raise JsonDatabaseError(
                "Erro ao excluir arquivo JSON.",
                self.file_path,
                e
            )

    def update(self, callback):
        """
        Carrega o JSON, aplica alteração via callback e salva.

        Exemplo:
            db.update(lambda data: data.update({"tema": "dark"}))
        """
        data = self.load()

        callback(data)

        self.save(data)

        return data