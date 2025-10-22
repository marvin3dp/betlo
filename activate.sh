#!/bin/bash
# Quick activation script for Zefoy Bot venv

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
    echo "Python: $(which python)"
    echo "Version: $(python --version)"
    echo ""
    echo "To deactivate: deactivate"
else
    echo "✗ Virtual environment not found!"
    echo "Run: ./install.sh"
fi
