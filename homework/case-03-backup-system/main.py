"""
main.py - точка входа в программу BackupSystem.

Команды:
    python main.py check                 - проверить структуру проекта
    python main.py backup                - создать резервную копию
    python main.py list                  - показать список копий
    python main.py verify                - проверить целостность всех копий
    python main.py restore <копия|дата>  - восстановить в папку restored
    python main.py compare <папка1> <папка2> - сравнить две папки по SHA-256

Примеры restore:
    python main.py restore backup_2026-11-16_14-01-47
    python main.py restore "2026-11-16 14:01"
"""

import json
import sys
from pathlib import Path

from backup import create_backup
from integrity import verify_backup, read_manifest, build_file_table, compare_with_table
from restore import choose_backup, restore_backup
from storage import (
    PROJECT_DIR, DEFAULT_SOURCE, BACKUPS_DIR, RESTORE_DIR,
    find_backups, find_incomplete,
)

EXPECTED_FOLDERS = ["test_data/documents", "backups"]
EXPECTED_FILES = ["backup.py", "restore.py", "integrity.py", "storage.py", "README.md"]


def check_project():
    """Проверяет, на месте ли все папки и файлы."""
    all_ok = True
    for folder in EXPECTED_FOLDERS:
        if (PROJECT_DIR / folder).is_dir():
            print(f"[OK] Папка найдена: {folder}")
        else:
            print(f"[ОШИБКА] Папка не найдена: {folder}")
            all_ok = False
    for file in EXPECTED_FILES:
        if (PROJECT_DIR / file).is_file():
            print(f"[OK] Файл найден: {file}")
        else:
            print(f"[ОШИБКА] Файл не найден: {file}")
            all_ok = False
    return all_ok


def run_backup():
    """Создаёт копию и честно сообщает результат."""
    print(f"Копируем: {DEFAULT_SOURCE}")
    try:
        target, files = create_backup(DEFAULT_SOURCE, BACKUPS_DIR)
    except KeyboardInterrupt:
        print("\n[ОШИБКА] Копирование прервано. Копия НЕ создана.")
        return False
    except Exception as error:
        print(f"[ОШИБКА] Копия НЕ создана: {error}")
        return False
    print(f"[OK] Копия создана: {target.name}")
    print(f"     Файлов скопировано: {files}")
    print("     Проверка SHA-256 пройдена, manifest.json записан.")
    return True


def run_list():
    """Показывает все копии: готовые и неполные."""
    backups = find_backups(BACKUPS_DIR)
    incomplete = find_incomplete(BACKUPS_DIR)

    if not backups and not incomplete:
        print("Копий пока нет.")
        return True

    for folder in backups:
        try:
            manifest = read_manifest(folder)
            created = manifest.get("created", "?").replace("T", " ")
            count = manifest.get("file_count", "?")
            print(f"{folder.name}   создана: {created}   файлов: {count}")
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
            print(f"{folder.name}   [нет читаемого manifest.json]")

    for folder in incomplete:
        print(f"{folder.name}   [НЕПОЛНАЯ копия, не использовать]")
    return True


def run_verify():
    """Проверяет все готовые копии."""
    backups = find_backups(BACKUPS_DIR)
    incomplete = find_incomplete(BACKUPS_DIR)

    if not backups and not incomplete:
        print("Копий пока нет.")
        return True

    all_ok = True
    for folder in backups:
        problems = verify_backup(folder)
        if problems:
            all_ok = False
            print(f"[ПОВРЕЖДЕНА] {folder.name}")
            for problem in problems:
                print(f"     - {problem}")
        else:
            print(f"[OK] {folder.name}")

    for folder in incomplete:
        all_ok = False
        print(f"[НЕПОЛНАЯ] {folder.name} (прерванное копирование)")
    return all_ok


def run_restore(what):
    """Восстанавливает выбранную копию в папку restored."""
    try:
        folder = choose_backup(BACKUPS_DIR, what)
        print(f"Выбрана копия: {folder.name}")
        target, files = restore_backup(folder, RESTORE_DIR)
    except KeyboardInterrupt:
        print("\n[ОШИБКА] Восстановление прервано.")
        return False
    except Exception as error:
        print(f"[ОШИБКА] Восстановление НЕ выполнено: {error}")
        return False
    print(f"[OK] Восстановлено в: {target}")
    print(f"     Файлов: {files}")
    print("     SHA-256 восстановленных файлов совпал с манифестом.")
    return True


def run_compare(first, second):
    """Сравнивает две папки по SHA-256."""
    first = Path(first)
    second = Path(second)
    for folder in (first, second):
        if not folder.is_dir():
            print(f"[ОШИБКА] Папка не найдена: {folder}")
            return False

    problems = compare_with_table(second, build_file_table(first))
    if problems:
        print("[РАЗЛИЧИЯ] Папки не совпадают:")
        for problem in problems:
            print(f"     - {problem}")
        return False
    print("[OK] Папки совпадают: все файлы и SHA-256 одинаковые.")
    return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    command = sys.argv[1]

    if command == "check":
        return 0 if check_project() else 1
    if command == "backup":
        return 0 if run_backup() else 1
    if command == "list":
        return 0 if run_list() else 1
    if command == "verify":
        return 0 if run_verify() else 1
    if command == "restore":
        if len(sys.argv) < 3:
            print("Укажите копию или дату. Пример: python main.py restore backup_2026-11-16_14-01-47")
            return 1
        return 0 if run_restore(sys.argv[2]) else 1
    if command == "compare":
        if len(sys.argv) < 4:
            print("Укажите две папки. Пример: python main.py compare test_data\\documents restored\\restored_backup_...")
            return 1
        return 0 if run_compare(sys.argv[2], sys.argv[3]) else 1

    print(f"Неизвестная команда: {command}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())