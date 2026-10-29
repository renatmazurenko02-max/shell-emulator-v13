"""Verify stage-one parsing, stubs, errors, and exit behavior."""

import unittest

from src.shell import CommandError, Shell, parse_command


class ShellTests(unittest.TestCase):
    """Exercise the command engine independently of the GUI."""

    def setUp(self):
        """Create a deterministic environment for every test."""
        self.environment = {
            "HOME": "/home/student", "USERPROFILE": "C:/User Name"
        }
        self.shell = Shell(self.environment)

    def test_empty_input(self):
        """Blank input must not fail or request exit."""
        result = self.shell.execute("   ")
        self.assertEqual(result.output, "")
        self.assertFalse(result.should_exit)

    def test_stubs(self):
        """Both commands report their names and arguments."""
        for command in ("ls", "cd"):
            with self.subTest(command=command):
                self.assertIn(command, self.shell.execute(command).output)
                result = self.shell.execute(command + " /docs")
                self.assertIn("/docs", result.output)

    def test_environment(self):
        """Support both variable forms and preserve spaces in values."""
        self.assertEqual(
            parse_command("ls ${HOME}", self.environment),
            ["ls", "/home/student"],
        )
        self.assertEqual(
            parse_command("cd $USERPROFILE", self.environment),
            ["cd", "C:/User Name"],
        )

    def test_quoted_argument(self):
        """A quoted path with spaces remains a single argument."""
        self.assertEqual(
            parse_command('cd "my documents"', self.environment),
            ["cd", "my documents"],
        )

    def test_errors(self):
        """Reject unknown commands, bad arguments, and unfinished quotes."""
        invalid = (
            "unknown", "ls a b", "cd -x", "exit now", 'ls "', "cd $MISSING"
        )
        for line in invalid:
            with self.subTest(line=line):
                with self.assertRaises(CommandError):
                    self.shell.execute(line)

    def test_exit(self):
        """Exit sets the flag consumed by the window."""
        self.assertTrue(self.shell.execute("exit").should_exit)


if __name__ == "__main__":
    unittest.main()
