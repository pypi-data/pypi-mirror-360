import tempfile
import os
from aifootprintcleaner.cleaner import clean_directory

def write_dirty_file(path):
    dirty = "code = 42\ufeff\u200b\u200c\u200d\u2060\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(dirty)

def read_cleaned(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def test_include_argument_allows_custom_extension():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'custom.foo')
        write_dirty_file(filepath)

        clean_directory(tmpdir, extra_extensions={'.foo'})
        result = read_cleaned(filepath)

        assert result == "code = 42\n"

def test_exclude_argument_skips_extension():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'script.py')
        write_dirty_file(filepath)

        # .py is normally included, but we exclude it
        clean_directory(tmpdir, exclude_extensions={'.py'})
        result = read_cleaned(filepath)

        # It should not be cleaned
        assert result != "code = 42\n"
