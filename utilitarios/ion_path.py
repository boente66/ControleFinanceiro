import os
import sys
import platform
import logging
from PyQt5 import uic

logger = logging.getLogger(__name__)


class IonPath:
    """
    Gerenciador de caminhos multiplataforma profissional.

    ✔ Windows / Linux / macOS
    ✔ Executável (PyInstaller)
    ✔ Seguro contra falhas de ambiente
    ✔ Cache interno para performance
    ✔ Pronto para produção
    """

    APP_NAME = "ControleFinanceiro"

    _cache = {}

    # =====================================================
    # BASE (DEV OU EXECUTÁVEL)
    # =====================================================
    @classmethod
    def get_base_path(cls) -> str:

        if "base_path" in cls._cache:
            return cls._cache["base_path"]

        try:
            # PyInstaller (onefile / onedir)
            if getattr(sys, "frozen", False):
                base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            else:
                base = os.path.dirname(os.path.abspath(sys.argv[0]))

            base = os.path.normpath(base)

        except Exception:
            logger.exception("Erro ao obter base_path")
            base = os.getcwd()

        cls._cache["base_path"] = base
        return base

    # =====================================================
    # RESOURCE (ASSETS)
    # =====================================================
    @classmethod
    def resource(cls, *paths) -> str:
        return os.path.normpath(os.path.join(cls.get_base_path(), *paths))

    # 🔥 Atalho para assets/icons
    @classmethod
    def icon(cls, nome: str) -> str:
        return cls.resource("assets", "icons", f"{nome}.svg")

    # =====================================================
    # USER DIR (MULTIPLATAFORMA)
    # =====================================================
    @classmethod
    def user_dir(cls) -> str:

        if "user_dir" in cls._cache:
            return cls._cache["user_dir"]

        system = platform.system()

        try:
            if system == "Windows":
                base = os.getenv("APPDATA") or os.path.expanduser("~")

            elif system == "Darwin":
                base = os.path.expanduser("~/Library/Application Support")

            else:
                base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")

            path = os.path.join(base, cls.APP_NAME)
            os.makedirs(path, exist_ok=True)

        except Exception:
            logger.exception("Erro ao criar user_dir")

            path = os.path.join(os.getcwd(), cls.APP_NAME)
            os.makedirs(path, exist_ok=True)

        path = os.path.normpath(path)
        cls._cache["user_dir"] = path
        return path

    # =====================================================
    # DATABASE
    # =====================================================
    @classmethod
    def database(cls) -> str:
        return os.path.join(cls.user_dir(), "financeiro.db")

    # =====================================================
    # BACKUP
    # =====================================================
    @classmethod
    def backup_dir(cls) -> str:

        if "backup_dir" in cls._cache:
            return cls._cache["backup_dir"]

        path = os.path.join(cls.user_dir(), "backup")
        cls.ensure_dir(path)

        cls._cache["backup_dir"] = path
        return path

    @classmethod
    def backup_file(cls, nome: str) -> str:
        return os.path.join(cls.backup_dir(), nome)

    # =====================================================
    # LOGS
    # =====================================================
    @classmethod
    def log_dir(cls) -> str:

        if "log_dir" in cls._cache:
            return cls._cache["log_dir"]

        path = os.path.join(cls.user_dir(), "logs")
        cls.ensure_dir(path)

        cls._cache["log_dir"] = path
        return path

    @classmethod
    def log_file(cls, nome="app.log") -> str:
        return os.path.join(cls.log_dir(), nome)

    # =====================================================
    # CONFIG
    # =====================================================
    @classmethod
    def config_file(cls) -> str:
        return os.path.join(cls.user_dir(), "config.json")

    # =====================================================
    # TEMP (IMPORTANTE PRA IMPORTAÇÃO)
    # =====================================================
    @classmethod
    def temp_dir(cls) -> str:

        if "temp_dir" in cls._cache:
            return cls._cache["temp_dir"]

        path = os.path.join(cls.user_dir(), "temp")
        cls.ensure_dir(path)

        cls._cache["temp_dir"] = path
        return path

    # =====================================================
    # UTIL
    # =====================================================
    @staticmethod
    def ensure_dir(path: str):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            logger.exception(f"Erro ao garantir diretório: {path}")

    @staticmethod
    def join(*paths) -> str:
        return os.path.normpath(os.path.join(*paths))

    # =====================================================
    # DEBUG
    # =====================================================
    @classmethod
    def debug_info(cls) -> dict:
        """
        Retorna informações úteis para debug do ambiente
        """
        return {
            "base_path": cls.get_base_path(),
            "user_dir": cls.user_dir(),
            "database": cls.database(),
            "platform": platform.system(),
            "frozen": getattr(sys, "frozen", False),
        }

    def recourse_paths(*paths) -> list:
        get_base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(get_base_path, *paths)

    @classmethod
    def load_ui(cls,widget,*paths):
        "Carregar UI com caminho seguro + seguro"

        path = cls.recourse_paths(*paths)

        if not os.path.exist(path):
            raise FileNotFoundError(f"UI não encontrado: {path}")

        try:
            uic.loadUi(path, widget)
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar UI:{path} \n {e}")

        return path