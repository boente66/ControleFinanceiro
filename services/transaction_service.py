from datetime import datetime
import logging

from models.transaction_model import TransactionModel
from models.account_model import AccountModel

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Regras de negócio de transações financeiras.
    """

    def __init__(self):
        self.transaction_model = TransactionModel()
        self.account_model = AccountModel()

    # ============================================================
    # CRIAR TRANSAÇÃO (MANUAL)
    # ============================================================
    def criar_transacao(self, dados: dict):

        id_usuario = dados.get("ID_Usuario")
        id_conta = dados.get("ID_Conta")

        if not id_usuario or not id_conta:
            raise ValueError("ID_Usuario e ID_Conta são obrigatórios.")

        conta = self.account_model.get_account_by_id(id_conta, id_usuario)

        if not conta:
            raise PermissionError("Conta não pertence ao usuário.")

        valor = float(dados["Valor"])

        # Regra aplicada apenas manualmente
        if valor < 0 and conta["Saldo_Atual"] < abs(valor):
            raise ValueError("Saldo insuficiente.")

        self.transaction_model.add_transaction(dados)
        self.account_model.update_saldo(id_conta, valor, id_usuario)

        return True

    # ============================================================
    # CRIAR TRANSAÇÃO IMPORTADA (SEM VALIDAR SALDO)
    # ============================================================
    def criar_transacao_importada(self, dados: dict):

        id_usuario = dados.get("ID_Usuario")
        id_conta = dados.get("ID_Conta")

        if not id_usuario or not id_conta:
            raise ValueError("ID_Usuario e ID_Conta são obrigatórios.")

        conta = self.account_model.get_account_by_id(id_conta, id_usuario)

        if not conta:
            raise PermissionError("Conta não pertence ao usuário.")

        valor = float(dados["Valor"])

        # ❌ Não valida saldo aqui

        self.transaction_model.add_transaction(dados)
        self.account_model.update_saldo(id_conta, valor, id_usuario)

        return True

    # ============================================================
    # IMPORTAÇÃO EM LOTE
    # ============================================================
    def salvar_lote_importado(self, lista_transacoes: list, id_usuario: int):

        if not lista_transacoes:
            return 0

        total_importadas = 0

        for item in lista_transacoes:
            try:

                valor = float(item.get("Valor", 0))

                tipo = item.get("Tipo")
                if not tipo:
                    tipo = "Despesa" if valor < 0 else "Receita"

                dados = {
                    "ID_Conta": item.get("ID_Conta"),
                    "Descricao": item.get("Descricao"),
                    "Valor": valor,
                    "Data": item.get("Data"),
                    "Tipo": tipo,
                    "ID_Usuario": id_usuario,
                    "ID_Categoria": item.get("ID_Categoria"),
                    "ID_Favorecido": item.get("ID_Favorecido"),
                }

                if not dados["ID_Conta"] or not dados["Data"]:
                    raise ValueError("Dados obrigatórios ausentes.")

                self.criar_transacao_importada(dados)
                total_importadas += 1

            except Exception as e:
                logger.warning(f"Falha ao importar transação: {e}")
                continue

        return total_importadas

    # ============================================================
    # EXCLUIR TRANSAÇÃO
    # ============================================================
    def excluir_transacao(self, id_transacao, id_usuario):

        trans = self.transaction_model.get_transaction_by_id(id_transacao,id_usuario)

        if not trans:
            raise ValueError("Transação não encontrada.")

        if trans["ID_Usuario"] != id_usuario:
            raise PermissionError("Transação não pertence ao usuário.")

        valor = float(trans["Valor"])
        id_conta = trans["ID_Conta"]

        self.account_model.update_saldo(id_conta, -valor, id_usuario)
        self.transaction_model.delete_transaction(id_transacao,id_usuario)

        return True

    # ============================================================
    # ATUALIZAR TRANSAÇÃO
    # ============================================================
    def atualizar_transacao(self, dados: dict):

        id_transacao = dados.get("ID_Transacao")
        id_usuario = dados.get("ID_Usuario")

        trans = self.transaction_model.get_transaction_by_id(id_transacao, id_usuario)

        if not trans:
            raise ValueError("Transação não encontrada.")

        if trans["ID_Usuario"] != id_usuario:
            raise PermissionError("Transação não pertence ao usuário.")

        diferenca = float(dados["Valor"]) - float(trans["Valor"])

        if diferenca != 0:
            self.account_model.update_saldo(
                trans["ID_Conta"],
                diferenca,
                id_usuario
            )

        self.transaction_model.update_transaction(id_transacao, dados)

        return True

    # ============================================================
    # TRANSFERÊNCIA
    # ============================================================
    def transferir(self, id_origem, id_destino, valor, data, id_usuario):

        if id_origem == id_destino:
            raise ValueError("Contas devem ser diferentes.")

        origem = self.account_model.get_account_by_id(id_origem, id_usuario)
        destino = self.account_model.get_account_by_id(id_destino, id_usuario)

        if not origem or not destino:
            raise PermissionError("Conta inválida.")

        if origem["Saldo_Atual"] < valor:
            raise ValueError("Saldo insuficiente.")

        data_str = data if isinstance(data, str) else data.strftime("%Y-%m-%d")

        self.criar_transacao({
            "ID_Conta": id_origem,
            "Descricao": f"Transferência para conta {id_destino}",
            "Valor": -abs(valor),
            "Data": data_str,
            "ID_Usuario": id_usuario
        })

        self.criar_transacao({
            "ID_Conta": id_destino,
            "Descricao": f"Transferência recebida da conta {id_origem}",
            "Valor": abs(valor),
            "Data": data_str,
            "ID_Usuario": id_usuario
        })

        return True

    # ============================================================
    # CONVERTER EM TRANSFERÊNCIA
    # ============================================================
    def converter_em_transferencia(self, id_transacao, id_destino, id_usuario):

        transacao = self.transaction_model.get_transaction_by_id(id_transacao)

        if not transacao:
            raise ValueError("Transação não encontrada.")

        if transacao["ID_Usuario"] != id_usuario:
            raise PermissionError("Transação não pertence ao usuário.")

        id_origem = transacao["ID_Conta"]
        valor = abs(float(transacao["Valor"]))
        data = transacao["Data"]

        conta_origem = self.account_model.get_account_by_id(id_origem, id_usuario)
        conta_destino = self.account_model.get_account_by_id(id_destino, id_usuario)

        if not conta_origem or not conta_destino:
            raise ValueError("Conta inválida.")

        # Estorna saldo original
        self.account_model.update_saldo(
            id_origem,
            -float(transacao["Valor"]),
            id_usuario
        )

        self.transaction_model.delete_transaction(id_transacao)

        self.transferir(id_origem, id_destino, valor, data, id_usuario)

        return True

    # ============================================================
    # CONSULTAS
    # ============================================================
    def get_transactions_by_account_periodo(self, id_usuario, id_conta, periodo):

        conta = self.account_model.get_account_by_id(id_conta, id_usuario)

        if not conta:
            raise PermissionError("Conta inválida.")

        data_inicio, data_fim = periodo

        return self.transaction_model.get_transactions_by_account_periodo(
            id_conta,
            data_inicio,
            data_fim,
            id_usuario
        )

    def get_transaction_by_id(self, id_transacao,id_usuario):
        return self.transaction_model.get_transaction_by_id(id_transacao,id_usuario)

    def get_resumo_financeiro(self, user_id):
        return self.transaction_model.get_resumo_financeiro(user_id)

    def get_analise_mensal(self, user_id):
        return self.transaction_model.get_analise_mensal(user_id)