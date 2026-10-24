import os
import tempfile
import unittest

from resume_matcher.exceptions import FileValidationError
from resume_matcher.file_handler import (
    EmptyContentError,
    UnsupportedFileTypeError,
    collect_resume_files,
    read_file,
    validate_file_path,
)


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _write(self, name, content):
        path = os.path.join(self.tmp, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_read_valid_file(self):
        path = self._write("a.txt", "hello world")
        self.assertEqual(read_file(path), "hello world")

    def test_empty_file_raises(self):
        path = self._write("empty.txt", "")
        with self.assertRaises(EmptyContentError):
            read_file(path)

    def test_whitespace_only_raises(self):
        path = self._write("ws.txt", "   \n  ")
        with self.assertRaises(EmptyContentError):
            read_file(path)

    def test_missing_file_raises(self):
        with self.assertRaises(FileValidationError):
            read_file(os.path.join(self.tmp, "nope.txt"))

    def test_unsupported_extension(self):
        path = self._write("x.xyz", "content")
        with self.assertRaises(UnsupportedFileTypeError):
            read_file(path)

    def test_validate_ok(self):
        path = self._write("ok.txt", "content")
        self.assertTrue(validate_file_path(path).is_file())

    def test_collect_resume_files(self):
        self._write("r1.txt", "a")
        self._write("r2.md", "b")
        self._write("ignore.png", "c")
        files = collect_resume_files(self.tmp)
        self.assertEqual(len(files), 2)


if __name__ == "__main__":
    unittest.main()
