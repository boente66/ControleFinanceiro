import logging
from datetime import datetime
from models.meta_model import MetaModel
from models.transaction_model import TransactionModel
from database.database import DatabaseError

logger = logging.getLogger(__name__)


class MetaService:

    TIPOS_VALIDOS = ("Categoria", "Economia", "Objetivo")

    def __init__(self):
        self.model = MetaModel()
        self.transaction_model = TransactionModel()

    # --------------------------------------------------
    # CRIAR META
    # --------------------------------------------------
    def criar_meta(self, dados):

        obrigatorios = ["Nome", "Tipo", "Valor_Alvo", "ID_Usuario"]

        for campo in obrigatorios:
            if campo not in dados or not dados[campo]:
                raise ValueError(f"Campo obrigatório ausente: {campo}")

        tipo = dados["Tipo"]

        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("Tipo de meta inválido")

        valor_alvo = float(dados["Valor_Alvo"])
        if valor_alvo <= 0:
            raise ValueError("Valor alvo deve ser maior que zero")

        id_categoria = dados.get("ID_Categoria")

        # Evita duplicidade de meta ativa para mesma categoria
        if tipo == "Categoria" and id_categoria:
            metas = self.model.get_metas_by_categoria(
                id_categoria,
                dados["ID_Usuario"]
            )
            if metas:
                raise ValueError("Já existe meta ativa para essa categoria")

        return self.model.add_meta(
            nome=dados["Nome"].strip(),
            tipo=tipo,
            valor_alvo=valor_alvo,
            id_usuario=dados["ID_Usuario"],
            id_categoria=id_categoria,
            data_inicio=dados.get("Data_Inicio"),
            data_fim=dados.get("Data_Fim")
        )

    # --------------------------------------------------
    # LISTAR COM CÁLCULO
    # --------------------------------------------------
    def listar_metas_com_progresso(self, id_usuario, status="ATIVA"):

        metas = self.model.get_metas_by_status(id_usuario, status)

        metas_calculadas = []

        for meta in metas:
            progresso = self._calcular_progresso(meta, id_usuario)
            meta["Progresso"] = progresso

            # Conclusão automática
            if (
                meta["Status"] == "ATIVA"
                and progresso["percentual"] >= 100
                and meta["Tipo"] != "Categoria"
            ):
                self.model.update_status(meta["ID_Meta"], "CONCLUIDA", id_usuario)
                meta["Status"] = "CONCLUIDA"

            metas_calculadas.append(meta)

        # Ordena por risco
        metas_calculadas.sort(
            key=lambda m: m["Progresso"]["percentual"],
            reverse=True
        )

        return metas_calculadas

    # --------------------------------------------------
    # CÁLCULO CENTRAL
    # --------------------------------------------------
    def _calcular_progresso(self, meta, id_usuario):

        tipo = meta["Tipo"]
        valor_alvo = float(meta["Valor_Alvo"])

        data_inicio = meta.get("Data_Inicio")
        data_fim = meta.get("Data_Fim")

        if tipo == "Categoria":
            total = self.transaction_model.somar_despesas_categoria_periodo(
                meta["ID_Categoria"],
                id_usuario,
                data_inicio,
                data_fim
            )

            percentual = (total / valor_alvo) * 100

            return {
                "valor_atual": total,
                "valor_alvo": valor_alvo,
                "percentual": round(percentual, 2),
                "restante": valor_alvo - total
            }

        if tipo == "Economia":
            total = self.transaction_model.calcular_economia_periodo(
                id_usuario,
                data_inicio,
                data_fim
            )

            percentual = (total / valor_alvo) * 100

            return {
                "valor_atual": total,
                "valor_alvo": valor_alvo,
                "percentual": round(percentual, 2),
                "restante": valor_alvo - total
            }

        if tipo == "Objetivo":
            total = self.transaction_model.somar_receitas_periodo(
                id_usuario,
                data_inicio,
                data_fim
            )

            percentual = (total / valor_alvo) * 100

            return {
                "valor_atual": total,
                "valor_alvo": valor_alvo,
                "percentual": round(percentual, 2),
                "restante": valor_alvo - total
            }

        return {
            "valor_atual": 0,
            "valor_alvo": valor_alvo,
            "percentual": 0,
            "restante": valor_alvo
        }

    # --------------------------------------------------
    # ALTERAR STATUS
    # --------------------------------------------------
    def alterar_status(self, id_meta, novo_status, id_usuario):

        if novo_status not in ("ATIVA", "CONCLUIDA", "CANCELADA"):
            raise ValueError("Status inválido")

        self.model.update_status(id_meta, novo_status, id_usuario)

    # --------------------------------------------------
    # EXCLUIR
    # --------------------------------------------------
    def excluir_meta(self, id_meta, id_usuario):
        self.model.delete_meta(id_meta, id_usuario)