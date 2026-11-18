"""
integrity.py - проверка целостности файлов через SHA-256 и манифест.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

MANIFEST_NAME = "manifest.json"


def sha256_of_file(path):
    """Считает SHA-256 файла. Читаем кусками, чтобы большие файлы не забивали память."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)  # по 1 МБ
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def build_file_table(folder):
    """Возвращает словарь {относительный_путь: {size, sha256}} для всех файлов папки.
    Сам файл manifest.json в список не попадает.
    """
    folder = Path(folder)
    table = {}
    for item in sorted(folder.rglob("*")):
        if item.is_file() and item.name != MANIFEST_NAME:
            relative = item.relative_to(folder).as_posix()
            table[relative] = {
                "size": item.stat().st_size,
                "sha256": sha256_of_file(item),
            }
    return table


def write_manifest(folder, file_table, source):
    """Записывает manifest.json в папку копии."""
    manifest = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "source": str(source),
        "file_count": len(file_table),
        "files": file_table,
    }
    path = Path(folder) / MANIFEST_NAME
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def read_manifest(folder):
    """Читает manifest.json. Если файла нет или он испорчен, выбросит ошибку."""
    path = Path(folder) / MANIFEST_NAME
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_with_table(folder, expected_table):
    """Сравнивает папку с ожидаемой таблицей файлов. Возвращает список проблем (пустой = всё хорошо)."""
    folder = Path(folder)
    problems = []

    for relative, info in expected_table.items():
        file_path = folder / relative
        if not file_path.is_file():
            problems.append(f"файл отсутствует: {relative}")
            continue
        if file_path.stat().st_size != info["size"]:
            problems.append(f"размер не совпадает: {relative}")
            continue
        if sha256_of_file(file_path) != info["sha256"]:
            problems.append(f"SHA-256 не совпадает (файл изменён): {relative}")

    # Лишние файлы, которых нет в манифесте
    actual = build_file_table(folder)
    for relative in actual:
        if relative not in expected_table:
            problems.append(f"лишний файл, которого нет в манифесте: {relative}")

    return problems


def verify_backup(folder):
    """Полная проверка одной копии. Возвращает список проблем (пустой = копия целая)."""
    folder = Path(folder)
    try:
        manifest = read_manifest(folder)
    except FileNotFoundError:
        return ["нет файла manifest.json (копия неполная или старого формата)"]
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ["manifest.json повреждён"]

    if "files" not in manifest:
        return ["manifest.json имеет неверный формат"]

    return compare_with_table(folder, manifest["files"])
