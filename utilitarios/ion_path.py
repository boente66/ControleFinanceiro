import os
import os.path
import sys 

class IonPath:
    """Utilitario central de caminho do sistema.
    Compartivel com:
    - Ambiente de desenvolvimento
    - Executável (PyInstaller / auto-py-to-exe)
    """

    @staticmethod
    def get_base_path():
        """Retorna o caminho base do sistema, seja em ambiente de desenvolvimento ou executável."""
        if getattr(sys, 'frozen', False):
            # Se estiver rodando como executável, use o caminho do diretório do executável
            return os.path.dirname(sys.executable)
        else:
            # Se estiver rodando em ambiente de desenvolvimento, use o caminho do script atual
            return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def resource(*paths) -> str:
        """Retorna o caminho absoluto para um recurso, dado um caminho relativo."""
      
        return os.path.join(IonPath.get_base_path(), *paths)

    @staticmethod
    def user_dir() -> str:
        """Pasta padrão do sistema do usuario."""
        path = os.path.join(os.path.expanduser("~"), "ControleFinanceiro")
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    
    @staticmethod
    def backup_file(nome: str) -> str:
        """Retorna o caminho do arquivo de backup."""
        user_dir = IonPath.user_dir()
        backup_dir = os.path.join(user_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return os.path.join(backup_dir, nome)
    
    @staticmethod
    def log_file() -> str:
        return os.path.join(IonPath.user_dir(), "app.log")
    
    @staticmethod
    def ensure_dir(path: str):
        """Garante que o diretório existe."""
        if not os.path.exists(path):
            os.makedirs(path)