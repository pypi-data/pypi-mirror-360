from pathlib import Path
from typing import Dict, Optional

from dotenv import dotenv_values

from r00adb import adb
from r00pykit import time_it
from r00logger import log
from r00system import run


def get_env_by_filename(filename: str) -> Optional[Dict[str, str]]:
    """
    Ищет env-файл по имени в директории вызывающего скрипта и во всех
    родительских каталогах.
    """
    for filepath in find_project_root(__file__).glob('**/*.env'):
        if filepath.name == filename:
            return dotenv_values(dotenv_path=filepath)
    return None


def find_project_root(current_path: Path | str, root_dir_name: str = 'r00flash') -> Path | None:
    """
    Ищет корневую директорию проекта, двигаясь вверх от указанного пути.

    Args:
        current_path: Начальный путь (например, __file__).
        root_dir_name: Имя корневой директории проекта.

    Returns:
        Путь к корневой директории или None, если не найдено.
    """
    path = Path(current_path).resolve()  # Получаем абсолютный путь
    for parent in path.parents:
        if parent.name == root_dir_name:
            return parent
    # Проверяем и сам текущий путь, если он является директорией
    if path.is_dir() and path.name == root_dir_name:
        return path
    return None


def get_stock_files(dir_stock: Path) -> dict:
    if not dir_stock.is_dir():
        raise ValueError(f"Указанный путь '{dir_stock}' не является директорией.")

    found_files = {}
    search_patterns = {
        "AP": "AP_*.tar.md5",
        "BL": "BL_*.tar.md5",
        "CP": "CP_*.tar.md5",
        "CSC": "CSC_*.tar.md5",
    }

    # Поиск каждого типа файла
    for file_type, pattern in search_patterns.items():
        matches = list(dir_stock.glob(pattern))

        if not matches:
            log.error(f"Не найден необходимый файл для {file_type} по паттерну '{pattern}' в директории '{dir_stock}'")
            raise FileNotFoundError(f"Не найден файл {file_type} (паттерн: '{pattern}') в '{dir_stock}'")
        elif len(matches) > 1:
            log.warning(
                f"Найдено несколько файлов для {file_type} по паттерну '{pattern}': {matches}")
            raise ValueError(f"Найдено несколько подходящих файлов для {file_type} (паттерн: '{pattern}')")
        else:
            log.debug(f"Найден файл для {file_type}: {Path(matches[0]).name}")
            found_files[file_type] = matches[0]

    # Убедимся, что все 4 файла были найдены
    if len(found_files) != len(search_patterns):
        missing_types = [ftype for ftype in search_patterns if ftype not in found_files]
        log.critical(f"Не удалось найти все необходимые типы файлов. Отсутствуют: {missing_types}")
        raise FileNotFoundError(f"Не удалось найти все необходимые файлы прошивки. Отсутствуют: {missing_types}")

    log.info("Все необходимые файлы прошивки успешно найдены.")
    return found_files


@time_it
def push_firmware_on_device(firmware_zip: str | Path = None, device_path='/sdcard/firmware.zip'):
    log.info("Пушим прошивку...")
    adb.push(str(firmware_zip), '/sdcard/firmware.zip', timeout=1500)
    return device_path


def is_download_mode():
    output = run('lsusb', verbose=False, disable_log=True).output
    if not '(Download mode)' in output:
        adb.reboot(download_mode=True)
