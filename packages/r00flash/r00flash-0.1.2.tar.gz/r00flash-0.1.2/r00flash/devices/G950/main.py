import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import questionary

from r00adb import adb
from .tui_boot import TuiBoot
from r00docker import DockerClient
from r00logger import log
from richi import print_fullscreen, print_animated
from .manager_boot import BootManager
from .manager_efs import ManagerEFS
from .manager_firmware import FirmwareManager
from .manager_kernel import KernelManager
from .utils import push_firmware_on_device, get_env_by_filename
from ... import custom_style


def process_stock(dir_stock):
    if FirmwareManager.flash_stock(dir_stock):
        print_fullscreen('FLASH\nSTOCK\nSUCCESS !')


def process_recovery(path_recovery):
    if FirmwareManager.flash_recovery(path_recovery):
        print_fullscreen('bixby + volume up + power', timeout=20)


def process_boot(model):
    bm = BootManager()
    tui_boot = TuiBoot(model, bm)
    tui_boot.start()


def process_kernel(docker_image, new, boot_path, no_clean, start, build, flash, output_path):
    env_data = get_env_by_filename('kernel.env')
    docker = DockerClient(image_name=docker_image)
    km = KernelManager(docker)

    if start or build or new:
        km.start_container(new, env_data)
        log.info(f"Запустил контейнер: {km.docker.container_name}")

    if build:
        km.unpacking_boot(boot_path)
        km.build(no_clean)
        boot = km.repacking_boot(boot_path, output_path)

        if flash:
            km.write_bootimg(boot)


def go_recovery(format_data):
    adb.reboot(recovery_mode=True)
    if not adb.is_twrp_mode():
        raise ValueError("Я не вижу где твой TWRP")

    if format_data:
        adb.twrp.wipe()
    return True


def process_custom(firmware_dir, format_data, magisk):
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            thread_recovery = executor.submit(go_recovery, format_data)

            firmware_dir = Path(firmware_dir).resolve()
            device_path = f'/sdcard/firmware.zip'
            fm = FirmwareManager()

            if not magisk:  # Remove magisk in updater-script
                updater_file = firmware_dir / 'META-INF/com/google/android/updater-script'
                updater_data = updater_file.read_text()
                start_marker = "# __MARK_MAGISK_START__"
                end_marker = "# __MARK_MAGISK_END__"
                pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?", flags=re.DOTALL)
                cleaned_text = re.sub(pattern, "", updater_data)
                shutil.copy(updater_file, updater_file.with_suffix('.bak'))
                updater_file.write_text(cleaned_text, encoding='utf-8')

            firmware_zip = fm.create_firmware_zip(firmware_dir)
            thread_recovery.result()

        push_firmware_on_device(firmware_zip, device_path)
        log.info("Устанавливаем прошивку...")
        adb.twrp.install_zip(device_path)
        print_animated("Установка завершена. Перезагружаю устройство...")
    finally:
        if not magisk:
            shutil.copy(updater_file.with_suffix('.bak'), updater_file)



def process_efs(id_phone, mount, umount, flash, restore):
    me = ManagerEFS(id_phone)
    if restore:
        me.restore()

    if mount:
        me.mount()

    if umount:
        me.umount()

    if flash:
        me.flash()
