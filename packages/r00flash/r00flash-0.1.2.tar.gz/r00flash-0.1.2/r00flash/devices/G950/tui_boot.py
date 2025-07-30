import sys
from pathlib import Path

import questionary

from .manager_boot import BootManager
from ... import custom_style, pointer


class TuiBoot:
    def __init__(self, model: str, bm: BootManager):
        self.model = model
        self.bm = bm

    def add_choice_exit(self, data: list):
        data.append(questionary.Choice(title="--- Выход ---", value="exit"))

    def select_boot(self) -> Path:
        # Выбор прошивки
        firmwares_root = Path('/media/user/Android/Devices/GalaxyS8/Fireware/Android_9.0_SDK28/horizon_rom/patched')
        firmwares_path = [str(firmware_folder) for firmware_folder in firmwares_root.glob('source*')]
        firmwares_name = [str(firmware_folder.name) for firmware_folder in firmwares_root.glob('source*')]
        self.add_choice_exit(firmwares_name)
        firmware_name = questionary.select(
            "Выбери название прошивки",
            choices=firmwares_name,
            pointer=pointer,
            style=custom_style
        ).ask()

        if firmware_name == 'exit':
            sys.exit(0)

        for firmware_dir in firmwares_path:
            firmware_dir = Path(firmware_dir)
            if firmware_name == firmware_dir.name:
                break

        # Local OR Device
        device_or_local = questionary.select(
            "Local or Device",
            choices=[
                questionary.Choice(title="Local boot", value="local"),
                questionary.Choice(title="Device boot", value="device"),
            ],
            pointer=pointer,
            style=custom_style
        ).ask()

        boots_root = firmware_dir / f'HoriOne/Kernel/{self.model}'
        if device_or_local == 'local':
            boots_name = [str(boot_name.name) for boot_name in boots_root.glob('boot*img')]
            boot_name = questionary.select(
                "Выбери boot.img",
                choices=boots_name,
                pointer=pointer,
                style=custom_style
            ).ask()

            boot_path = boots_root / boot_name
            return boot_path
        else:
            boot_device_path = boots_root / 'boot_device.img'
            self.bm.copy_from_device(boot_device_path)
            return boot_device_path

    def menu_boot(self, boot_input: Path, flag_unpack):
        result = {
            "unpack": questionary.Choice(title="Распаковать (unpack)", value="unpack"),
            "repack": questionary.Choice(title="Перепаковать (repack)", value="repack"),
            "flash": questionary.Choice(title="Записать на устройство (flash)", value="flash"),
        }

        if not flag_unpack:
            del result["repack"]

        data = list(result.values())
        self.add_choice_exit(data)
        action = questionary.select(
            f"Выбери что сделать с {boot_input.name}",
            choices=data,
            pointer=pointer,
            style=custom_style
        ).ask()

        if action == "exit":
            sys.exit(0)
        return action

    @staticmethod
    def menu_repack(boot_path: Path):
        answer = questionary.confirm(f"Заменить входной {boot_path.name}?", style=custom_style).ask()
        if not answer:
            boot_output_name = questionary.path(
                "Укажи новое имя (без расширения):",
                style=custom_style,
                default=str(boot_path.stem) + '_new'
            ).ask()
            boot_path_new = boot_path.parent / f'{boot_output_name}.img'
        else:
            boot_path_new = boot_path
        return boot_path_new

    @staticmethod
    def menu_flash():
        why_boot = questionary.select(
            "Что прошить?",
            choices=[
                questionary.Choice(title="Оригинальный boot", value="orig"),
                questionary.Choice(title="Распакованный boot", value="unpacked"),
            ],
            pointer=pointer,
            style=custom_style
        ).ask()
        return why_boot

    def start(self):
        boot_input = None
        boot_output = None
        flag_unpack = False
        flag_selected_boot = False

        try:
            while True:
                if not flag_selected_boot:
                    boot_input = self.select_boot()
                    flag_selected_boot = True
                else:
                    action = self.menu_boot(boot_input, flag_unpack)
                    if action == 'unpack':
                        self.bm.unpack(boot_input)
                        flag_unpack = True
                    elif action == 'repack':
                        boot_output = self.menu_repack(boot_input)
                        self.bm.repack(boot_input, boot_output)
                    elif action == 'flash':
                        why_boot = self.menu_flash()
                        if why_boot == 'orig':
                            self.bm.flash(boot_input)
                        else:
                            boot_output = self.menu_repack(boot_input)
                            self.bm.repack(boot_input, boot_output)
                            self.bm.flash(boot_output)
                    elif action == "exit":
                        sys.exit(0)
        except KeyboardInterrupt:
            questionary.print("Выход")
            return
