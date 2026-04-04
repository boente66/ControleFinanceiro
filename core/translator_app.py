from core.session import Session
from core.i18n import t
import weakref
import logging

logger = logging.getLogger(__name__)


class TranslatorApp:

    _registry = []
    _bound_widgets = weakref.WeakSet()

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
    # 🔥 TRADUÇÃO CENTRAL (INTEGRADA)
    # ==================================================
    @classmethod
    def _translate(cls, texto, idioma):

        # 1️⃣ tenta tradução local
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

    # ==================================================
    # MAPEAR IDIOMA
    # ==================================================
    @staticmethod
    def _map_language(idioma):
        mapa = {
            "Português": "pt",
            "Inglês": "en",
            "Espanhol": "es"
        }
        return mapa.get(idioma, "en")

    # ==================================================
    # REFRESH GLOBAL
    # ==================================================
    @classmethod
    def refresh(cls):
        for callback in list(cls._registry):
            try:
                callback(cls.current())
            except Exception:
                logger.exception("[Translator] erro no refresh")

    # ==================================================
    # REGISTRO AUTOMÁTICO
    # ==================================================
    @classmethod
    def _auto_bind(cls, widget, updater):

        if widget not in cls._bound_widgets:
            cls._bound_widgets.add(widget)

        ref = weakref.ref(widget)

        def callback(idioma):
            obj = ref()
            if obj is None:
                return

            try:
                updater(obj, idioma)
            except RuntimeError:
                pass
            except Exception:
                logger.exception("[Translator] erro ao atualizar widget")

        callback(cls.current())

        cls._registry.append(callback)
        Session.on_idioma_change(callback)

    # ==================================================
    # UI BINDINGS (AGORA USANDO _translate)
    # ==================================================
    @classmethod
    def text(cls, widget, chave):
        cls._auto_bind(widget, lambda w, i: w.setText(cls._translate(chave, i)))

    @classmethod
    def group(cls, widget, chave):
        cls._auto_bind(widget, lambda w, i: w.setTitle(cls._translate(chave, i)))

    @classmethod
    def window_title(cls, widget, chave):
        cls._auto_bind(widget, lambda w, i: w.setWindowTitle(cls._translate(chave, i)))

    @classmethod
    def placeholder(cls, widget, chave):
        cls._auto_bind(widget, lambda w, i: w.setPlaceholderText(cls._translate(chave, i)))

    @classmethod
    def tooltip(cls, widget, chave):
        cls._auto_bind(widget, lambda w, i: w.setToolTip(cls._translate(chave, i)))

    @classmethod
    def combo(cls, combo, chaves):

        def update(c, idioma):
            try:
                valor = c.currentData() or c.currentText()

                c.blockSignals(True)
                c.clear()

                for chave in chaves:
                    c.addItem(cls._translate(chave, idioma), chave)

                index = c.findData(valor)
                if index >= 0:
                    c.setCurrentIndex(index)

                c.blockSignals(False)

            except Exception:
                logger.exception("[Translator] erro combo")

        cls._auto_bind(combo, update)

    @classmethod
    def table_headers(cls, table, chaves):
        cls._auto_bind(
            table,
            lambda w, i: w.setHorizontalHeaderLabels(
                [cls._translate(c, i) for c in chaves]
            )
        )

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
            except RuntimeError:
                pass
            except Exception:
                logger.exception("[Translator] erro auto")

        update()
        Session.on_idioma_change(lambda _: update())

    # ==================================================
    # GET SIMPLES (INTEGRADO)
    # ==================================================
    @classmethod
    def get(cls, chave):
        idioma = cls.current()
        return cls._translate(chave, idioma)


    @classmethod
    def get_all(cls):
        idioma = cls.current()
        return cls._translate("todos", idioma)

    @classmethod
    def bind(cls, widget, *args):
        """
        Two modes:
        - bind(widget, chave, setter)  where setter is a callable (widget, text) or a method name string
        - bind(widget)  infers chave from widget.tr_key or widget.objectName() and picks a sensible setter
        """
        # determine chave and setter
        if len(args) == 0:
            chave = getattr(widget, "tr_key", None)
            if not chave:
                objname = getattr(widget, "objectName", None)
                chave = objname() if callable(objname) else None

            if not chave:
                logger.warning("[Translator] bind: chave não encontrada para widget %r", widget)
                return

            # pick a reasonable default setter
            if hasattr(widget, "setText"):
                setter = lambda w, txt: w.setText(txt)
            elif hasattr(widget, "setPlaceholderText"):
                setter = lambda w, txt: w.setPlaceholderText(txt)
            elif hasattr(widget, "setTitle"):
                setter = lambda w, txt: w.setTitle(txt)
            elif hasattr(widget, "setWindowTitle"):
                setter = lambda w, txt: w.setWindowTitle(txt)
            else:
                logger.warning("[Translator] bind: nenhum setter conhecido para widget %r", widget)
                return

        elif len(args) == 2:
            chave, setter = args
            # if setter is a method name, resolve it to a callable
            if isinstance(setter, str):
                method = getattr(widget, setter, None)
                if callable(method):
                    setter = lambda w, txt, _m=method: _m(txt)
                else:
                    logger.warning("[Translator] bind: método %r não encontrado em %r", setter, widget)
                    return
            elif not callable(setter):
                logger.warning("[Translator] bind: setter inválido para %r", widget)
                return

        else:
            raise TypeError("bind() accepts either (widget) or (widget, chave, setter)")

        # keep a weak reference record of the widget
        try:
            if widget not in cls._bound_widgets:
                cls._bound_widgets.add(widget)
        except Exception:
            pass

        def update(idioma):
            try:
                texto = cls._translate(chave, idioma)
                setter(widget, texto)
            except Exception:
                logger.exception("[Translator] erro bind")

        update(cls.current())
        Session.on_idioma_change(update)
