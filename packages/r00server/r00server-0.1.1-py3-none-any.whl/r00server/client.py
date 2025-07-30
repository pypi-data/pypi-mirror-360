import random
import time
from typing import List

import niquests
from pathlib import Path
from r00logger import log
from r00secret import secret
from platformdirs import user_cache_dir

class ServerUploadError(Exception):
    """Исключение, выбрасываемое, когда папка не найдена."""

    def __init__(self, message: str):
        super().__init__(message)


class ServerDownloadError(Exception):
    """Исключение, выбрасываемое, когда папка не найдена."""

    def __init__(self, message: str):
        super().__init__(message)


class FileServer:
    def __init__(self):
        self.server_url = secret.fileserver.host
        self.cache_dir = Path(user_cache_dir())
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = niquests.Session(
            pool_maxsize=1000, multiplexed=True, keepalive_delay=60
        )  # Используем один клиент для всех запросов
        self.client.headers.update({'Connection': 'keep-alive'})

    def exist_file(self, remote_path: str) -> bool:
        """
        Проверяет существование файла на сервере с помощью HEAD-запроса.

        :param remote_path: Удалённый путь к файлу, например "configs/1.txt".
                            Не должен заканчиваться на '/'.
        :return: True, если файл существует, иначе False.
        """
        # Проверяем, что путь не пустой и не указывает на директорию
        if not remote_path or remote_path.endswith('/'):
            return False

        url = f"{self.server_url}/file/{remote_path}"
        try:
            response = self.client.head(url, timeout=10)
            # 200 OK означает, что файл найден
            if response.status_code == 200:
                return True
            # 404 Not Found означает, что файла нет
            elif response.status_code == 404:
                return False
            # В других случаях (ошибка сервера и т.д.) считаем, что файла нет
            else:
                log.warning(
                    f"Получен неожиданный статус {response.status_code} "
                    f"при проверке существования файла: {remote_path}"
                )
                return False
        except niquests.exceptions.RequestException as e:
            # В случае сетевых ошибок или таймаута также считаем, что файла нет
            log.error(f"Ошибка сети при проверке файла {remote_path}: {e}")
            return False

    def list(self, remote_folder: str, recursive: bool = True) -> List[str]:
        """
        Получает список файлов в удаленной папке.
        :param remote_folder: Удаленный путь к папке, например "configs/".
        :param recursive: Если True, рекурсивно собирает файлы из поддиректорий.
        :return: Список файлов, например ["configs/1.txt", "configs/2.txt", "configs/backup/1.txt"].
        """
        # Убираем ведущие и конечные слэши
        folder = remote_folder.strip("/")
        url = f"{self.server_url}/list/{folder}"
        response = self.client.get(url)
        if not response.ok:
            raise Exception(f"Ошибка получения списка файлов для '{remote_folder}': {response.status_code}")
        data = response.json()
        # data должен содержать ключи: "folder", "files", "directories"
        # Формируем список файлов с полным путем относительно корня сервера
        files = [f"{folder}/{f}" for f in data.get("files", [])]

        if recursive:
            for d in data.get("directories", []):
                subfolder = f"{folder}/{d}"
                try:
                    subfiles = self.list(subfolder, recursive=True)
                    files.extend(subfiles)
                except Exception as e:
                    log.error(f"Ошибка при получении списка для поддиректории '{subfolder}': {e}")
        return files

    def _download_dir(self, remote_dir: Path) -> Path:
        """
        Скачивает все файлы из удаленной директории и сохраняет их в локальной папке, сохраняя структуру.
        :param remote_dir: Удаленная папка, которую нужно скачать.
        :return: Локальная директория, в которую были скачаны файлы.
        """
        # Получаем список файлов и поддиректорий в удаленной папке
        remote_files = self.list(str(remote_dir), recursive=True)
        for server_path in remote_files:
            filepath = self.download(server_path)
        return filepath.parent

    def download(self, remote_path: str, local_path=None, force=True, retries: int = 3) -> Path:
        """
        Скачивание файла с сервера.
        :param remote_path: Удалённый путь configs/1.txt. Скачать папку: указать на конце "/" (тип str)
        :param local_path: Локальный путь, куда будет сохранён файл.
        :param force: Принудительно перекачать файл, даже если он есть на клиенте
        :param retries: Колличество попыток скачивания, если завершилось с ошибкой
        :return:
        """
        full_remote_path = f"{self.server_url}/file/{remote_path}"
        if full_remote_path.endswith('/'):
            folder_dir = self._download_dir(Path(remote_path))
            return folder_dir

        remote_path = Path(remote_path)
        local_path = self.cache_dir / remote_path if not local_path else Path(local_path)

        if local_path.exists() and not force:
            return local_path

        for i in range(retries):
            # Скачивание файла
            log.trace(f'💻 Download file: {remote_path}')
            file_response = self.client.get(full_remote_path)
            if not file_response.ok:
                raise FileNotFoundError(f"Failed to download {remote_path}")

            # Получаем размер файла из заголовка Content-Length
            content_length = file_response.headers.get("Content-Length")
            if content_length is None:
                raise ServerDownloadError(f"Сервер не предоставил размер файла для {remote_path}")

            expected_size = int(content_length)

            # Сохраняем файл в локальное хранилище
            local_path.parent.mkdir(parents=True, exist_ok=True)
            total_bytes = 0
            with open(local_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:  # Фильтруем keep-alive chunks
                        f.write(chunk)
                        total_bytes += len(chunk)

            # Проверяем размер скачанного файла
            if total_bytes != expected_size:
                local_path.unlink(missing_ok=True)  # Удаляем файл, если размер не совпал
                sleep_time = self._get_sleep(retries)
                log.warning(f"💻 Не смог скачать файл с серрвера: {remote_path}\n"
                            f"Размер скачанного файла не совпадает: {total_bytes} != {expected_size}\n"
                            f"Повторная попытка через {sleep_time:.2f} сек...")
                time.sleep(sleep_time)
                continue

            return local_path
        else:
            raise ServerDownloadError(f"Не смог скачать файл с сервера: {full_remote_path}")

    def _upload_dir(self, local_dir: Path, remote_dir: Path):
        local_dir = local_dir.expanduser()
        for file in local_dir.rglob("*"):
            if file.is_file():
                # Вычисляем относительный путь файла от корня local_dir
                rel_path = file.relative_to(local_dir)
                # Формируем удалённый путь, объединяя remote_dir и относительный путь
                remote_file = remote_dir / rel_path
                self.upload(str(file), str(remote_file))


    def upload(
            self,
            local_path: str,
            remote_path: str,
            retries: int = 3
    ) -> bool:
        """
        Синхронно загружает файл на сервер с проверкой целостности.
        Использует постоянное соединение и экспоненциальный backoff с jitter.
        """
        if str(local_path).endswith('/'):
            self._upload_dir(Path(local_path), Path(remote_path))
            return True

        file = Path(local_path)
        if not file.exists():
            raise FileNotFoundError(f"Локальный файл {file} не найден")

        file_size = file.stat().st_size
        metadata = {"path": remote_path, "size": str(file_size)}

        for attempt in range(1, retries + 1):
            try:
                with file.open("rb") as f:
                    response = self.client.post(
                        url=f"{self.server_url}/upload",
                        data=metadata,
                        files={"file": (remote_path, f)},
                        timeout=30 + file_size // (1024 * 100)  # Адаптивный таймаут
                    )

                if self._validate_response(response, file_size):
                    log.trace(f'💻 Upload file: {remote_path}')
                    return True

            except IOError as e:
                self._log_error("💻 I/O Error", remote_path, attempt, e)
                raise  # Критическая ошибка, прерываем попытки
            except Exception as e:
                self._log_error("💻 неожиданная ошибка", remote_path, attempt, e)

            # Повторяем попытку закачки файла
            sleep_time = self._get_sleep(retries)
            log.debug(f"💻 Не смог закачать файл на серрвер: {remote_path}\n"
                      f"Запущен ли uviicorn на сервере?\n"
                      f"Повторная попытка через {sleep_time:.2f} сек...")
            time.sleep(sleep_time)

        raise ServerUploadError(f"Не удалось загрузить {file} после {retries} попыток")

    def _validate_response(self, response, expected_size: int) -> bool:
        if response.status_code == 200:
            if response.json().get("size") == expected_size:
                return True
            log.warning("💻 Несоответствие размера файла на сервере")
        return False

    def _log_error(self, error_type: str, path: str, attempt: int, exception: Exception):
        log.error(
            f"[{error_type.upper()}] Ошибка при загрузке {path} "
            f"(попытка {attempt}): {str(exception)}"
        )

    def _get_sleep(self, attempt):
        return (1 + attempt) + random.uniform(0, 1)


serv = FileServer()
