import argparse
import json
from . import api


def json_dict(value):
    """Парсит строку JSON в словарь."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise argparse.ArgumentTypeError(f"Некорректный формат JSON: {value}. Ошибка: {e}")


def handle_firmware_stock(args):
    api.flash_stock(args.model, args.dir_stock, args.sdk)


def handle_firmware_recovery(args):
    api.flash_recovery(args.model, args.path_recovery, args.sdk)


def handle_firmware_boot(args):
    api.flash_boot(args.model, args.sdk)


def handle_kernel(args):
    api.flash_kernel(args.model, args.docker_image, args.new, args.boot, args.no_clean, args.sdk, args.start, args.build,
                     args.flash, args.output)


def handle_custom(args):
    api.flash_custom(args.model, args.firmware_dir, args.format, args.magisk, args.sdk)


def handle_efs(args):
    api.flash_efs(args.model, args.id_phone, args.mount, args.umount, args.flash, args.restore, args.sdk)


def setup_flash_parser(subparsers):
    common_options_parser = argparse.ArgumentParser(add_help=False)
    common_options_parser.add_argument("model", type=str.upper, help="Модель устройства (например, G950, G955)")
    common_options_parser.add_argument("--sdk", type=int, default=28,
                                       help="Версия Android SDK для операций (по умолчанию: 28)")

    # firmware stock
    parser_stock = subparsers.add_parser("stock", help="Прошивает телефон на стоковую прошивку",
                                         parents=[common_options_parser])
    parser_stock.add_argument("dir_stock", type=str, help="Путь к папке с прошивкой")
    parser_stock.set_defaults(func=handle_firmware_stock)

    # firmware recovery
    parser_recovery = subparsers.add_parser("recovery", help="Прошивает recovery", parents=[common_options_parser])
    parser_recovery.add_argument("path_recovery", type=str, help="Путь к recovery.tar")
    parser_recovery.set_defaults(func=handle_firmware_recovery)

    # firmware boot
    parser_boot = subparsers.add_parser("boot", help="Прошивает boot.img", parents=[common_options_parser])
    parser_boot.set_defaults(func=handle_firmware_boot)

    # firmware kernel
    parser_kernel = subparsers.add_parser("kernel", help="Перекомпилирует, модифицирует, прошивает ядро",
                                          parents=[common_options_parser])
    parser_kernel.add_argument("docker_image", help="Имя образа с исходный кодом ядра")
    parser_kernel.add_argument("boot", type=str, help="Путь к boot.img в который зальётся новое ядро")
    parser_kernel.add_argument("--start", action="store_true", help="Запустить контейнер с исходным кодом ядра")
    parser_kernel.add_argument("--build", action="store_true", help="Сборка ядра")
    parser_kernel.add_argument("--flash", action="store_true", help="Прошить ядро")
    parser_kernel.add_argument("--new", action="store_true", help="Пересоздать контейнер, если он уже существует")
    parser_kernel.add_argument("--no-clean", action='store_true', help="Пропустить 'make clean' перед сборкой")
    parser_kernel.add_argument("--output", type=str, help="Путь выходного boot.img")
    parser_kernel.set_defaults(func=handle_kernel)

    # firmware custom
    parser_custom = subparsers.add_parser("custom", help="Прошивает телефон на кастомную прошивку",
                                          parents=[common_options_parser])
    parser_custom.add_argument("firmware_dir", type=str, help="Путь к директории пршивки")
    parser_custom.add_argument("--format", action='store_true', help="Форматировать перед прошивкой")
    parser_custom.add_argument("--magisk", action='store_true', help="Включить в прошивку Magisk через updater-scripts")
    parser_custom.set_defaults(func=handle_custom)

    # firmware efs
    parser_efs = subparsers.add_parser("efs", help="Работа с EFS", parents=[common_options_parser])
    parser_efs.add_argument("id_phone", type=int, help="ID телефона")
    parser_efs.add_argument("--mount", action='store_true', help="Монтирование раздела")
    parser_efs.add_argument("--umount", action='store_true', help="Размонтирование раздела")
    parser_efs.add_argument("--flash", action='store_true', help="Прошить EFS на телефон")
    parser_efs.add_argument("--restore", action='store_true', help="Восстановить оригинальный EFS из бекапа на сервере")
    parser_efs.set_defaults(func=handle_efs)
