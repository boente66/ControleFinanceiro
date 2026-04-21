# -*- coding: utf-8 -*-
import weakref
from PyQt5 import sip
from PyQt5.QtWidgets import QWidget, QTableWidget


class TranslatorApp:

    _bindings = []
    _translations = {}
    _current_lang = "pt"

    # 🔥 guarda texto original
    _original_texts = {}

    # ======================================================
    # CONFIGURAÇÃO DE IDIOMA
    # ======================================================
    @classmethod
    def set_language(cls, lang):
        cls._current_lang = lang
        cls.translate_all()

    @classmethod
    def load_translations(cls, translations: dict):
        cls._translations = translations or {}

    # ======================================================
    # TRADUÇÃO
    # ======================================================
    @classmethod
    def get(cls, texto: str) -> str:

        if not texto:
            return ""

        lang_dict = cls._translations.get(cls._current_lang, {})
        return lang_dict.get(texto, texto)

    # ======================================================
    # AUTO TRANSLATION
    # ======================================================
    @classmethod
    def enable_auto_translation(cls, widget):

        def callback():
            cls._translate_widget(widget)

        cls.bind(callback, widget)
        cls._translate_widget(widget)  # 🔥 traduz na hora

    # ======================================================
    # CORE ENGINE
    # ======================================================
    @classmethod
    def _translate_widget(cls, widget):

        # 🔹 TEXT (QLabel, QPushButton, etc)
        if hasattr(widget, "setText") and hasattr(widget, "text"):
            try:
                original = cls._original_texts.get(widget)

                if original is None:
                    original = widget.text()
                    cls._original_texts[widget] = original

                widget.setText(cls.get(original))
            except Exception:
                pass

        # 🔹 PLACEHOLDER
        if hasattr(widget, "setPlaceholderText") and hasattr(widget, "placeholderText"):
            try:
                key = (widget, "placeholder")

                original = cls._original_texts.get(key)

                if original is None:
                    original = widget.placeholderText()
                    cls._original_texts[key] = original

                widget.setPlaceholderText(cls.get(original))
            except Exception:
                pass

        # 🔹 TABELAS
        if isinstance(widget, QTableWidget):
            try:
                headers = []

                for i in range(widget.columnCount()):
                    item = widget.horizontalHeaderItem(i)
                    if item:
                        headers.append(item.text())
                    else:
                        headers.append("")

                widget.setHorizontalHeaderLabels(
                    [cls.get(h) for h in headers]
                )
            except Exception:
                pass

        # 🔥 CORREÇÃO AQUI (TODOS OS FILHOS)
        for child in widget.findChildren(QWidget):
            cls._translate_widget(child)

    # ======================================================
    # BIND / UNBIND
    # ======================================================
    @classmethod
    def bind(cls, callback, widget):
        cls._bindings.append((callback, weakref.ref(widget)))

    @classmethod
    def unbind(cls, widget):
        cls._bindings = [
            (cb, ref) for cb, ref in cls._bindings
            if ref() is not widget
        ]

        # limpa cache de texto também
        cls._original_texts = {
            k: v for k, v in cls._original_texts.items()
            if not (isinstance(k, tuple) and k[0] is widget) and k is not widget
        }

    # ======================================================
    # EXECUÇÃO GLOBAL
    # ======================================================
    @classmethod
    def translate_all(cls):

        novos = []

        for callback, widget_ref in cls._bindings:

            widget = widget_ref()

            if widget is None or sip.isdeleted(widget):
                continue

            try:
                callback()
                novos.append((callback, widget_ref))
            except RuntimeError:
                continue

        cls._bindings = novos
