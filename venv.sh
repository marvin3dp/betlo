#!/bin/bash
# Run Zefoy Bot with automatic venv activation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "✗ Virtual environment not found!"
    echo ""
    echo "Run installation first:"
    echo "./install.sh"
    exit 1
fi

# Activate venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if activation successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo "✗ Failed to activate virtual environment!"
    exit 1
fi

echo "✓ Virtual environment activated"
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo ""

# Run the bot
echo "🚀 Starting Zefoy Bot..."
echo ""

python run.py

# Deactivate on exit
echo ""
echo "🔄 Deactivating virtual environment..."
deactivate
echo "✓ Done"
