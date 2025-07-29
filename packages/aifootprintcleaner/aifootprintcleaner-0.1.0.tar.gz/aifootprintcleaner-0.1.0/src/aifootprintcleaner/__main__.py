import sys
import os
import argparse
from .cleaner import clean_directory

def parse_args():
    """
    Parse command-line arguments for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description='Remove non-printable and AI-artifact characters from source code files.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Directory to clean recursively (default: current directory)'
    )
    parser.add_argument(
        '--include',
        nargs='*',
        help='Extra file extensions to include (e.g. .md .yaml)'
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        help='File extensions to exclude from cleaning (e.g. .log .txt)'
    )
    return parser.parse_args()

def main():
    """
    Entry point for CLI usage.
    """
    args = parse_args()
    target_dir = args.path
    extra_exts = set(args.include or [])
    exclude_exts = set(args.exclude or [])

    if not os.path.isdir(target_dir):
        print(f"[ERROR] {target_dir} is not a valid directory.")
        sys.exit(1)

    print(f"[INFO] Cleaning directory: {target_dir}")
    clean_directory(
        target_dir,
        extra_extensions=extra_exts,
        exclude_extensions=exclude_exts
    )

if __name__ == "__main__":
    main()
