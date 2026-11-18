"""
restore.py - выбор копии по дате и восстановление в отдельную папку.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from integrity import MANIFEST_NAME, read_manifest, verify_backup, compare_with_table
from storage import BACKUP_PREFIX, TEMP_PREFIX, find_backups, count_files


def parse_when(text):
    """Превращает текст в дату и время. Если указана только дата, берём конец этого дня."""
    text = text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            moment = datetime.strptime(text, fmt)
        except ValueError:
            continue
        if fmt == "%Y-%m-%d":
            moment = moment.replace(hour=23, minute=59, second=59)
        elif fmt == "%Y-%m-%d %H:%M":
            moment = moment.replace(second=59)
        return moment
    raise ValueError(
        f"Не понимаю дату: {text!r}. Примеры: 2026-11-16 или 2026-11-16 14:01 или 2026-11-16 14:01:47"
    )


def choose_backup(backups_dir, what):
    """Выбирает копию: по точному имени или по дате (самая свежая не позже указанного момента)."""
    backups_dir = Path(backups_dir)

    # Вариант 1: указано имя копии
    if what.startswith(BACKUP_PREFIX):
        folder = backups_dir / what
        if not folder.is_dir():
            raise FileNotFoundError(f"Копия не найдена: {what}")
        return folder

    # Вариант 2: указана дата
    moment = parse_when(what)
    best_folder = None
    best_time = None
    for folder in find_backups(backups_dir):
        try:
            created = datetime.fromisoformat(read_manifest(folder)["created"])
        except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
            continue  # копия без читаемого манифеста для выбора по дате не годится
        if created <= moment and (best_time is None or created > best_time):
            best_folder = folder
            best_time = created

    if best_folder is None:
        raise LookupError(f"Нет копий, созданных не позже {moment:%Y-%m-%d %H:%M:%S}.")
    return best_folder


def restore_backup(backup_folder, restore_root):
    """Восстанавливает копию в restore_root. Возвращает (путь, количество_файлов)."""
    backup_folder = Path(backup_folder).resolve()
    restore_root = Path(restore_root).resolve()

    # Шаг 1: убеждаемся, что сама копия целая
    problems = verify_backup(backup_folder)
    if problems:
        raise RuntimeError("Копия повреждена, восстановление отменено: " + "; ".join(problems))

    manifest = read_manifest(backup_folder)

    # Шаг 2: готовим пути (существующее никогда не перезаписываем)
    restore_root.mkdir(exist_ok=True)
    final_path = restore_root / ("restored_" + backup_folder.name)
    temp_path = restore_root / (TEMP_PREFIX + final_path.name)

    if final_path.exists() or temp_path.exists():
        raise FileExistsError(
            f"Папка уже существует: {final_path.name}. Удалите её или выберите другую копию."
        )

    # Шаг 3: копируем во временную папку (без manifest.json) и сверяем с манифестом
    try:
        shutil.copytree(backup_folder, temp_path, ignore=shutil.ignore_patterns(MANIFEST_NAME))
        problems = compare_with_table(temp_path, manifest["files"])
        if problems:
            raise RuntimeError("Восстановленные файлы не прошли проверку SHA-256: " + "; ".join(problems))
        temp_path.rename(final_path)
    except BaseException:
        # Убираем только свою временную папку, чтобы не оставлять мусор
        shutil.rmtree(temp_path, ignore_errors=True)
        raise

    return final_path, count_files(final_path)
