"""Verify ZIP import, binary preservation, and diagnostic commands."""

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

from src.shell import CommandError, Shell
from src.vfs import VFS, VFSError, archive_path


class VFSTests(unittest.TestCase):
    """Check actual archive bytes while isolating each test directory."""

    def setUp(self):
        """Create a temporary archive location."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = self.root / "vfs.zip"

    def archive(self, entries):
        """Write test entries and return the archive path."""
        with zipfile.ZipFile(self.path, "w") as archive:
            for name, data in entries.items():
                archive.writestr(name, data)
        return self.path

    def test_memory_and_binary(self):
        """Import without extraction and keep data after deleting the source."""
        data = bytes(range(256))
        self.archive({"a/b/c/data.bin": data, "empty.txt": b"", "folder/": b""})
        before = self.path.read_bytes()
        with patch.object(zipfile.ZipFile, "extractall") as extract:
            vfs = VFS.load(self.path)
            extract.assert_not_called()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.root.iterdir()), [self.path])
        self.path.unlink()
        self.assertEqual(vfs.read("/a/b/c/data.bin"), data)
        self.assertEqual(vfs.read("empty.txt"), b"")
        self.assertIn("/a/b/c", vfs.directories)
        self.assertIn("/folder", vfs.directories)

    def test_empty_archive(self):
        """An empty ZIP contains only the virtual root."""
        vfs = VFS.load(self.archive({}))
        self.assertEqual(vfs.directories, {"/"})
        self.assertEqual(vfs.files, {})

    def test_invalid_archives(self):
        """Report missing and corrupt archives."""
        with self.assertRaises(VFSError):
            VFS.load(self.path)
        self.path.write_bytes(b"broken")
        with self.assertRaises(VFSError):
            VFS.load(self.path)

    def test_invalid_names_and_conflicts(self):
        """Reject traversal, absolute paths, and file-directory conflicts."""
        with self.assertRaises(VFSError):
            archive_path("a\\b")
        for name in ("../x", "/x", "C:/x", "a/./b"):
            with self.subTest(name=name), self.assertRaises(VFSError):
                VFS.load(self.archive({name: b"x"}))
        with self.assertRaises(VFSError):
            VFS.load(self.archive({"a": b"file", "a/b": b"child"}))

    def test_commands(self):
        """Expose memory diagnostics and report invalid virtual reads."""
        shell = Shell({})
        with self.assertRaises(CommandError):
            shell.execute("vfs-info")
        shell.vfs = VFS.load(self.archive({"readme.txt": b"Hi"}))
        self.assertIn("/readme.txt", shell.execute("vfs-info").output)
        self.assertIn("SGk=", shell.execute("vfs-read /readme.txt").output)
        for line in ("vfs-info x", "vfs-read", "vfs-read /missing"):
            with self.subTest(line=line), self.assertRaises(CommandError):
                shell.execute(line)


if __name__ == "__main__":
    unittest.main()
