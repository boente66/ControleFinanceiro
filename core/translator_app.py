from core.session import Session
from core.i18n import t
import weakref


class TranslatorApp:
    """
    Sistema central de tradução reativa da aplicação.
    Substitui uso manual de t() e _retranslate_ui.
    """

    # armazena callbacks sem impedir GC
    _listeners = []

    # ==================================================
    # BASE
    # ==================================================
    @classmethod
    def __bind(cls, widget, callback):
        """
        Registra callback ligado ao ciclo de vida do widget
        """
        ref = weakref.ref(widget)

        def safe_callback(idioma):
            obj = ref()
            if obj is None:
                return  # widget já destruído

            try:
                callback(obj, idioma)
            except RuntimeError:
                # PyQt: objeto deletado
                return

        # executa imediatamente
        idioma = Session.get_config("idioma", "Português")
        safe_callback(idioma)

        # registra listener global
        cls._listeners.append(safe_callback)

        # conecta ao evento global
        Session.on_idioma_change(safe_callback)

    # ==================================================
    # LABEL / BOTÃO
    # ==================================================
    @classmethod
    def text(cls, widget, chave):
        if not hasattr(widget, "setText"):
            return
        cls.__bind(widget, lambda w, idioma: w.setText(t(chave, idioma)))

    # ==================================================
    # PLACEHOLDER (QLineEdit)
    # ==================================================
    @classmethod
    def placeholder(cls, widget, chave):
        cls.__bind(widget, lambda w, idioma: w.setPlaceholderText(t(chave, idioma)))

    # ==================================================
    # TOOLTIP
    # ==================================================
    @classmethod
    def tooltip(cls, widget, chave):
        cls.__bind(widget, lambda w, idioma: w.setToolTip(t(chave, idioma)))

    # ==================================================
    # GROUPBOX
    # ==================================================
    @classmethod
    def group(cls, widget, chave):
        cls.__bind(widget, lambda w, idioma: w.setTitle(t(chave, idioma)))

    # ==================================================
    # COMBOBOX (lista fixa)
    # ==================================================
    @classmethod
    def combo(cls, combo, chaves):
        cls.__bind(combo, cls._update_combo(chaves))

    @staticmethod
    def _update_combo(chaves):
        def update(combo, idioma):
            try:
                valor_atual = combo.currentData() or combo.currentText()

                combo.blockSignals(True)
                combo.clear()

                for chave in chaves:
                    combo.addItem(t(chave, idioma), chave)

                # restaura seleção
                index = combo.findData(valor_atual)
                if index >= 0:
                    combo.setCurrentIndex(index)

                combo.blockSignals(False)

            except RuntimeError:
                pass

        return update

    # ==================================================
    # TABELA HEADER
    # ==================================================
    @classmethod
    def table_headers(cls, table, chaves):
        cls.__bind(
            table,
            lambda w, idioma: w.setHorizontalHeaderLabels(
                [t(c, idioma) for c in chaves]
            ),
        )

    # ==================================================
    # TEXTO DIRETO (quando não é widget)
    # ==================================================
    @staticmethod
    def get(chave):
        idioma = Session.get_config("idioma", "Português")
        return t(chave, idioma)

    # ==================================================
    # FORÇAR UPDATE GLOBAL (caso precise)
    # ==================================================
    @classmethod
    def refresh(cls):
        idioma = Session.get_config("idioma", "Português")

        for callback in list(cls._listeners):
            try:
                callback(idioma)
            except Exception:
                continue

        def update_widgets(idioma):
            for widget in cls._widgets:
                widget.update(idioma)

        cls._listeners.append(update_widgets)

    @classmethod
    def window_title(cls, window, chave):
        cls.__bind(window, lambda w, idioma: w.setWindowTitle(t(chave, idioma)))
