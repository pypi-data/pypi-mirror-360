import os
import os.path
import shutil
import sys
from pathlib import Path
from typing import Union

import pyperclip

from adb import adb
from r00logger import log
from system import run
from .utils import find_project_root


class BootManager:
    @staticmethod
    def copy_from_device(boot_output) -> str:
        """
        Копирует boot.img из дейвайса на хост
        :return:
        """
        adb.reboot(recovery_mode=True)
        device_path = adb.twrp.backup('boot')
        local_path = Path(boot_output)
        if local_path.is_file():
            local_path.unlink()
        adb.pull(device_path, local_path)
        return str(local_path)

    @staticmethod
    def get_aik_dir(boot_input: Path) -> Path:
        boot_dir = boot_input.parent
        aik_dir = boot_dir / f'aik_{boot_input.stem}'
        return aik_dir

    def unpack(self, boot_input: Path):
        aik_dir = self.get_aik_dir(boot_input)
        unpacking_sh = aik_dir / 'unpackimg.sh'
        cleanup_sh = aik_dir / 'cleanup.sh'

        # Если нет aik папки, скачиваем
        if not aik_dir.is_dir() or not unpacking_sh.is_file():
            aik_source = find_project_root(__file__) / 'data' / 'aik-linux'
            for item in aik_source.iterdir():
                target = aik_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)
        else:
            run(str(cleanup_sh), verbose=True)

        os.chdir(aik_dir)
        run(f'cp {boot_input} {aik_dir}/boot.img', verbose=False)
        run(f'{unpacking_sh}', disable_log=True)
        log.info(f"UNPACK {boot_input.name} success")

    def repack(self, boot_input, boot_output):
        aik_dir = self.get_aik_dir(boot_input)
        if not aik_dir.is_dir() and not (aik_dir / 'ramdisk').is_dir():
            log.error("Сначала сделай --unpack")
            return False

        os.chdir(aik_dir)
        repacking_sh = aik_dir / 'repackimg.sh'
        run(f'{repacking_sh}', disable_log=True)
        new_boot = f'{aik_dir}/image-new.img'

        shutil.copy(new_boot, boot_output)
        log.info(f'REPACK boot.img success {boot_output}')

    @staticmethod
    def flash(boot_path) -> None:
        log.info(f'Прошиваем {boot_path} ...')
        device_path = '/sdcard/boot.img'
        adb.reboot(recovery_mode=True)
        adb.push(boot_path, device_path)
        adb.twrp.overwrite_boot_partition(device_path)
        adb.reboot()
