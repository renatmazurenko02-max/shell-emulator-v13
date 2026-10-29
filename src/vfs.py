"""Load ZIP contents into a memory-only virtual filesystem."""

import base64
from pathlib import Path, PurePosixPath
import zipfile


class VFSError(ValueError):
    """Report an invalid archive or virtual path."""


def archive_path(name: str) -> str:
    """Validate archive names and return an absolute virtual path."""
    parts = name.rstrip("/").split("/")
    if (not name or name.startswith("/") or "\\" in name
            or any(part in {"", ".", ".."} for part in parts)
            or ":" in parts[0]):
        raise VFSError(f"Недопустимый путь в ZIP: {name}")
    return "/" + "/".join(parts)


class VFS:
    """Keep directories and base64-encoded file contents in memory."""

    def __init__(self):
        """Create an empty virtual root."""
        self.directories = {"/"}
        self.files: dict[str, str] = {}

    @classmethod
    def load(cls, path: Path) -> "VFS":
        """Read a ZIP without extracting or changing it on disk."""
        vfs = cls()
        try:
            with zipfile.ZipFile(path, "r") as archive:
                for entry in archive.infolist():
                    name = archive_path(entry.filename)
                    if entry.is_dir():
                        vfs.add_directory(name)
                    else:
                        vfs.add_file(name, archive.read(entry))
        except (OSError, zipfile.BadZipFile, RuntimeError,
                NotImplementedError) as error:
            raise VFSError(f"Не удалось загрузить ZIP: {error}") from error
        return vfs

    def add_directory(self, path: str) -> None:
        """Register a directory and all parents, checking file conflicts."""
        chain = [PurePosixPath(path), *PurePosixPath(path).parents]
        for directory in chain:
            name = str(directory)
            if name in self.files:
                raise VFSError(f"Файл используется как папка: {name}")
            self.directories.add(name)

    def add_file(self, path: str, data: bytes) -> None:
        """Store all bytes as base64, preserving empty and binary files."""
        if path in self.files or path in self.directories:
            raise VFSError(f"Повторяющийся путь: {path}")
        self.add_directory(str(PurePosixPath(path).parent))
        self.files[path] = base64.b64encode(data).decode("ascii")

    def read(self, path: str) -> bytes:
        """Read a virtual file using only the in-memory representation."""
        normalized = "/" + path.lstrip("/")
        if normalized not in self.files:
            raise VFSError(f"Файл VFS не найден: {path}")
        return base64.b64decode(self.files[normalized])

    def describe(self) -> str:
        """Show the loaded hierarchy for stage-three diagnostics."""
        count = len(self.directories)
        lines = [f"VFS: файлов {len(self.files)}, папок {count}"]
        lines.extend(f"DIR  {name}" for name in sorted(self.directories))
        lines.extend(f"FILE {name}" for name in sorted(self.files))
        return "\n".join(lines)
