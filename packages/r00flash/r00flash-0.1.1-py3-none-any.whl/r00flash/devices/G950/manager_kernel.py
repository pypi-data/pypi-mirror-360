import os
import os.path
import re
import sys

from dotenv import dotenv_values

from adb import adb
from r00docker import DockerClient
from r00logger import log
from richi import print_nice
from secret import secret


class KernelManager:
    def __init__(self, docker):
        self.docker: DockerClient = docker

    def is_success_compiled(self):
        status, output = self.docker.exec_run('stat /root/horizon/arch/arm64/boot/Image')
        if status == 0 and 'regular file' in output:
            return True
        return False

    @staticmethod
    def crop_compile_log(input_string):
        # Разбиваем строку на строки по символу новой строки
        lines = input_string.split('\n')

        # Обработанные строки будем складывать в список
        processed_lines = []
        last_line_was_dashed = False

        for line in lines:
            # Если строка начинается с CC или LD, заменяем её на "-------"
            if re.match(
                    r'^\s+(CC|LD|KSYM|UPD|CHK|GEN|MODPOST|LINK|AR|AS|PERLASM|DTC|MK_FW|IHEX|VDSOSYM|VDSOL|CALL|HOSTLD|HOSTCC|MKELF|replace|boolean|INFO|VDSOA|OBJCOPY|DTBTOOL|SYSMAP|GZIP)',
                    line):
                if not last_line_was_dashed:
                    processed_lines.append('-------')
                last_line_was_dashed = True
            else:
                if "ignoring unsupported character '\r'" in line:
                    line = line.replace('\r', '\\r')
                processed_lines.append(line)
                last_line_was_dashed = False

        # Объединяем обработанные строки обратно в один текст
        return '\n'.join(processed_lines)

    def stop_container(self):
        """ Остановка контейнера """
        self.docker.kill_container()

    def remove_container(self):
        """ Удаляем контейнер """
        self.stop_container()
        self.docker.remove_container()

    def start_container(self, is_new: bool, env_data: dict):
        if is_new:
            self.remove_container()

        try:
            if self.docker.is_container_running():
                return True
            else:
                stopped = self.docker.list_containers(filters={"name": self.docker.container_name})
                if stopped:
                    self.docker.start_container()
                else:
                    log.debug(f"Контейнер '{self.docker.container_name}' не найден. Загружаем и запускаем его...")
                    if not self.docker.get_image(self.docker.image):
                        self.docker.login_to_registry(secret.dockerhub.user, secret.dockerhub.paswd)

                    self.docker.run(
                        env=env_data,
                        detach=True,
                        force=True
                    )
        except Exception as e:
            raise ValueError(f"Не удалось запустить контейнер") from e

    def unpacking_boot(self, path_boot):
        """Распаковывает boot.img внутри контейнера."""
        remote_boot = '/root/aik/boot.img'
        self.docker.exec_run('cd /root/aik && rm -rf boot.img image-new.img ramdisk ramdisk-new.cpio.gz split_img')

        self.docker.copy_to_container(path_boot, remote_boot)
        self.docker.exec_script_in_container("cd /root/aik &&./cleanup.sh --nosudo")
        status_unpack, out_unpack = self.docker.exec_script_in_container("cd /root/aik && ./unpackimg.sh --nosudo")
        if status_unpack == 0:
            log.debug(f'Образ boot успешно распакован в {remote_boot}')
        else:
            log.exception(f"Скрипт распаковки завершился с ошибкой (статус {status_unpack})")
            raise

    def repacking_boot(self, path_boot, output_path=None):
        repack_script = """
        #!/bin/bash
        cd /root/aik

        cp /root/horizon/arch/arm64/boot/Image /root/aik/split_img/boot.img-kernel
        #/root/horizon/tools/dtbtool -o /root/aik/split_img/boot.img-dt /root/horizon/arch/arm64/boot/dts/exynos/

        ./repackimg.sh --nosudo
        """

        status_repack, out_repack = self.docker.exec_script_in_container(repack_script)
        log.trace(f"Вывод скрипта перепаковки:\n{out_repack}")
        if status_repack != 0:
            log.error(f"Скрипт перепаковки завершился с ошибкой (статус {status_repack})")
            raise

        # Проверяем что новый образ создан
        container_output_img = '/root/aik/image-new.img'
        output = self.docker.exec_run(f'ls -la {container_output_img}')
        if output[0] == 0 and not '-rw-r--r--' in output[1]:
            raise ValueError("Не найден image-new.img в aik в контейнере")

        output = output_path if output_path else path_boot
        if os.path.exists(output):
            log.debug(f"Удаляем существующий файл образа boot: {output}")
            os.remove(output)

        self.docker.copy_from_container(container_output_img, output)
        log.success(f'Образ boot успешно перепакован в: {output}')

    def build(self, no_clean: bool):
        print_nice('... compile kernel ...', variant=2)

        if no_clean:
            log.debug("Запуск компиляции без make clean...")
            script_prebuild = """
                                #!/bin/bash
                                echo insecure >> ~/.curlrc
                                cd /root/horizon
                                make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- exynos8895-dreamlte_defconfig
                                """
        else:
            log.debug("Запуск компиляции с make clean...")
            # make mrproper
            script_prebuild = """
                                #!/bin/bash
                                echo insecure >> ~/.curlrc
                                cd /root/horizon
                                make -j32 ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- clean
                                make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- exynos8895-dreamlte_defconfig
                                """

        status, output = self.docker.exec_script_in_container(script_content=script_prebuild)
        if status != 0:
            raise ValueError("Ошибка при выполнении скрипта подготовки сборки")

        script_build = 'cd /root/horizon && make -j32 ARCH=arm64 CROSS_COMPILE=aarch64-linux-android-'
        status, output = self.docker.exec_script_in_container(script_content=script_build)
        warn_log = self.crop_compile_log(output)
        count = sum(1 for line in warn_log.split() if line.strip() == '-------')
        log.warning(warn_log + f'\n!##### {count} warnings #####!')

        if not self.is_success_compiled():
            print_nice('Compilation ERROR ;(', variant=4, title=f'{count} count errors', type='error')
            sys.exit(1)
        print_nice("Compilation SUCCESS !!!", 4)

    def write_bootimg(self, boot_path: str) -> str:
        adb.reboot(recovery_mode=True)
        device_path = '/sdcard/boot.img'
        if adb.exists(device_path):
            adb.remove(device_path)

        adb.push(boot_path, device_path)
        adb.twrp.overwrite_boot_partition(device_path)
        adb.reboot()

    # def apatch_inject(self, boot_path):
    #     log.info("Прошивка Apatch...")
    #     dir_apatch = '/media/user/Android/Apatch/boot_apatch'
    #     os.chdir(dir_apatch)
    #
    #     # Распаковываем boot.img и патчим
    #     run('rm -rf ./boot.img')
    #     run(f'cp {boot_path} ./boot.img')
    #     run('./magiskboot unpack ./boot.img')
    #     run('./kptools-linux -p --image ./kernel --skey "Asdqwe468155" --kpimg ./kpimg-android --out ./kernel_patched')
    #     run('mv ./kernel_patched ./kernel')
    #     run('./magiskboot repack ./boot.img')
    #
    #     # Копируем обратно в исходную директорию
    #     run(f'mv ./new-boot.img {boot_path}')
    #     print_nice('Пароль на Apatch: Asdqwe468155', 2)
    #     run('./magiskboot cleanup')
