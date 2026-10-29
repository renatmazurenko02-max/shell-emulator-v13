"""Read command-line configuration without opening a window."""

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Store physical paths supplied at application startup."""

    vfs: Path
    startup: Path | None


def parse_config(arguments: list[str] | None = None) -> Config:
    """Parse optional VFS and startup-script paths relative to the cwd."""
    parser = argparse.ArgumentParser(description="Shell emulator, variant 13")
    parser.add_argument(
        "--vfs", type=Path, default=Path("demo-vfs.zip"),
        help="Path to VFS ZIP (loading is implemented in stage 3)",
    )
    parser.add_argument(
        "--startup", type=Path, help="Path to a UTF-8 startup script",
    )
    options = parser.parse_args(arguments)
    startup = options.startup.resolve() if options.startup else None
    return Config(options.vfs.resolve(), startup)
