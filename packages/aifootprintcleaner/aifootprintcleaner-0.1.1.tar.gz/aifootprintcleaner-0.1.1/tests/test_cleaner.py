import tempfile
import os
from aifootprintcleaner.cleaner import clean_file

def test_remove_invisible_characters():
    # BOM format
    dirty_text = "print('Hello')\ufeff\u200b\u200c\u200d\u2060\n"

    with tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8') as tmp:
        tmp.write(dirty_text)
        tmp_path = tmp.name

    clean_file(tmp_path)

    with open(tmp_path, 'r', encoding='utf-8') as f:
        cleaned = f.read()

    os.remove(tmp_path)

    # only the line
    assert cleaned == "print('Hello')\n"

def test_keep_valid_code():
    clean_code = "def foo():\n\tprint('bar')\n"

    with tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8') as tmp:
        tmp.write(clean_code)
        tmp_path = tmp.name

    clean_file(tmp_path)

    with open(tmp_path, 'r', encoding='utf-8') as f:
        cleaned = f.read()

    os.remove(tmp_path)

    # equal code
    assert cleaned == clean_code
