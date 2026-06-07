# -*- coding: utf-8 -*-
import logging

from database.json_database import JsonDatabase, JsonDatabaseError

logger = logging.getLogger(__name__)


class TranslationStorage:
    """
    Persistência das traduções dinâmicas da aplicação.

    Usa JsonDatabase para salvar/cachear traduções geradas pelo Argos.
    """

    def __init__(self, file_path="translations.json"):
        self.db = JsonDatabase(
            file_path=file_path,
            default_data={}
        )

    def load(self) -> dict:
        try:
            return self.db.load() or {}
        except JsonDatabaseError:
            logger.exception("Erro ao carregar traduções")
            return {}

    def save(self, translations: dict) -> bool:
        try:
            return self.db.save(translations or {})
        except JsonDatabaseError:
            logger.exception("Erro ao salvar traduções")
            return False

    def get(self, language: str, text: str):
        data = self.load()
        return data.get(language, {}).get(text)

    def set(self, language: str, text: str, translated: str) -> bool:
        data = self.load()

        data.setdefault(language, {})
        data[language][text] = translated

        return self.save(data)

    def ensure_language(self, language: str) -> bool:
        data = self.load()
        data.setdefault(language, {})
        return self.save(data)