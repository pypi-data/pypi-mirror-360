import unicodedata
import re
import os

SUPPORTED_EXTENSIONS = (
    '.py', '.pyw', '.ipynb',
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp',
    '.cs', '.go', '.java', '.kt', '.kts',
    '.js', '.ts', '.jsx', '.tsx',
    '.rb', '.php', '.rs', '.swift',
    '.sh', '.bash', '.zsh', '.fish',
    '.lua', '.pl', '.r', '.m',
    '.html', '.htm', '.xml', '.xhtml',
    '.css', '.scss', '.sass',
    '.md', '.markdown',
    '.json', '.yaml', '.yml', '.toml', '.ini', '.txt',
    '.env', '.cfg', '.conf', '.config',
    '.dockerfile', '.make', '.txt', '.csv', '.tsv', '.log',
)

SPECIAL_FILES = {'Dockerfile', 'Makefile', 'CMakeLists.txt'}

def clean_file(file_path: str) -> bool:
    """
    Clean the file and overwrite it if changes were made.
    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        content = original_content.replace('\ufeff', '')
        content = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', content)
        content = ''.join(
            c for c in content
            if unicodedata.category(c)[0] != 'C' or c in '\n\t'
        )
        content = ''.join(
            c for c in content
            if (32 <= ord(c) <= 126) or c in '\n\t'
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[CLEANED] {file_path}")
            return True
        else:
            print(f"[UNCHANGED] {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] Could not clean {file_path}: {e}")
        return False

def clean_directory(base_path: str, extra_extensions=None, exclude_extensions=None):
    """
    Clean all supported files under base_path recursively.
    Prints detailed report about files found, cleaned, and unchanged.
    """
    all_extensions = set(SUPPORTED_EXTENSIONS)
    if extra_extensions:
        all_extensions.update(extra_extensions)
    if exclude_extensions:
        all_extensions.difference_update(exclude_extensions)

    total_files_found = 0
    total_files_cleaned = 0
    total_files_unchanged = 0

    for root, _, files in os.walk(base_path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in all_extensions or filename in SPECIAL_FILES:
                total_files_found += 1
                file_path = os.path.join(root, filename)
                cleaned = clean_file(file_path)
                if cleaned:
                    total_files_cleaned += 1
                else:
                    total_files_unchanged += 1

    print("========================================")
    print(f"[SUMMARY] Files found: {total_files_found}")
    print(f"[SUMMARY] Files cleaned: {total_files_cleaned}")
    print(f"[SUMMARY] Files unchanged: {total_files_unchanged}")
    print("========================================")
