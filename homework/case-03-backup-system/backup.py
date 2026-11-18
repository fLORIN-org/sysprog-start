"""
backup.py - создание резервной копии папки.
Копия сначала создаётся во временной папке и получает настоящее имя
только после успешной проверки SHA-256.
"""

import shutil
from pathlib import Path

from storage import make_backup_name, count_files, TEMP_PREFIX
from integrity import build_file_table, compare_with_table, write_manifest


def create_backup(source, backups_dir):
    """Создаёт копию. Возвращает (путь_к_копии, количество_файлов).
    При любой проблеме (в том числе при Ctrl+C) выбрасывает ошибку,
    а настоящая папка backup_... не появляется.
    """
    source = Path(source).resolve()
    backups_dir = Path(backups_dir).resolve()

    if not source.is_dir():
        raise FileNotFoundError(f"Исходная папка не найдена: {source}")

    if source == backups_dir or source in backups_dir.parents or backups_dir in source.parents:
        raise ValueError("Папка копий и исходная папка не должны лежать одна внутри другой.")

    backups_dir.mkdir(exist_ok=True)

    final_name = make_backup_name()
    final_path = backups_dir / final_name
    temp_path = backups_dir / (TEMP_PREFIX + final_name)

    if final_path.exists() or temp_path.exists():
        raise FileExistsError(f"Копия с таким именем уже есть: {final_name}. Подождите секунду и повторите.")

    # 1. Хеши исходных файлов (исходники только читаем)
    file_table = build_file_table(source)

    # 2. Копируем во временную папку
    shutil.copytree(source, temp_path)

    # 3. Сверяем копию с исходниками
    problems = compare_with_table(temp_path, file_table)
    if problems:
        raise RuntimeError("Копия не прошла проверку SHA-256: " + "; ".join(problems))

    # 4. Записываем манифест
    write_manifest(temp_path, file_table, source)

    # 5. Последний шаг: переименование. Только теперь копия считается готовой.
    temp_path.rename(final_path)

    return final_path, count_files(final_path) - 1  # минус manifest.json
