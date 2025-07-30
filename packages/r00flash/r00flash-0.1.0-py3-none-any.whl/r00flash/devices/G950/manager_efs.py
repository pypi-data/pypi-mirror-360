from pathlib import Path

from platformdirs import user_cache_dir
from adb import adb
from r00logger import log
from r00server import serv
from system import run


class ManagerEFS:
    def __init__(self, id_phone):
        self.cache_dir = Path(user_cache_dir())
        self.work_img = self.cache_dir / f'efs_{id_phone}.img'
        self.mount_dir = self.cache_dir / f'efs_{id_phone}_dir'
        self.stock_remote_img = f'devices/{id_phone}/efs/stock.img'
        self.id_phone = id_phone

    def restore(self):
        self.umount()
        if self.work_img.is_file():
            self.work_img.unlink(missing_ok=True)
        serv.download(self.stock_remote_img, self.work_img)
        log.info(f'Восстановлен файл {self.work_img} из бекапа {self.stock_remote_img}')

    def is_backup(self):
        # Проверяем, есть ли бекап на сервере
        if not serv.exist_file(self.stock_remote_img):
            log.info(f'Не найден файл stock.img на сервере, делаем backup EFS: {self.stock_remote_img}')
            stock_local_img = '/tmp/efs_stock.img'
            adb.reboot(recovery_mode=True)
            device_path_img = adb.twrp.backup('efs')
            adb.pull(device_path_img, stock_local_img)
            serv.upload(stock_local_img, self.stock_remote_img)

        # Готовим work.img для модифиикаций
        if not self.work_img.exists():
            log.trace(f'Не найден файл {self.work_img}, делаем копию stock.img')
            serv.download(self.stock_remote_img, self.work_img)

    def mount(self):
        self.is_backup()
        if self.work_img.is_mount():
            log.warning(f'Не делаем mount так как образ уже смонтирован: {self.work_img}')
            return True

        if not self.mount_dir.is_dir():
            run(f'sudo mkdir -p {self.mount_dir}')

        run(f'sudo mount -o loop -t ext4 {self.work_img} {self.mount_dir}')
        check_file = self.mount_dir / 'nv_data.bin'
        if not check_file.exists():
            raise ValueError(f"Не могу найти файл {check_file}. Образ не смонтирован?")
        log.info(f'Образ смонтирован: {self.mount_dir}')

    def umount(self):
        if not self.mount_dir.is_mount():
            log.warning(f'Не делаем umount так как образ уже размонтирован: {self.mount_dir}')
            return True

        run(f'sudo umount --lazy {self.mount_dir}')
        check_file = self.mount_dir / 'nv_data.bin'
        if check_file.exists():
            raise ValueError(f"Нашел файл {check_file}. Образ не размонтирован?")
        log.info(f'Образ размонтирован! {self.work_img}')

    def flash(self):
        adb.reboot(recovery_mode=True)
        device_path_img = adb.push(self.work_img, '/sdcard/efs.img')
        adb.twrp.overwrite_efs_partition(device_path_img)
        adb.reboot()
