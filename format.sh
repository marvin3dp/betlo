#!/bin/bash

# =============================================================================
# Format All Files Before Git Push
# Formats Python, Markdown, YAML, Shell, JSON files
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╭─────────────────────────────────────────────────────╮${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}│          🎨 Code Formatter & Linter 🎨              │${NC}"
echo -e "${BLUE}│                                                     │${NC}"
echo -e "${BLUE}╰─────────────────────────────────────────────────────╯${NC}"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo -e "${YELLOW}   Activating venv...${NC}"
    source venv/bin/activate
fi

# Install formatters if not present
install_formatters() {
    echo -e "${BLUE}📦 Checking formatters...${NC}"

    # Python formatters
    if ! command -v black &> /dev/null; then
        echo -e "${YELLOW}   Installing black...${NC}"
        pip install black --quiet
    fi

    if ! command -v isort &> /dev/null; then
        echo -e "${YELLOW}   Installing isort...${NC}"
        pip install isort --quiet
    fi

    if ! command -v autopep8 &> /dev/null; then
        echo -e "${YELLOW}   Installing autopep8...${NC}"
        pip install autopep8 --quiet
    fi

    # Check for prettier (Node.js)
    if ! command -v prettier &> /dev/null; then
        echo -e "${YELLOW}   ⚠️  Prettier not found (for Markdown/YAML/JSON)${NC}"
        echo -e "${YELLOW}      Install with: npm install -g prettier${NC}"
        echo -e "${YELLOW}      Skipping Markdown/YAML/JSON formatting...${NC}"
        SKIP_PRETTIER=true
    else
        SKIP_PRETTIER=false
    fi

    echo -e "${GREEN}✅ Formatters ready!${NC}"
    echo ""
}

# Format Python files
format_python() {
    echo -e "${BLUE}🐍 Formatting Python files...${NC}"

    # Find all Python files
    python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "*/__pycache__/*")

    if [ -z "$python_files" ]; then
        echo -e "${YELLOW}   No Python files found${NC}"
        return
    fi

    file_count=$(echo "$python_files" | wc -l)
    echo -e "${BLUE}   Found $file_count Python file(s)${NC}"

    # Format with black
    echo -e "${BLUE}   Running black...${NC}"
    black --quiet --line-length 100 $python_files 2> /dev/null || true

    # Sort imports with isort
    echo -e "${BLUE}   Running isort...${NC}"
    isort --quiet --profile black --line-length 100 $python_files 2> /dev/null || true

    # Fix PEP8 issues with autopep8
    echo -e "${BLUE}   Running autopep8...${NC}"
    for file in $python_files; do
        autopep8 --in-place --aggressive --aggressive --max-line-length 100 "$file" 2> /dev/null || true
    done

    echo -e "${GREEN}   ✅ Python files formatted!${NC}"
    echo ""
}

# Format Markdown files
format_markdown() {
    if [ "$SKIP_PRETTIER" = true ]; then
        return
    fi

    echo -e "${BLUE}📝 Formatting Markdown files...${NC}"

    # Find all Markdown files
    md_files=$(find . -name "*.md" -not -path "./venv/*" -not -path "./.git/*")

    if [ -z "$md_files" ]; then
        echo -e "${YELLOW}   No Markdown files found${NC}"
        return
    fi

    file_count=$(echo "$md_files" | wc -l)
    echo -e "${BLUE}   Found $file_count Markdown file(s)${NC}"

    # Format with prettier
    echo -e "${BLUE}   Running prettier...${NC}"
    prettier --write --prose-wrap always --print-width 80 $md_files 2> /dev/null || true

    echo -e "${GREEN}   ✅ Markdown files formatted!${NC}"
    echo ""
}

# Format YAML files
format_yaml() {
    if [ "$SKIP_PRETTIER" = true ]; then
        return
    fi

    echo -e "${BLUE}📋 Formatting YAML files...${NC}"

    # Find all YAML files
    yaml_files=$(find . \( -name "*.yaml" -o -name "*.yml" \) -not -path "./venv/*" -not -path "./.git/*")

    if [ -z "$yaml_files" ]; then
        echo -e "${YELLOW}   No YAML files found${NC}"
        return
    fi

    file_count=$(echo "$yaml_files" | wc -l)
    echo -e "${BLUE}   Found $file_count YAML file(s)${NC}"

    # Format with prettier
    echo -e "${BLUE}   Running prettier...${NC}"
    prettier --write $yaml_files 2> /dev/null || true

    echo -e "${GREEN}   ✅ YAML files formatted!${NC}"
    echo ""
}

# Format JSON files
format_json() {
    echo -e "${BLUE}🗂️  Formatting JSON files...${NC}"

    # Find all JSON files
    json_files=$(find . -name "*.json" -not -path "./venv/*" -not -path "./.git/*" -not -path "*/node_modules/*")

    if [ -z "$json_files" ]; then
        echo -e "${YELLOW}   No JSON files found${NC}"
        return
    fi

    file_count=$(echo "$json_files" | wc -l)
    echo -e "${BLUE}   Found $file_count JSON file(s)${NC}"

    # Format with Python json module (built-in)
    echo -e "${BLUE}   Formatting with Python...${NC}"
    for file in $json_files; do
        python3 -c "import json; f=open('$file'); data=json.load(f); f.close(); f=open('$file','w'); json.dump(data,f,indent=2); f.close()" 2> /dev/null || true
    done

    echo -e "${GREEN}   ✅ JSON files formatted!${NC}"
    echo ""
}

# Format Shell scripts
format_shell() {
    echo -e "${BLUE}🐚 Checking Shell scripts...${NC}"

    # Find all shell scripts
    shell_files=$(find . \( -name "*.sh" -o -name "*.bash" \) -not -path "./venv/*" -not -path "./.git/*")

    if [ -z "$shell_files" ]; then
        echo -e "${YELLOW}   No Shell scripts found${NC}"
        return
    fi

    file_count=$(echo "$shell_files" | wc -l)
    echo -e "${BLUE}   Found $file_count Shell script(s)${NC}"

    # Check if shfmt is available
    if command -v shfmt &> /dev/null; then
        echo -e "${BLUE}   Running shfmt...${NC}"
        shfmt -w -i 4 -bn -ci -sr $shell_files 2> /dev/null || true
        echo -e "${GREEN}   ✅ Shell scripts formatted!${NC}"
    else
        echo -e "${YELLOW}   ⚠️  shfmt not found${NC}"
        echo -e "${YELLOW}      Install with: brew install shfmt (macOS) or from https://github.com/mvdan/sh${NC}"
        echo -e "${YELLOW}      Checking syntax only...${NC}"

        # At least check syntax
        for file in $shell_files; do
            bash -n "$file" 2> /dev/null && echo -e "${GREEN}      ✓ $file${NC}" || echo -e "${RED}      ✗ $file (syntax error)${NC}"
        done
    fi

    echo ""
}

# Check for common issues
check_issues() {
    echo -e "${BLUE}🔍 Checking for common issues...${NC}"

    # Check for trailing whitespace
    echo -e "${BLUE}   Checking trailing whitespace...${NC}"
    files_with_trailing=$(find . \( -name "*.py" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" \) -not -path "./venv/*" -not -path "./.git/*" -exec grep -l " $" {} \; 2> /dev/null || true)

    if [ -n "$files_with_trailing" ]; then
        echo -e "${YELLOW}   ⚠️  Files with trailing whitespace found${NC}"
        # Remove trailing whitespace
        for file in $files_with_trailing; do
            sed -i 's/[[:space:]]*$//' "$file"
        done
        echo -e "${GREEN}   ✅ Trailing whitespace removed${NC}"
    else
        echo -e "${GREEN}   ✅ No trailing whitespace${NC}"
    fi

    # Check for tabs (should use spaces)
    echo -e "${BLUE}   Checking for tabs...${NC}"
    files_with_tabs=$(find . \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" \) -not -path "./venv/*" -not -path "./.git/*" -exec grep -l $'\t' {} \; 2> /dev/null || true)

    if [ -n "$files_with_tabs" ]; then
        echo -e "${YELLOW}   ⚠️  Files with tabs found (prefer spaces)${NC}"
        echo "$files_with_tabs"
    else
        echo -e "${GREEN}   ✅ No tabs found${NC}"
    fi

    # Check for mixed line endings
    echo -e "${BLUE}   Checking line endings...${NC}"
    files_with_crlf=$(find . \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) -not -path "./venv/*" -not -path "./.git/*" -exec file {} \; | grep CRLF | cut -d: -f1 || true)

    if [ -n "$files_with_crlf" ]; then
        echo -e "${YELLOW}   ⚠️  Files with CRLF line endings found${NC}"
        # Convert to LF
        for file in $files_with_crlf; do
            dos2unix "$file" 2> /dev/null || sed -i 's/\r$//' "$file"
        done
        echo -e "${GREEN}   ✅ Converted to LF line endings${NC}"
    else
        echo -e "${GREEN}   ✅ Line endings OK${NC}"
    fi

    echo ""
}

# Run linters
run_linters() {
    echo -e "${BLUE}🔬 Running linters...${NC}"

    # Pylint for Python (if available)
    if command -v pylint &> /dev/null; then
        echo -e "${BLUE}   Running pylint...${NC}"
        python_files=$(find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" -not -path "*/__pycache__/*")
        if [ -n "$python_files" ]; then
            pylint --disable=all --enable=E,F $python_files 2> /dev/null || echo -e "${YELLOW}      ⚠️  Some issues found (see above)${NC}"
        fi
    fi

    echo -e "${GREEN}   ✅ Linting complete${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}Starting formatting process...${NC}"
    echo ""

    install_formatters
    format_python
    format_markdown
    format_yaml
    format_json
    format_shell
    check_issues

    # Optional: run linters
    if [[ "$1" == "--lint" ]]; then
        run_linters
    fi

    echo -e "${GREEN}╭─────────────────────────────────────────────────────╮${NC}"
    echo -e "${GREEN}│                                                     │${NC}"
    echo -e "${GREEN}│              ✅ Formatting Complete! ✅             │${NC}"
    echo -e "${GREEN}│                                                     │${NC}"
    echo -e "${GREEN}│   All files are now formatted and ready to push!    │${NC}"
    echo -e "${GREEN}│                                                     │${NC}"
    echo -e "${GREEN}╰─────────────────────────────────────────────────────╯${NC}"
    echo ""
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo -e "${BLUE}   1. Review changes: git diff${NC}"
    echo -e "${BLUE}   2. Stage changes: git add .${NC}"
    echo -e "${BLUE}   3. Commit: git commit -m \"Format all files\"${NC}"
    echo -e "${BLUE}   4. Push: git push${NC}"
    echo ""
}

# Run with --lint flag to also run linters
main "$@"
