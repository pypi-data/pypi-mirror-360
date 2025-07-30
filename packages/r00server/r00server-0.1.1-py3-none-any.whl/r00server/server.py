import hashlib
import os
import shutil
from functools import lru_cache
from pathlib import Path

import aiofiles
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse

app = FastAPI()
SERVER_DIR = Path("/media/hdd1/server/storage/")


def is_safe_path(path: Path) -> bool:
    """Проверяет, что путь после объединения с SERVER_DIR остается внутри SERVER_DIR."""
    try:
        # Пытаемся получить путь относительно базовой директории.
        # Если путь выходит за пределы, этот вызов вызовет ValueError.
        (SERVER_DIR / path).resolve().relative_to(SERVER_DIR.resolve())
        return True
    except ValueError:
        # Путь находится за пределами SERVER_DIR.
        return False

@app.head("/file/{filepath:path}")
@app.get("/file/{filepath:path}")
async def download_or_check_file(filepath: str) -> FileResponse:
    # Убираем ведущий слэш, чтобы Path не считал его абсолютным путем
    safe_filepath = Path(filepath.lstrip('/\\'))

    # Проверяем, что путь не пытается выйти за пределы корневой директории
    if '..' in safe_filepath.parts:
        raise HTTPException(403, "Недопустимый путь (содержит '..')")

    abs_path = SERVER_DIR / safe_filepath

    # Добавлена проверка is_safe_path для дополнительной безопасности
    if not is_safe_path(safe_filepath):
        raise HTTPException(403, "Недопустимый путь")

    # Улучшенная проверка: убеждаемся, что это файл, а не директория
    if not abs_path.is_file():
        raise HTTPException(404, "Файл не найден")

    return FileResponse(abs_path)


@app.post("/upload")
async def upload_file(
        path: str = Form(...),
        size: int = Form(...),
        file: UploadFile = File(...)
):
    abs_path = (SERVER_DIR / path.lstrip('/')).resolve()
    if not is_safe_path(abs_path):
        raise HTTPException(403, "Недопустимый путь")

    # Создаем директорию на сервере, если её нет
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = abs_path.with_suffix(".tmp")
    chunk_size = 16 * 1024  # 16 КБ

    try:
        total_bytes = 0
        async with aiofiles.open(temp_path, 'wb') as out_file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                await out_file.write(chunk)
                total_bytes += len(chunk)

        # Проверка размера загруженного файла
        if total_bytes != size:
            await aiofiles.os.remove(temp_path)
            raise HTTPException(400, f"Размер файла не совпадает: {total_bytes} != {size}")

        # Перемещаем временный файл в итоговое место
        shutil.move(temp_path, abs_path)
        return {"status": "success", "size": total_bytes}

    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Ошибка при сохранении файла: {str(e)}")


@app.get("/list/{folder:path}")
async def list_files(folder: str):
    """
    Возвращает список файлов и поддиректорий в указанной папке.
    Пример: GET /list/samsung/backup/s8/efs
    """
    abs_path = (SERVER_DIR / folder.lstrip('/')).resolve()
    if not is_safe_path(abs_path):
        raise HTTPException(403, "Недопустимый путь")
    if not abs_path.exists() or not abs_path.is_dir():
        raise HTTPException(404, "Папка не найдена")
    # Составляем список файлов и директорий
    files = [item.name for item in abs_path.iterdir() if item.is_file()]
    directories = [item.name for item in abs_path.iterdir() if item.is_dir()]
    return {"folder": folder, "files": files, "directories": directories}