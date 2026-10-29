"""Execute a startup script with a visible transcript and fail-fast behavior."""

from collections.abc import Callable
from pathlib import Path

from src.shell import CommandError, Shell


def run_startup(
    path: Path, shell: Shell, write: Callable[[str], None]
) -> bool:
    """Run UTF-8 lines until the first error or exit; return the exit flag."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as error:
        write(f"Ошибка чтения стартового скрипта {path}: {error}")
        return False
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        write(f"shell> {line}")
        try:
            result = shell.execute(line)
        except CommandError as error:
            write(f"Ошибка скрипта {path.name}, строка {number}: {error}")
            write("Стартовый скрипт остановлен. Доступен ручной ввод.")
            return False
        if result.output:
            write(result.output)
        if result.should_exit:
            return True
    write("Стартовый скрипт выполнен.")
    return False
