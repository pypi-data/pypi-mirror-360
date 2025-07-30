import os
import sys

# --- НАСТРОЙКИ ---
WORK_DIR = "/media/user/Android/Devices/GalaxyS8/Fireware/Android_9.0_SDK28/horizon_rom/patched/source_combat/system"

REPLACE_PAIRS = [
    ('N950F', 'G950F'),
    ('greatlte', 'dreamlte')
]

# Список расширений файлов, которые считаются бинарными и которые мы НЕ трогаем.
# Можно добавлять сюда другие по мере необходимости.
BINARY_EXTENSIONS_TO_IGNORE = {
    '.odex', '.vdex', '.oat', '.art',  # Оптимизированный/скомпилированный код
    '.ttf', '.otf', '.ttc',  # Шрифты
    '.qmg', '.spi', '.webp', '.png',  # Графика
    '.ogg', '.mp3', '.wav',  # Аудио
    '.so', '.a', '.elf',  # Библиотеки и исполняемые файлы
    '.jar', '.apk',  # Java-архивы и пакеты
    '.bin', '.dat', '.db'  # Общие бинарные данные/базы
}

# Явные исключения: файлы, которые ЯВЛЯЮТСЯ бинарными, но мы ХОТИМ в них произвести замену.
# Используем пути относительно WORK_DIR.
BINARY_FILES_TO_PROCESS = {
    # 'vendor/lib/soundfx/libswdap.so',
    # 'vendor/lib64/soundfx/libswdap.so'
    # Добавь сюда другие бинарники, если уверен, что их нужно патчить.
}


def is_likely_binary(filepath: str, chunk_size: int = 1024) -> bool:
    """
    Эвристическая проверка, является ли файл бинарным.
    Читает начало файла и ищет нулевой байт.
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(chunk_size)
        return b'\x00' in chunk
    except IOError:
        return True  # Если не можем прочитать, лучше считать бинарным


def replace_content_in_files(directory: str, old_str: str, new_str: str):
    print(f"--- Замена содержимого: '{old_str}' -> '{new_str}' ---")

    old_bytes = old_str.encode('utf-8')
    new_bytes = new_str.encode('utf-8')

    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            relative_filepath = os.path.relpath(filepath, directory)

            # Получаем расширение файла
            _, ext = os.path.splitext(filename)

            # Решаем, обрабатывать ли файл
            process_this_file = False
            if relative_filepath in BINARY_FILES_TO_PROCESS:
                # 1. Это файл из списка явных исключений для обработки
                process_this_file = True
                print(f"  [*] Обработка бинарного файла из списка исключений: {relative_filepath}")
            elif ext.lower() in BINARY_EXTENSIONS_TO_IGNORE:
                # 2. Расширение в "черном списке" - пропускаем
                continue
            elif not is_likely_binary(filepath):
                # 3. Файл не похож на бинарный - обрабатываем
                process_this_file = True

            if process_this_file:
                try:
                    with open(filepath, 'rb') as f:
                        content = f.read()

                    if old_bytes in content:
                        print(f"  [+] Найдено и заменено в: {relative_filepath}")
                        new_content = content.replace(old_bytes, new_bytes)
                        with open(filepath, 'wb') as f:
                            f.write(new_content)

                except Exception as e:
                    print(f"  [!] Ошибка при обработке {filepath}: {e}", file=sys.stderr)

    print("Замена содержимого завершена.\n")


def rename_files_and_dirs(directory: str, old_str: str, new_str: str):
    # Эта функция остается без изменений, она безопасна
    print(f"--- Переименование файлов и папок: '{old_str}' -> '{new_str}' ---")
    for root, dirs, files in os.walk(directory, topdown=False):
        # ... (код из предыдущего ответа)
        for filename in files:
            if old_str in filename:
                old_path = os.path.join(root, filename)
                new_filename = filename.replace(old_str, new_str)
                new_path = os.path.join(root, new_filename)
                try:
                    print(f"  [R] Файл: {old_path} -> {new_path}")
                    os.rename(old_path, new_path)
                except OSError as e:
                    print(f"  [!] Ошибка переименования файла {old_path}: {e}", file=sys.stderr)
        for dirname in dirs:
            if old_str in dirname:
                old_path = os.path.join(root, dirname)
                new_dirname = dirname.replace(old_str, new_str)
                new_path = os.path.join(root, new_dirname)
                try:
                    print(f"  [R] Папка: {old_path} -> {new_path}")
                    os.rename(old_path, new_path)
                except OSError as e:
                    print(f"  [!] Ошибка переименования папки {old_path}: {e}", file=sys.stderr)
    print("Переименование завершено.\n")


def main():
    if not (os.path.isdir(os.path.join(WORK_DIR, 'etc')) and os.path.isdir(os.path.join(WORK_DIR, 'omc'))):
        print(f"Ошибка: Директория '{WORK_DIR}' не похожа на корень системного раздела.", file=sys.stderr)
        sys.exit(1)

    os.chdir(WORK_DIR)
    print(f"Рабочая директория: {os.getcwd()}")

    for old, new in REPLACE_PAIRS:
        replace_content_in_files('.', old, new)

    for old, new in REPLACE_PAIRS:
        rename_files_and_dirs('.', old, new)

    print("Портирование успешно завершено!")


if __name__ == "__main__":
    main()