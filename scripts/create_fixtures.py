"""Generate reproducible ZIP fixtures; never extract them."""

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def make_zip(name: str, entries: dict[str, bytes]) -> None:
    """Write generated test data into a ZIP excluded from Git."""
    with zipfile.ZipFile(ROOT / "generated" / name, "w") as archive:
        for path, data in entries.items():
            archive.writestr(path, data)


def main() -> None:
    """Create minimal, mixed, deeply nested, and invalid samples."""
    (ROOT / "generated").mkdir(exist_ok=True)
    make_zip("minimal.zip", {"readme.txt": b"Hello VFS\n"})
    make_zip("vfs with spaces.zip", {"readme.txt": b"Hello VFS\n"})
    make_zip("multiple.zip", {
        "readme.txt": b"Hello VFS\n", "empty.txt": b"",
        "data.bin": bytes([0, 255, 128, 10]),
        "my notes.txt": b"Notes\n", "empty-directory/": b"",
    })
    make_zip("deep.zip", {
        "readme.txt": b"Hello VFS\n",
        "level1/a.txt": b"A", "level1/level2/b.txt": b"B",
        "level1/level2/level3/c.txt": b"C",
    })
    make_zip("unsafe.zip", {"../outside.txt": b"invalid"})
    (ROOT / "generated" / "broken.zip").write_bytes(b"not a ZIP")
    print("Created VFS fixtures in generated/")


if __name__ == "__main__":
    main()
