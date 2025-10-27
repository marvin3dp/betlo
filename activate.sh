#!/bin/bash
# Quick activation script for Zefoy Bot venv
# Compatible with Linux and macOS

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
    echo "Python: $(which python)"
    echo "Version: $(python --version)"
    echo ""
    echo "📌 Next Steps:"
    echo ""
    echo " Option 1 - Run with auto-activation:"
    echo "    ./venv.sh"
    echo ""
    echo " Option 2 - Run manually:"
    echo "    python run.py"
    echo "    # or"
    echo "    python -m betlo"
    echo ""
    echo "💡 To deactivate: deactivate"
else
    echo "✗ Virtual environment not found!"
    echo ""
    echo "Please run installation first:"
    echo "  ./install.sh"
fi
