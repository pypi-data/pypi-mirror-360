from pathlib import Path

from r00logger import log
from system import get_file_metadata, set_file_metadata, run

BOOT_DIR = Path(
    '/media/user/Android/Devices/GalaxyS8/Fireware/Android_9.0_SDK28/horizon_rom/patched/source_combat/HoriOne/Kernel/G950/aik_boot_device/ramdisk')
NEW_FILES = [
    # Path("/media/user/Android/Magisk/source_build/magisk_build_output/app-debug_1/lib/arm64-v8a/libmagiskinit.so")
    Path("/media/user/Android/Magisk/source_build/mod/Magisk/out/app-debug_1/lib/arm64-v8a/libmagiskinit.so")
]

for new_file in NEW_FILES:
    if 'libmagiskinit' in str(new_file):
        boot_file = BOOT_DIR / 'init'

        metadata = get_file_metadata(boot_file)
        run(f'sudo chmod 777 {boot_file}')
        log.info(f"Был размер: {boot_file.name} - {boot_file.stat().st_size}")
        run(f'sudo rm -rf {boot_file}')
        run(f'sudo cp {new_file} {boot_file}')
        log.debug(f"Замена файла: {new_file} -> {boot_file}")
        log.info(f"Стал размер: {boot_file.name} - {boot_file.stat().st_size}")
        set_file_metadata(boot_file, metadata)
