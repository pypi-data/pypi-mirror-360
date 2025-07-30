from pathlib import Path

from r00logger import log
from system import run
from .utils import is_download_mode, get_stock_files


class FirmwareManager:
    @staticmethod
    def flash_stock(dir_stock):
        is_download_mode()
        found_files = get_stock_files(dir_stock)
        command = (
            f"odin4 -a \"{found_files["AP"]}\" "
            f"-b \"{found_files["BL"]}\" "
            f"-c \"{found_files["CP"]}\" "
            f"-s \"{found_files["CSC"]}\""
        )

        log.info("Начинаем прошивать телефон на сток...")
        cmdres = run(command, timeout=2000)
        if cmdres.success:
            return True

        log.exception(cmdres)
        raise ValueError("Не смог прошить на stock")

    @staticmethod
    def flash_recovery(path_recovery):
        is_download_mode()
        if not path_recovery.exists():
            raise FileNotFoundError(f"Файл прошивки не найден: {path_recovery}")

        command = f"odin4 -a \"{path_recovery}\""
        cmdres = run(command, verbose=False)
        if cmdres.success:
            log.info(f"ЗАЖМИ 'BIXBY + VOLUME UP + POWER !'")
            return True

        log.exception(cmdres)
        raise ValueError("Не смог прошить recovery")

    def create_firmware_zip(self, firmware_dir: Path) -> Path:
        local_path_zip = firmware_dir.parent / 'firmware.zip'
        if local_path_zip.is_file():
            log.warning(f"Удаляем старый zip архив: {local_path_zip}")
            local_path_zip.unlink(missing_ok=True)

        log.info(f"Создаем новый zip архив: {local_path_zip}")
        run(f'7z a -tzip -mm=Deflate -mx=4 {local_path_zip} {firmware_dir}/*', timeout=1900, disable_log=True)
        return local_path_zip
