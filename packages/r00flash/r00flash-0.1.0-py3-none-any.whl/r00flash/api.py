import importlib
from pathlib import Path
from adb import adb


def get_device_controller(model_name: str):
    module_path = f"r00flash.devices.{model_name.upper()}.main"
    return importlib.import_module(module_path)

def flash_stock(model, dir_stock, sdk):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    dir_stock = Path(dir_stock).resolve()
    return device_logic.process_stock(dir_stock)

def flash_recovery(model, path_recovery, sdk):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    path_recovery = Path(path_recovery).resolve()
    return device_logic.process_recovery(path_recovery)

def flash_boot(model, sdk):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    return device_logic.process_boot(model)

def flash_kernel(model, docker_image, new, boot_path, no_clean, sdk, start, build, flash, output):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    return device_logic.process_kernel(docker_image, new, boot_path, no_clean, start, build, flash, output)


def flash_custom(model, firmware_dir, format_data, magisk, sdk):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    return device_logic.process_custom(firmware_dir, format_data, magisk)


def flash_efs(model, id_phone, mount, umount, flash, restore, sdk):
    adb.device.sdk = sdk
    device_logic = get_device_controller(model)
    return device_logic.process_efs(id_phone, mount, umount, flash, restore)