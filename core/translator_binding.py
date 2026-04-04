import weakref
import logging

from core.session import Session
from core.translator_app import TranslatorApp

logger = logging.getLogger(__name__)


class TranslatorBinding:

    @staticmethod
    def bind(widget, chave, setter):

        if not callable(setter):
            logger.warning("[Binding] setter inválido")
            return

        ref = weakref.ref(widget)

        def update(_):
            obj = ref()
            if obj is None:
                return

            try:
                texto = TranslatorApp.get(chave)
                setter(obj, texto)
            except Exception:
                logger.exception("[Binding] erro")

        update(None)
        Session.on_idioma_change(update)