from core.session import Session
from core.i18n import t

import weakref
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class TranslatorApp:

    _callbacks = []
    _lock_refresh = False

    # ==================================================
    # CORE
    # ==================================================
    @classmethod
    def set_language(cls, idioma):
        Session.set_config("idioma", idioma)
        cls.refresh()

    @classmethod
    def current(cls):
        return Session.get_config("idioma", "Português")

    # ==================================================
    # CACHE
    # ==================================================
    @classmethod
    @lru_cache(maxsize=5000)
    def _translate_cached(cls, texto, idioma):
        return cls._translate_internal(texto, idioma)

    @classmethod
    def _translate_internal(cls, texto, idioma):

        # 1️⃣ dicionário local
        try:
            traduzido = t(texto, idioma)
            if traduzido != texto:
                return traduzido
        except Exception:
            pass

        # 2️⃣ fallback Argos
        try:
            from services.argos_service import ArgosService

            origem = "pt"
            destino = cls._map_language(idioma)

            return ArgosService.traduzir(texto, origem, destino)

        except Exception:
            return texto

    @classmethod
    def _translate(cls, texto, idioma):
        return cls._translate_cached(texto, idioma)

    # ==================================================
    # MAPA IDIOMA
    # ==================================================
    @staticmethod
    def _map_language(idioma):
        return {
            "Português": "pt",
            "Inglês": "en",
            "Espanhol": "es"
        }.get(idioma, "en")

    # ==================================================
    # REFRESH GLOBAL
    # ==================================================
    @classmethod
    def refresh(cls):

        if cls._lock_refresh:
            return

        cls._lock_refresh = True

        try:
            idioma = cls.current()
            ativos = []

            for callback, ref in cls._callbacks:
                if ref() is None:
                    continue

                try:
                    callback(idioma)
                    ativos.append((callback, ref))
                except Exception:
                    logger.exception("[Translator] erro refresh")

            cls._callbacks = ativos

        finally:
            cls._lock_refresh = False

    # ==================================================
    # REGISTRAR CALLBACK
    # ==================================================
    @classmethod
    def _register(cls, callback, ref):
        cls._callbacks.append((callback, ref))
        Session.on_idioma_change(callback)

    # ==================================================
    # 🔥 AUTO TRANSLATE TREE
    # ==================================================
    @classmethod
    def auto_translate_tree(cls, root):

        idioma = cls.current()

        for widget in root.findChildren(object):

            try:
                # TEXT
                if hasattr(widget, "text") and hasattr(widget, "setText"):

                    if not hasattr(widget, "_original_text"):
                        widget._original_text = widget.text()

                    base = widget._original_text
                    if base:
                        widget.setText(cls._translate(base, idioma))

                # PLACEHOLDER
                if hasattr(widget, "placeholderText") and hasattr(widget, "setPlaceholderText"):

                    if not hasattr(widget, "_original_placeholder"):
                        widget._original_placeholder = widget.placeholderText()

                    base = widget._original_placeholder
                    if base:
                        widget.setPlaceholderText(cls._translate(base, idioma))

                # TITLE
                if hasattr(widget, "title") and hasattr(widget, "setTitle"):

                    if not hasattr(widget, "_original_title"):
                        widget._original_title = widget.title()

                    base = widget._original_title
                    if base:
                        widget.setTitle(cls._translate(base, idioma))

                # COMBO
                if hasattr(widget, "count") and hasattr(widget, "setItemText"):

                    if not hasattr(widget, "_original_items"):
                        widget._original_items = [
                            widget.itemText(i) for i in range(widget.count())
                        ]

                    for i, texto in enumerate(widget._original_items):
                        widget.setItemText(i, cls._translate(texto, idioma))

            except Exception:
                logger.exception("[Translator] erro auto tree")

    # ==================================================
    # ATIVAR GLOBAL
    # ==================================================
    @classmethod
    def enable_auto_translation(cls, root):

        ref = weakref.ref(root)

        def update(_):
            obj = ref()
            if obj is None:
                return
            cls.auto_translate_tree(obj)

        cls.auto_translate_tree(root)
        cls._register(update, ref)

    # ==================================================
    # TEXTO DINÂMICO
    # ==================================================
    @classmethod
    def auto(cls, widget, func):

        ref = weakref.ref(widget)

        def update(_=None):
            obj = ref()
            if obj is None:
                return

            try:
                obj.setText(func())
            except Exception:
                logger.exception("[Translator] erro auto")

        update()
        cls._register(lambda _: update(), ref)

    # ==================================================
    # GET
    # ==================================================
    @classmethod
    def get(cls, chave):
        return cls._translate(chave, cls.current())

    @classmethod
    def get_all(cls):
        return cls._translate("Todos", cls.current())
