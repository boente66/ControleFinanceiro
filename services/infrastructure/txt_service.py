# infrastructure/txt_service.py

class TxtService:

    def ler(self, caminho_txt: str):
        if not caminho_txt:
            raise ValueError("Arquivo TXT não informado.")

        with open(caminho_txt, "r", encoding="utf-8") as f:
            return f.read()