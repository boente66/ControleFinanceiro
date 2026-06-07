class XlsxService:

    def ler(self, caminho_xlsx: str):

        if not caminho_xlsx:
            raise ValueError("Arquivo XLSX não informado.")

        try:
            import pandas as pd

        except ImportError as exc:
            raise RuntimeError(
                "Dependência 'pandas' ausente. "
                "Instale o ambiente completo para importar XLSX."
            ) from exc

        try:
            df = pd.read_excel(caminho_xlsx)

            # remove linhas totalmente vazias
            df = df.dropna(how="all")

            # converte NaN para ""
            df = df.fillna("")

            return df.to_dict(orient="records")

        except Exception as e:
            raise RuntimeError(
                f"Erro ao ler XLSX: {e}"
            ) from e