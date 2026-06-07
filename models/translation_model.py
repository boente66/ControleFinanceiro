# -*- coding: utf-8 -*-

import os

from database.json_database import JsonDatabase
from core.config import DATA_DIR


class TranslationModel:
    """
    Persistência de traduções.

    Responsável por:
    - carregar traduções
    - salvar traduções
    - buscar tradução específica
    - adicionar tradução nova
    - remover tradução
    - limpar idioma
    """

    def __init__(self):

        file_path = os.path.join(
            DATA_DIR,
            "translations.json"
        )

        self.db = JsonDatabase(
            file_path=file_path,
            default_data={}
        )

    # =====================================================
    # LOAD
    # =====================================================
    def load_translations(self) -> dict:
        return self.db.load()

    # =====================================================
    # SAVE
    # =====================================================
    def save_translations(self, translations: dict) -> bool:
        return self.db.save(translations)

    # =====================================================
    # GET
    # =====================================================
    def get_translation(
        self,
        language: str,
        original_text: str
    ):

        translations = self.db.load()

        return (
            translations
            .get(language, {})
            .get(original_text)
        )

    # =====================================================
    # EXISTS
    # =====================================================
    def exists(
        self,
        language: str,
        original_text: str
    ) -> bool:

        return (
            self.get_translation(
                language,
                original_text
            ) is not None
        )

    # =====================================================
    # SET
    # =====================================================
    def set_translation(
        self,
        language: str,
        original_text: str,
        translated_text: str
    ) -> bool:

        translations = self.db.load()

        translations.setdefault(
            language,
            {}
        )

        translations[language][original_text] = translated_text

        return self.db.save(translations)

    # =====================================================
    # REMOVE
    # =====================================================
    def remove_translation(
        self,
        language: str,
        original_text: str
    ) -> bool:

        translations = self.db.load()

        if (
            language in translations
            and original_text in translations[language]
        ):
            del translations[language][original_text]

            return self.db.save(translations)

        return False

    # =====================================================
    # LANGUAGE DICT
    # =====================================================
    def get_language_dict(
        self,
        language: str
    ) -> dict:

        translations = self.db.load()

        return translations.get(
            language,
            {}
        )

    # =====================================================
    # ADD LANGUAGE
    # =====================================================
    def add_language(
        self,
        language: str
    ) -> bool:

        translations = self.db.load()

        translations.setdefault(
            language,
            {}
        )

        return self.db.save(translations)

    # =====================================================
    # CLEAR LANGUAGE
    # =====================================================
    def clear_language(
        self,
        language: str
    ) -> bool:

        translations = self.db.load()

        if language in translations:
            translations[language] = {}

            return self.db.save(translations)

        return False