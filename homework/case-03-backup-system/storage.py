"""
storage.py - пути проекта, имена резервных копий и поиск копий на диске.
"""

from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

# Папка, которую мы копируем по умолчанию (только тестовые данные!)
DEFAULT_SOURCE = PROJECT_DIR / "test_data" / "documents"

# Папка, где хранятся все резервные копии
BACKUPS_DIR = PROJECT_DIR / "backups"

# Папка, куда восстанавливаем (отдельно от исходников и от копий)
RESTORE_DIR = PROJECT_DIR / "restored"

# Префиксы имён
BACKUP_PREFIX = "backup_"
TEMP_PREFIX = ".tmp_"


def make_backup_name():
    """Имя копии с текущей датой и временем. Пример: backup_2026-11-16_14-05-30"""
    return BACKUP_PREFIX + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def count_files(folder):
    """Считает файлы в папке (вместе с подпапками)."""
    return sum(1 for item in folder.rglob("*") if item.is_file())


def find_backups(backups_dir):
    """Возвращает список готовых копий (папки backup_...), от старых к новым."""
    backups_dir = Path(backups_dir)
    if not backups_dir.is_dir():
        return []
    return sorted(p for p in backups_dir.iterdir() if p.is_dir() and p.name.startswith(BACKUP_PREFIX))


def find_incomplete(backups_dir):
    """Возвращает список неполных копий (временные папки .tmp_...)."""
    backups_dir = Path(backups_dir)
    if not backups_dir.is_dir():
        return []
    return sorted(p for p in backups_dir.iterdir() if p.is_dir() and p.name.startswith(TEMP_PREFIX))
