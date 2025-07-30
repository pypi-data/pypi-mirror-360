from pathlib import Path
from .client import serv

def is_server_path(path: str) -> Path:
    """Проверяет, является ли путь серверным и возвращает локальный путь."""
    path = str(path)
    if path.startswith('server://'):
        filepath_server = path.replace('server://', '')
        return serv.download(filepath_server)
    return Path(path).resolve()