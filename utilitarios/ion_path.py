import os
import sys
import platform
import logging

logger = logging.getLogger(__name__)


class IonPath:
    """
    Gerenciador de caminhos multiplataforma profissional.

    ✔ Windows / Linux / macOS
    ✔ Executável (PyInstaller)
    ✔ Seguro contra falhas de ambiente
    ✔ Cache interno para performance
    """

    APP_NAME = "ControleFinanceiro"

    _cache = {}

    # =====================================================
    # BASE (DEV OU EXECUTÁVEL)
    # =====================================================
    @staticmethod
    def get_base_path() -> str:
        try:
            if getattr(sys, "frozen", False):
                return sys._MEIPASS  # PyInstaller
            return os.path.dirname(os.path.abspath(sys.argv[0]))
        except Exception:
            logger.exception("Erro ao obter base_path")
            return os.getcwd()

    # =====================================================
    # RESOURCE (ASSETS)
    # =====================================================
    @staticmethod
    def resource(*paths) -> str:
        return os.path.join(IonPath.get_base_path(), *paths)

    # =====================================================
    # USER DIR (MULTIPLATAFORMA)
    # =====================================================
    @staticmethod
    def user_dir() -> str:

        if "user_dir" in IonPath._cache:
            return IonPath._cache["user_dir"]

        system = platform.system()

        try:
            if system == "Windows":
                base = os.getenv("APPDATA") or os.path.expanduser("~")

            elif system == "Darwin":
                base = os.path.expanduser("~/Library/Application Support")

            else:
                base = os.getenv("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")

            path = os.path.join(base, IonPath.APP_NAME)

            os.makedirs(path, exist_ok=True)

            IonPath._cache["user_dir"] = path
            return path

        except Exception:
            logger.exception("Erro ao criar user_dir")

            fallback = os.path.join(os.getcwd(), IonPath.APP_NAME)
            os.makedirs(fallback, exist_ok=True)

            IonPath._cache["user_dir"] = fallback
            return fallback

    # =====================================================
    # DATABASE
    # =====================================================
    @staticmethod
    def database() -> str:
        return os.path.join(IonPath.user_dir(), "financeiro.db")

    # =====================================================
    # BACKUP
    # =====================================================
    @staticmethod
    def backup_dir() -> str:

        if "backup_dir" in IonPath._cache:
            return IonPath._cache["backup_dir"]

        path = os.path.join(IonPath.user_dir(), "backup")
        os.makedirs(path, exist_ok=True)

        IonPath._cache["backup_dir"] = path
        return path

    @staticmethod
    def backup_file(nome: str) -> str:
        return os.path.join(IonPath.backup_dir(), nome)

    # =====================================================
    # LOGS
    # =====================================================
    @staticmethod
    def log_dir() -> str:

        if "log_dir" in IonPath._cache:
            return IonPath._cache["log_dir"]

        path = os.path.join(IonPath.user_dir(), "logs")
        os.makedirs(path, exist_ok=True)

        IonPath._cache["log_dir"] = path
        return path

    @staticmethod
    def log_file(nome="app.log") -> str:
        return os.path.join(IonPath.log_dir(), nome)

    # =====================================================
    # CONFIG
    # =====================================================
    @staticmethod
    def config_file() -> str:
        return os.path.join(IonPath.user_dir(), "config.json")

    # =====================================================
    # TEMP (IMPORTANTE PRA IMPORTAÇÃO)
    # =====================================================
    @staticmethod
    def temp_dir() -> str:

        if "temp_dir" in IonPath._cache:
            return IonPath._cache["temp_dir"]

        path = os.path.join(IonPath.user_dir(), "temp")
        os.makedirs(path, exist_ok=True)

        IonPath._cache["temp_dir"] = path
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
        return os.path.join(*paths)