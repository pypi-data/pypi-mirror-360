# AIFootPrintCleaner

**AIFootPrintCleaner** is a lightweight CLI tool that removes invisible Unicode characters, control codes, and non-printable artifacts commonly introduced by AI assistants like ChatGPT, Copilot, and others.

> Works recursively over any directory and supports `.py`, `.js`, `.cpp`, `.html`, and other source code formats.

## Features

- Removes zero-width and invisible Unicode characters (`\u200b`, `\ufeff`, etc.)
- Cleans non-printable control characters from source files
- CLI usage: `aifoodprintcleaner [directory]`
- Safe overwriting of source files

## Quickstart

```bash
pip install aifoodprintcleaner
aifoodprintcleaner src/
```

## Run Tests
```bash
pytest -s .
```

## License
MIT License
