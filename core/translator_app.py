import weakref
import logging
from functools import lru_cache

from core.session import Session
from core.i18n import t

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
        cls._translate_cached.cache_clear()  # 🔥 limpa cache
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
    # REFRESH GLOBAL (CORRIGIDO)
    # ==================================================
    @classmethod
    def refresh(cls):

        if cls._lock_refresh:
            return

        cls._lock_refresh = True

        try:
            idioma = cls.current()
            novos = []

            for callback, ref in list(cls._callbacks):

                obj = ref()
                if obj is None:
                    continue

                try:
                    callback(idioma)
                    novos.append((callback, ref))
                except Exception:
                    logger.exception("[Translator] erro refresh")

            cls._callbacks = novos

        finally:
            cls._lock_refresh = False

    # ==================================================
    # REGISTRO SEGURO
    # ==================================================
    @classmethod
    def bind(cls, callback, widget=None):

        ref = weakref.ref(widget) if widget else weakref.ref(callback)

        cls._callbacks.append((callback, ref))

        # 🔥 NÃO usa mais Session.on_idioma_change (evita duplicação)

    # ==================================================
    # AUTO TRANSLATE TREE (OTIMIZADO)
    # ==================================================
    @classmethod
    def auto_translate_tree(cls, root):

        idioma = cls.current()

        for widget in root.findChildren(object):

            try:
                # TEXT
                if hasattr(widget, "setText") and hasattr(widget, "text"):

                    base = getattr(widget, "_original_text", None)
                    if base is None:
                        base = widget.text()
                        widget._original_text = base

                    if base:
                        widget.setText(cls._translate(base, idioma))

                # PLACEHOLDER
                if hasattr(widget, "setPlaceholderText"):

                    base = getattr(widget, "_original_placeholder", None)
                    if base is None:
                        base = widget.placeholderText()
                        widget._original_placeholder = base

                    if base:
                        widget.setPlaceholderText(cls._translate(base, idioma))

                # TITLE
                if hasattr(widget, "setTitle"):

                    base = getattr(widget, "_original_title", None)
                    if base is None:
                        base = widget.title()
                        widget._original_title = base

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
        cls.bind(update, root)

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
        cls.bind(update, widget)

    # ==================================================
    # HELPERS
    # ==================================================
    @classmethod
    def text(cls, widget, texto):
        widget.setText(cls.get(texto))

    @classmethod
    def group(cls, widget, texto):
        widget.setTitle(cls.get(texto))

    @classmethod
    def placeholder(cls, widget, texto):
        widget.setPlaceholderText(cls.get(texto))

    @classmethod
    def window_title(cls, widget, texto):
        widget.setWindowTitle(cls.get(texto))

    # ==================================================
    # GET
    # ==================================================
    @classmethod
    def get(cls, chave):
        return cls._translate(chave, cls.current())

    @classmethod
    def get_all(cls):
        return cls._translate("Todos", cls.current())

    @classmethod
    def table_headers(cls, table, headers):
        try:
            table.setHorizontalHeaderLabels([
                cls.get(h) for h in headers])
        except Exception:
            logger.exception("[Translator] erro ao traduzir cabeçalhos da tabela")
