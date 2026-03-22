from PyQt5.QtCore import QThread, pyqtSignal


class ImportWorker(QThread):

    progress = pyqtSignal(int, str)   # percentual, mensagem
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, service, caminho, id_usuario, id_conta):
        super().__init__()
        self.service = service
        self.caminho = caminho
        self.id_usuario = id_usuario
        self.id_conta = id_conta

    # ------------------------------------------
    # Callback interno para progresso
    # ------------------------------------------
    def _emit_progress(self, percentual, mensagem=""):
        self.progress.emit(percentual, mensagem)

    # ------------------------------------------
    # Execução da thread
    # ------------------------------------------
    def run(self):
        try:
            self._emit_progress(10, "Lendo arquivo...")

            dados = self.service.importar(
                self.caminho,
                self.id_usuario,
                self.id_conta,
                progress_callback=self._emit_progress  # 🔥 correto
            )

            self._emit_progress(100, "Finalizado.")

            self.finished.emit(dados)

        except Exception as e:
            self.error.emit(str(e))