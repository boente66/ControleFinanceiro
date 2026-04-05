import threading
import logging

import argostranslate.package
import argostranslate.translate

logger = logging.getLogger(__name__)


class ArgosService:

    _cache = {}
    _installed_pairs = set()
    _lock = threading.Lock()

    MAX_CACHE = 5000

    # ==================================================
    # CONFIG
    # ==================================================
    DEFAULT_SOURCE = "pt"
    DEFAULT_TARGET = "en"

    # ==================================================
    # DETECTAR SE MODELO EXISTE (CORRIGIDO)
    # ==================================================
    @classmethod
    def _is_installed(cls, origem, destino):
        try:
            installed = argostranslate.translate.get_installed_languages()

            for lang in installed:
                if lang.code == origem:

                    # 🔥 compatibilidade com versões diferentes
                    translations = getattr(lang, "translations_to", None)

                    if translations is None:
                        translations = getattr(lang, "translations", [])

                    for t in translations:
                        try:
                            if t.to_lang.code == destino:
                                return True
                        except Exception:
                            continue

            return False

        except Exception:
            logger.exception("[Argos] Erro ao verificar instalação")
            return False

    # ==================================================
    # INSTALAR MODELO
    # ==================================================
    @classmethod
    def ensure_model(cls, origem, destino, background=False):

        key = (origem, destino)

        if key in cls._installed_pairs:
            return True

        if cls._is_installed(origem, destino):
            cls._installed_pairs.add(key)
            return True

        if background:
            threading.Thread(
                target=cls._install_model,
                args=(origem, destino),
                daemon=True
            ).start()
            return False

        return cls._install_model(origem, destino)

    @classmethod
    def _install_model(cls, origem, destino):

        with cls._lock:
            try:
                logger.info(f"[Argos] Instalando modelo {origem}->{destino}")

                argostranslate.package.update_package_index()
                packages = argostranslate.package.get_available_packages()

                pkg = next(
                    (p for p in packages
                     if p.from_code == origem and p.to_code == destino),
                    None
                )

                if not pkg:
                    logger.warning(f"[Argos] Modelo não encontrado {origem}->{destino}")
                    return False

                path = pkg.download()
                argostranslate.package.install_from_path(path)

                cls._installed_pairs.add((origem, destino))

                logger.info(f"[Argos] Modelo instalado {origem}->{destino}")
                return True

            except Exception:
                logger.exception("[Argos] Erro ao instalar modelo")
                return False

    # ==================================================
    # TRADUÇÃO PRINCIPAL (NÃO BLOQUEIA)
    # ==================================================
    @classmethod
    def traduzir(cls, texto, origem=None, destino=None):

        if not texto:
            return texto

        origem = origem or cls.DEFAULT_SOURCE
        destino = destino or cls.DEFAULT_TARGET

        key = (texto, origem, destino)

        # CACHE
        if key in cls._cache:
            return cls._cache[key]

        try:
            # 🔥 não bloqueia UI
            if not cls._is_installed(origem, destino):
                cls.ensure_model(origem, destino, background=True)
                return texto

            resultado = argostranslate.translate.translate(
                texto, origem, destino
            )

            # 🔥 controle de cache
            if len(cls._cache) >= cls.MAX_CACHE:
                cls._cache.clear()

            cls._cache[key] = resultado

            return resultado

        except Exception:
            logger.exception("[Argos] Falha na tradução")
            return texto

    # ==================================================
    # TRADUÇÃO ASSÍNCRONA
    # ==================================================
    @classmethod
    def traduzir_async(cls, texto, callback, origem=None, destino=None):

        def worker():
            resultado = cls.traduzir(texto, origem, destino)
            try:
                callback(resultado)
            except Exception:
                logger.exception("[Argos] Erro no callback async")

        threading.Thread(target=worker, daemon=True).start()

    # ==================================================
    # PRÉ-CARREGAMENTO
    # ==================================================
    @classmethod
    def preload(cls, pares=None):

        pares = pares or [("pt", "en")]

        for origem, destino in pares:
            cls.ensure_model(origem, destino, background=True)

    # ==================================================
    # LIMPAR CACHE
    # ==================================================
    @classmethod
    def clear_cache(cls):
        cls._cache.clear()
        logger.info("[Argos] Cache limpo")

    # ==================================================
    # LISTAR IDIOMAS INSTALADOS
    # ==================================================
    @classmethod
    def listar_idiomas_instalados(cls):
        try:
            langs = argostranslate.translate.get_installed_languages()
            return [lang.code for lang in langs]
        except Exception:
            logger.exception("[Argos] Erro ao listar idiomas")
            return []

    # ==================================================
    # VERIFICAR STATUS DO PAR
    # ==================================================
    @classmethod
    def is_ready(cls, origem=None, destino=None):
        origem = origem or cls.DEFAULT_SOURCE
        destino = destino or cls.DEFAULT_TARGET
        return cls._is_installed(origem, destino)