import socket
import time

PHONE_IP = '192.168.1.68'
PHONE_PORT = 1030


def stream_logcat(interval=0.5):
    """
    Эмулирует real-time logcat, периодически запрашивая новые логи.
    :param interval: Интервал опроса в секундах.
    """
    print("[INFO] Starting real-time logcat streaming...")
    print(f"[INFO] Polling interval: {interval}s. Press Ctrl+C to stop.")

    # 1. Первоначальная очистка буфера логов на устройстве
    print("[INFO] Clearing initial logcat buffer...")
    execute_command("logcat -c")

    try:
        while True:
            # 2. Запрашиваем новые логи
            # 'logcat -d' выводит буфер и немедленно завершается
            new_logs = execute_command("logcat -d")

            if new_logs:
                # 3. Выводим то, что получили
                print(new_logs)

                # 4. Снова очищаем буфер, чтобы не получать эти же логи в следующий раз
                execute_command("logcat -c")

            # 5. Ждем перед следующим запросом
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\n[-] An unexpected error occurred during streaming: {e}")

def interactive_command(cmd: str):
    """
    Выполняет команду и выводит ее результат в реальном времени,
    не закрывая соединение до принудительного прерывания (Ctrl+C).
    """
    # Добавляем \n, чтобы команда выполнилась
    full_cmd = f"{cmd}\n"
    print(f"[INFO] Executing interactive command: {cmd}")
    print("[INFO] Press Ctrl+C to stop.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(9999)
            s.connect((PHONE_IP, PHONE_PORT))
            print(f"[+] Connected to {PHONE_IP}:{PHONE_PORT}")

            s.sendall(full_cmd.encode())

            # Бесконечный цикл для чтения и вывода данных
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    print("\n[-] Connection closed by remote host.")
                    break
                # Просто печатаем полученные байты как есть
                print(chunk.decode(errors='ignore'), end='', flush=True)

    except socket.timeout:
        print("\n[-] Error: Connection timed out.")
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"\n[-] An unexpected error occurred: {e}")


def execute_command(cmd: str):
    # Добавляем команду 'echo' со случайной меткой в конец,
    # чтобы точно знать, где закончился вывод основной команды.
    ECHO_BOUNDARY = "EXECUTION_FINISHED"
    full_cmd = f"{cmd}; echo {ECHO_BOUNDARY}\n"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(9999)  # Увеличим общий таймаут на всякий случай
            s.connect((PHONE_IP, PHONE_PORT))

            # --- УБРАН БЛОК s.recv(4096) ---
            # Сразу отправляем команду
            print(f"[>] Sending command: {cmd}")
            s.sendall(full_cmd.encode())

            # Читаем ответ в цикле, пока не встретим нашу метку
            response_buffer = ""
            while ECHO_BOUNDARY not in response_buffer:
                # Читаем данные небольшими порциями, чтобы не блокироваться надолго
                chunk = s.recv(4096).decode(errors='ignore')
                if not chunk:
                    # Сокет закрылся раньше времени
                    print("[-] Connection closed unexpectedly.")
                    break
                response_buffer += chunk

            # Убираем нашу команду и метку из ответа для чистоты
            # Сначала убираем метку и все, что после нее
            clean_response = response_buffer.split(ECHO_BOUNDARY)[0]
            # Затем убираем саму команду, которую мы отправили
            if clean_response.startswith(full_cmd.strip()):
                clean_response = clean_response[len(full_cmd.strip()):].lstrip()

            print(f"[<] Response:\n---\n{clean_response.strip()}\n---")
            return clean_response.strip()

    except socket.timeout:
        print("[-] Error: Connection or read operation timed out.")
        return None
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
        return None


def analyze_and_print_results(test_name: str, result: str, commands_config: dict):
    """Анализирует результат, фильтрует и выводит улики."""
    if not result or not result.strip():
        print(f"[-] No direct evidence found in '{test_name}'.")
        return False

    all_lines = result.strip().split('\n')
    evidence_lines = []

    # Получаем фильтры для текущего теста
    ignore_list = commands_config[test_name].get("ignore", [])

    for line in all_lines:
        line = line.strip()
        if not line:
            continue

        # Проверяем, не нужно ли игнорировать эту строку
        should_ignore = False
        for pattern in ignore_list:
            if pattern in line:
                should_ignore = True
                break

        if not should_ignore:
            evidence_lines.append(line)

    if evidence_lines:
        print(f"[!!!] POSITIVE FIND in '{test_name}':")
        for evidence in evidence_lines:
            print(f"    [+] {evidence}")
        return True
    else:
        # Все строки были отфильтрованы как ложные срабатывания
        print(f"[-] No direct evidence found in '{test_name}' (output was filtered).")
        return False


def run_magisk_detection_suite():
    print("\n[INFO] Starting Magisk detection suite...")

    # Конфигурация команд с дополнительными параметрами для анализа
    detection_commands = {
        "System Dumpstate Analysis": {
            "cmd": r'dumpstate 2>/dev/null | grep -i "magisk"',
            "desc": "Ищет следы Magisk и его компонентов в полном отчете о состоянии системы (dumpstate)."
        },
        "File System Search": {
            "cmd": "find / -name \"*magisk*\" -o -name \"*corepath*\" -o -name \"*r00ft1h*\" 2>/dev/null",
            "desc": "Ищет файлы и папки с именами, содержащими 'magisk' или никнейм разработчика."
        },
        "Mount Namespace Discrepancy": {
            "cmd": "cat /proc/1/mountinfo > /data/local/tmp/m1; cat /proc/self/mountinfo > /data/local/tmp/m2; diff /data/local/tmp/m1 /data/local/tmp/m2; rm /data/local/tmp/m1 /data/local/tmp/m2",
            "desc": "Сравнивает точки монтирования init и текущего процесса. Любое различие - признак сокрытия (DenyList)."
        },
        "SU Binary Detection": {
            "cmd": "ls -l /sbin/su /system/bin/su /system/xbin/su 2>/dev/null",
            "desc": "Ищет su файл"
        },
        "Anomalous Root Processes": {
            "cmd": "ps -ef | awk '$1 == \"root\" {print $8}' | xargs -I{} readlink -f {} 2>/dev/null | grep -vE '^/system/|^/vendor/|^/apex/|^$' | sort -u",
            "desc": "Ищет root-процессы, запущенные из подозрительных мест (не /system, /vendor)."
        },
        "Anomalous SELinux Contexts": {
            "cmd": "ls -Z /data/adb /sbin 2>/dev/null | grep 'u:object_r:magisk_file:s0'",
            "desc": "Ищет файлы с характерным для Magisk SELinux-контекстом 'magisk_file'."
        },
        "Suspicious Init Commands": {
            "cmd": "find /etc /system/etc /vendor/etc -name \"*.rc\" -type f -exec grep -H -E 'mount.*tmpfs|start .*\\/data\\/' {} + 2>/dev/null",
            "desc": "Ищет в загрузочных скриптах подозрительные команды.",
            "ignore": ["boottrace", "unzip"]
        },
        # -- Простые тесты, которые могут быть легко обмануты сокрытием, но все еще полезны --
        "Mount Points": {
            "cmd": "cat /proc/mounts | grep -i -e 'magisk' -e 'core/mirror'",
            "desc": "Прямой поиск точек монтирования Magisk."
        },
        "System Properties": {
            "cmd": "getprop | grep -i magisk",
            "desc": "Поиск системных свойств, установленных Magisk."
        },
        "Anomalous Root Processes2": {
            "cmd": "ps -ef | grep magisk",
            "desc": "Поиск magisk процессов",
            "ignore": ["grep magisk"]
        },
        "Kernel Messages (dmesg)": {
            "cmd": "dmesg | grep -i -e 'magisk' -e 'init.magisk'",
            "desc": "Ищет следы Magisk в логах ядра, которые остаются с раннего этапа загрузки."
        },
        "Android Logcat": {
            "cmd": "logcat -d | grep -i -e 'magisk' -e 'zygisk' -e 'DenyList'",
            "desc": "Ищет упоминания компонентов Magisk в системных логах Android."
        },
        "Android LAST_KMSG": {
            "cmd": "cat /proc/last_kmsg | grep -i -e 'magisk' -e 'zygisk' -e 'DenyList'",
            "desc": "Ищет упоминания компонентов Magisk last_kmsg"
        },
        "Selinux detect": {
            "cmd": "strings /sys/fs/selinux/policy | grep magisk",
            "desc": "Ищет упоминания компонентов Magisk в policy"
        },
        "Directory Structure Analysis": {
            "cmd": "find /data /cache -type d -name \"modules\" 2>/dev/null | sed 's/\\/modules$//'",
            "desc": "Находит корневой каталог руткита по наличию подкаталога 'modules'."
        },
        "Anomalous Execution in Memory": {
            "cmd": "grep 'r-xp' /proc/*/maps | grep -E '\\s/data/|\\s/cache/|\\s/dev/' | grep -v 'dalvik'",
            "desc": "Ищет процессы, исполняющие код из подозрительных мест (/data, /cache)."
        },
        "Init Script Fingerprint Scan": {
            "cmd": "find /etc /system/etc /vendor/etc -type f -name \"*.rc\" -exec grep -H -E \"on\\s*post-fs-data|mount\\s*tmpfs.*tmpfs\\s*/sbin\" {} + 2>/dev/null",
            "desc": "Ищет в init-скриптах структурные команды-отпечатки Magisk."
        }
    }


    total_evidence_found = False
    for test_name, config in detection_commands.items():
        print(f"\n--- Running Test: {test_name} ---")
        print(f"    (Description: {config['desc']})")

        result = execute_command(config['cmd'])

        if result is not None:
            if analyze_and_print_results(test_name, result, detection_commands):
                total_evidence_found = True
        else:
            # Ошибка выполнения команды
            print(f"[-] Test '{test_name}' failed to execute.")

        print('-' * 70)

    if total_evidence_found:
        print("\n[CONCLUSION] Magisk traces were FOUND on the system.")
    else:
        print("\n[CONCLUSION] No direct traces of Magisk were found with these methods.")


if __name__ == '__main__':
    #run_magisk_detection_suite()
    #interactive_command("unbuffer logcat")
    #stream_logcat()

    #interactive_command('dmesg')
    execute_command('id')
