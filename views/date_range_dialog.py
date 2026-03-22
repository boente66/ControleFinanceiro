from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt


class DateRangeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Selecionar intervalo de datas")
        self.setMinimumWidth(600)

        # --------------------------
        # Layout principal
        # --------------------------
        layout = QVBoxLayout(self)

        title = QLabel("Selecione a Data Inicial e Final")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # --------------------------
        # Calendários
        # --------------------------
        cal_layout = QHBoxLayout()

        self.calendar_start = QCalendarWidget()
        self.calendar_start.setGridVisible(True)

        self.calendar_end = QCalendarWidget()
        self.calendar_end.setGridVisible(True)

        cal_layout.addWidget(self.calendar_start)
        cal_layout.addWidget(self.calendar_end)

        layout.addLayout(cal_layout)

        # --------------------------
        # Botões
        # --------------------------
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_ok = QPushButton("Confirmar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_ok.clicked.connect(self.confirmar)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

        # Resultado
        self.data_inicial = None
        self.data_final = None

    # ============================================
    # Validação e retorno
    # ============================================
    def confirmar(self):
        data_ini = self.calendar_start.selectedDate()
        data_fim = self.calendar_end.selectedDate()

        if data_ini > data_fim:
            QMessageBox.warning(
                self,
                "Intervalo inválido",
                "A data inicial não pode ser maior que a data final."
            )
            return

        self.data_inicial = data_ini.toString("yyyy-MM-dd")
        self.data_final = data_fim.toString("yyyy-MM-dd")

        self.accept()

    # ============================================
    # Método para obter o resultado no Controller
    # ============================================
    def get_date_range(self):
        return self.data_inicial, self.data_final