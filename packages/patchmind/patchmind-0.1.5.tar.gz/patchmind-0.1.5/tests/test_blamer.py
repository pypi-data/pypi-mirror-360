"""Tests for PatchBlamer."""

import subprocess
import unittest
from unittest import mock

from core.blamer import PatchBlamer


class TestPatchBlamer(unittest.TestCase):
    """Ensure git blame output is parsed correctly."""

    @mock.patch("core.blamer.subprocess.run")
    def test_blame_parsing(self, mock_run: mock.Mock) -> None:
        output = (
            "abcd123 1 1 1\n"
            "author Alice\n"
            "filename foo.py\n"
            "\tprint('a')\n"
            "dcba321 2 2 1\n"
            "author Bob\n"
            "filename foo.py\n"
            "\tprint('b')\n"
        )
        mock_run.return_value = subprocess.CompletedProcess(["git"], 0, stdout=output, stderr="")
        result = PatchBlamer.blame("foo.py")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["author"], "Alice")
        self.assertEqual(result[1]["code_line"], "print('b')")

    @mock.patch("core.blamer.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    def test_blame_failure(self, mock_run: mock.Mock) -> None:
        with self.assertRaises(RuntimeError):
            PatchBlamer.blame("foo.py")


if __name__ == "__main__":
    unittest.main()
