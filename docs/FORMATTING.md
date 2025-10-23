# Code Formatting Guide

Complete guide for code formatting and quality standards.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Formatter Tools](#formatter-tools)
- [File-Specific Guidelines](#file-specific-guidelines)
- [Pre-commit Hooks](#pre-commit-hooks)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project uses automated code formatters to ensure consistent code style
across all files.

### Supported File Types

- ✅ **Python** (.py) - Black, isort, autopep8
- ✅ **Markdown** (.md) - Prettier
- ✅ **YAML** (.yaml, .yml) - Prettier
- ✅ **JSON** (.json) - Python json module
- ✅ **Shell** (.sh) - shfmt

---

## Quick Start

### Format All Files

```bash
# Make script executable
chmod +x format.sh

# Run formatter
./format.sh

# Run with linting
./format.sh --lint
```

### Format Specific File Types

```bash
# Python only
black --line-length 100 betlo/*.py
isort --profile black betlo/*.py

# Markdown only
prettier --write "**/*.md"

# YAML only
prettier --write "**/*.yaml" "**/*.yml"

# JSON only
python3 -m json.tool config.json > temp.json && mv temp.json config.json
```

---

## Formatter Tools

### Python Formatters

#### Black - Code Formatter

**Installation:**

```bash
pip install black
```

**Usage:**

```bash
black --line-length 100 betlo/
```

**Configuration:** `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
```

**Features:**

- Automatic code formatting
- PEP 8 compliant
- Deterministic (same input = same output)
- Opinionated (minimal configuration)

---

#### isort - Import Sorter

**Installation:**

```bash
pip install isort
```

**Usage:**

```bash
isort --profile black --line-length 100 betlo/
```

**Configuration:** `pyproject.toml`

```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
```

**Features:**

- Sorts imports alphabetically
- Groups imports by type (stdlib, third-party, local)
- Compatible with Black

---

#### autopep8 - PEP 8 Fixer

**Installation:**

```bash
pip install autopep8
```

**Usage:**

```bash
autopep8 --in-place --aggressive --aggressive --max-line-length 100 file.py
```

**Features:**

- Fixes PEP 8 violations
- Removes unused imports
- Fixes indentation

---

### Markdown Formatter

#### Prettier

**Installation:**

```bash
npm install -g prettier
```

**Usage:**

```bash
prettier --write "**/*.md"
```

**Configuration:** `.prettierrc`

```json
{
  "proseWrap": "always",
  "printWidth": 80
}
```

**Features:**

- Consistent formatting
- Line wrapping
- Table formatting
- List formatting

---

### YAML Formatter

**Installation:**

```bash
npm install -g prettier
```

**Usage:**

```bash
prettier --write "**/*.yaml" "**/*.yml"
```

**Features:**

- Consistent indentation (2 spaces)
- Quote normalization
- Key ordering (optional)

---

### JSON Formatter

**Built-in Python:**

```bash
python3 -m json.tool input.json > output.json
```

**Or with Prettier:**

```bash
prettier --write "**/*.json"
```

**Features:**

- 2-space indentation
- Sorted keys (optional)
- Trailing comma removal

---

### Shell Script Formatter

#### shfmt

**Installation:**

```bash
# macOS
brew install shfmt

# Linux
GO111MODULE=on go install mvdan.cc/sh/v3/cmd/shfmt@latest

# Or download binary from:
# https://github.com/mvdan/sh/releases
```

**Usage:**

```bash
shfmt -w -i 4 -bn -ci -sr script.sh
```

**Options:**

- `-w` - Write to file
- `-i 4` - Indent with 4 spaces
- `-bn` - Binary ops on next line
- `-ci` - Switch case indent
- `-sr` - Redirect operators followed by space

---

## File-Specific Guidelines

### Python Files

**Standards:**

- Line length: 100 characters
- Indentation: 4 spaces
- Imports: Sorted with isort
- Formatting: Black style
- Docstrings: Google style

**Example:**

```python
"""Module docstring.

This is a longer description.
"""

import os
import sys
from typing import List, Optional

from third_party import module

from local_module import utils


def function_name(param1: str, param2: int = 0) -> Optional[str]:
    """Function docstring.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    return None
```

---

### Markdown Files

**Standards:**

- Line length: 80 characters
- Headings: ATX style (#, ##, ###)
- Lists: Consistent symbols (-, \*, +)
- Code blocks: Fenced with language

**Example:**

````markdown
# Main Heading

## Subheading

This is a paragraph that wraps at 80 characters. It continues on the next line
when it exceeds the limit.

### Features

- First item
- Second item
  - Nested item
  - Another nested item

```python
def example():
    return "code"
```
````

````

---

### YAML Files

**Standards:**
- Indentation: 2 spaces
- Quotes: Use when necessary
- Lists: Dash notation
- Booleans: true/false (lowercase)

**Example:**
```yaml
# Comment
key: value
nested:
  key1: value1
  key2: value2

list:
  - item1
  - item2
  - item3

boolean: true
number: 42
string: "quoted when needed"
````

---

### JSON Files

**Standards:**

- Indentation: 2 spaces
- Quotes: Double quotes
- No trailing commas
- Keys alphabetically sorted (optional)

**Example:**

```json
{
  "key1": "value1",
  "key2": 42,
  "nested": {
    "inner": true
  },
  "list": ["item1", "item2"]
}
```

---

### Shell Scripts

**Standards:**

- Indentation: 4 spaces
- Shebang: `#!/bin/bash`
- Variables: `${VAR}` notation
- Functions: snake_case

**Example:**

```bash
#!/bin/bash

set -e

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function definition
function_name() {
    local param1="$1"
    local param2="${2:-default}"

    echo "Processing: ${param1}"
    return 0
}

# Main execution
main() {
    function_name "arg1" "arg2"
}

main "$@"
```

---

## Pre-commit Hooks

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Update hooks
pre-commit autoupdate
```

### Manual Run

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files file1.py file2.py

# Run specific hook
pre-commit run black --all-files
```

### Configuration

File: `.pre-commit-config.yaml`

Hooks automatically run before each commit and format/check:

- Trailing whitespace
- End of file
- YAML syntax
- JSON syntax
- Python formatting (Black, isort)
- Python linting (flake8)
- Shell formatting (shfmt)
- Markdown linting

### Skip Hooks

```bash
# Skip all hooks for one commit
git commit --no-verify

# Skip specific hook
SKIP=black git commit
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/format-check.yml`:

```yaml
name: Format Check

on: [push, pull_request]

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install formatters
        run: |
          pip install black isort autopep8

      - name: Check Python formatting
        run: |
          black --check --line-length 100 .
          isort --check --profile black .

      - name: Install Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install Prettier
        run: npm install -g prettier

      - name: Check Markdown/YAML formatting
        run: prettier --check "**/*.{md,yaml,yml,json}"
```

---

## Troubleshooting

### Black conflicts with other tools

**Solution:** Use Black-compatible profiles

```bash
isort --profile black
flake8 --extend-ignore=E203,W503
```

### Prettier not found

**Solution:** Install Node.js and Prettier

```bash
# macOS
brew install node
npm install -g prettier

# Ubuntu
sudo apt install nodejs npm
npm install -g prettier
```

### shfmt not found

**Solution:** Install shfmt

```bash
# macOS
brew install shfmt

# Linux - download from releases
wget https://github.com/mvdan/sh/releases/download/v3.8.0/shfmt_v3.8.0_linux_amd64
chmod +x shfmt_v3.8.0_linux_amd64
sudo mv shfmt_v3.8.0_linux_amd64 /usr/local/bin/shfmt
```

### Format script fails

**Solution:** Check permissions and dependencies

```bash
# Make executable
chmod +x format.sh

# Activate venv first
source venv/bin/activate

# Install dependencies
pip install black isort autopep8
```

### Pre-commit hook fails

**Solution:** Update and reinstall hooks

```bash
pre-commit clean
pre-commit uninstall
pre-commit install
pre-commit autoupdate
```

---

## Best Practices

### Before Committing

1. **Run formatter:**

   ```bash
   ./format.sh
   ```

2. **Review changes:**

   ```bash
   git diff
   ```

3. **Check for issues:**

   ```bash
   ./format.sh --lint
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Your message"
   ```

### Code Review

- ✅ All files formatted
- ✅ No linting errors
- ✅ Consistent style
- ✅ Readable code
- ✅ Proper documentation

### Continuous Improvement

- Keep formatters updated
- Review formatting rules periodically
- Discuss style changes with team
- Document exceptions

---

## Quick Reference

### Commands Cheat Sheet

```bash
# Format everything
./format.sh

# Python only
black . && isort .

# Markdown only
prettier --write "**/*.md"

# YAML only
prettier --write "**/*.{yaml,yml}"

# Check without changing
black --check .
prettier --check "**/*.md"

# Pre-commit
pre-commit run --all-files
```

### File Locations

- `format.sh` - Main formatter script
- `.editorconfig` - Editor configuration
- `.prettierrc` - Prettier configuration
- `.prettierignore` - Prettier ignore rules
- `pyproject.toml` - Python tool configuration
- `.pre-commit-config.yaml` - Pre-commit hooks

---

## Related Documentation

- [README.md](../README.md) - Main documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

**Last Updated:** October 23, 2025 **Version:** 2.2.0

**Happy Formatting! 🎨**
