"""Test configuration and startup execution without a graphical display."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from src.config import parse_config
from src.shell import Shell
from src.startup import run_startup


class ConfigTests(unittest.TestCase):
    """Check defaults, independent options, and invalid command lines."""

    def test_defaults(self):
        """A default VFS name is available without a startup script."""
        config = parse_config([])
        self.assertEqual(config.vfs.name, "minimal.zip")
        self.assertIsNone(config.startup)

    def test_paths(self):
        """Both paths are retained and resolved, including embedded spaces."""
        config = parse_config([
            "--vfs", "some folder/test.zip", "--startup", "start.txt",
        ])
        self.assertEqual(config.vfs, Path("some folder/test.zip").resolve())
        self.assertEqual(config.startup, Path("start.txt").resolve())

    def test_single_options(self):
        """Either setting can be supplied independently."""
        self.assertIsNone(parse_config(["--vfs", "a.zip"]).startup)
        self.assertEqual(
            parse_config(["--startup", "a.txt"]).vfs.name, "minimal.zip"
        )

    def test_invalid_options(self):
        """Unknown flags and missing values produce parser errors."""
        for args in (["--unknown"], ["--vfs"], ["--startup"]):
            with self.subTest(args=args):
                self.check_invalid(args)

    def check_invalid(self, args):
        """Check an invalid invocation while suppressing usage output."""
        with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    parse_config(args)
                self.assertEqual(result.exception.code, 2)


class StartupTests(unittest.TestCase):
    """Verify transcript order, failure stopping, and exit behavior."""

    def setUp(self):
        """Prepare a temporary script and deterministic shell environment."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "start.txt"
        self.shell = Shell({"HOME": "/home/student"})
        self.output = []

    def run_script(self, content):
        """Write a script and collect its complete transcript."""
        self.path.write_text(content, encoding="utf-8-sig")
        return run_startup(self.path, self.shell, self.output.append)

    def test_success(self):
        """Echo commands, expand variables, skip blanks, and report success."""
        self.assertFalse(self.run_script('\nls\ncd "$HOME"\n'))
        self.assertEqual(self.output[0], "shell> ls")
        self.assertIn("/home/student", self.output[3])
        self.assertIn("выполнен", self.output[-1])

    def test_stop_on_first_error(self):
        """Do not execute or echo any line after the first error."""
        for bad in ("unknown", "ls a b", 'ls "', "exit now"):
            with self.subTest(bad=bad):
                self.output.clear()
                self.assertFalse(self.run_script(f"ls\n{bad}\ncd /after"))
                transcript = "\n".join(self.output)
                self.assertIn("строка 2", transcript)
                self.assertNotIn("/after", transcript)

    def test_exit(self):
        """Stop at exit and request closing the GUI."""
        self.assertTrue(self.run_script("exit\nls /after"))
        self.assertNotIn("/after", "\n".join(self.output))

    def test_missing_file(self):
        """Report file errors instead of raising them to the GUI."""
        self.assertFalse(
            run_startup(self.path, self.shell, self.output.append)
        )
        self.assertIn("Ошибка чтения", self.output[0])

    def test_invalid_encoding(self):
        """Report scripts that cannot be decoded as UTF-8."""
        self.path.write_bytes(b"\xff\xfe\xff")
        self.assertFalse(
            run_startup(self.path, self.shell, self.output.append)
        )
        self.assertIn("Ошибка чтения", self.output[0])


if __name__ == "__main__":
    unittest.main()
