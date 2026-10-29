"""Parse commands and implement the first-stage shell stubs."""

import os
import re
import shlex
from dataclasses import dataclass
from typing import Mapping

from src.vfs import VFS, VFSError
from src.vfs_commands import inspect_vfs


VARIABLE = re.compile(
    r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))"
)
MAX_PATH_ARGUMENTS = 1


class CommandError(ValueError):
    """Indicate an invalid command or its arguments."""


@dataclass(frozen=True)
class Result:
    """Store command output and the requested exit state."""

    output: str = ""
    should_exit: bool = False


def expand_variables(text: str, environment: Mapping[str, str]) -> str:
    """Expand environment names; undefined variables become empty strings."""
    return VARIABLE.sub(
        lambda match: environment.get(match[1] or match[2], ""), text
    )


def parse_command(line: str, environment: Mapping[str, str]) -> list[str]:
    """Split quoted arguments, then expand environment variables in them."""
    try:
        tokens = shlex.split(line, comments=False, posix=True)
    except ValueError as error:
        raise CommandError(f"Ошибка ввода: {error}") from error
    return [expand_variables(token, environment) for token in tokens]


class Shell:
    """Dispatch commands without running any real operating-system commands."""

    def __init__(self, environment: Mapping[str, str] | None = None):
        """Use the real environment unless a test environment is supplied."""
        source = os.environ if environment is None else environment
        self.environment = dict(source)
        self.vfs: VFS | None = None

    def execute(self, line: str) -> Result:
        """Run an exit command or an ls/cd stub after validating arguments."""
        tokens = parse_command(line, self.environment)
        if not tokens:
            return Result()
        command, *arguments = tokens
        if command in {"vfs-info", "vfs-read"}:
            try:
                return Result(inspect_vfs(self.vfs, command, arguments))
            except VFSError as error:
                raise CommandError(str(error)) from error
        if command == "exit":
            if arguments:
                raise CommandError("Использование: exit")
            return Result("Завершение работы.", should_exit=True)
        if command not in {"ls", "cd"}:
            raise CommandError(f"Неизвестная команда: {command}")
        validate_path_arguments(command, arguments)
        return Result(f"Заглушка: {command}; аргументы: {arguments!r}")


def validate_path_arguments(command: str, arguments: list[str]) -> None:
    """Accept zero or one nonempty path and reject unsupported options."""
    if len(arguments) > MAX_PATH_ARGUMENTS:
        raise CommandError(f"Использование: {command} [путь]")
    if arguments and (not arguments[0] or arguments[0].startswith("-")):
        raise CommandError(f"Недопустимый аргумент команды {command}")
