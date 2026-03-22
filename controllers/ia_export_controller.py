# controllers/ia_export_controller.py

from services.ia_export_service import IAExportService


class IAExportController:
    def __init__(self):
        self.service = IAExportService()

    def exportar_extrato_conta(
        self,
        transacoes,
        conta,
        data_inicio,
        data_fim,
        formato,
        caminho
    ):
        return self.service.exportar_extrato_conta(
            transacoes,
            conta,
            data_inicio,
            data_fim,
            formato,
            caminho
        )
