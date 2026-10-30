"""Provide diagnostic access without implementing stage-four commands."""

import base64

from src.vfs import VFS, VFSError


REQUIRED_READ_ARGUMENTS = 1


def inspect_vfs(vfs: VFS | None, command: str, args: list[str]) -> str:
    """Handle hierarchy and base64 read diagnostics."""
    if vfs is None:
        raise VFSError("VFS не загружена")
    if command == "vfs-info":
        if args:
            raise VFSError("Использование: vfs-info")
        return vfs.describe()
    if len(args) != REQUIRED_READ_ARGUMENTS or not args[0]:
        raise VFSError("Использование: vfs-read путь")
    data = vfs.read(args[0])
    encoded = base64.b64encode(data).decode("ascii")
    return f"Размер: {len(data)} байт; base64: {encoded}"
