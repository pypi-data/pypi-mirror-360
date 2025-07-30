from pathlib import Path
from system import run
from r00logger import log

apk_dir = Path("/media/user/Android/APK/CheckRoot")
for filepath in apk_dir.glob('*.apk'):
    run(f'adb install "{filepath}"', timeout=333)
    log.info(filepath)
