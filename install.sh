#!/bin/bash
# Installation script for Zefoy Bot with Python venv

# Check Python version
echo "🔍 Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Found Python $python_version"
else
    echo "✗ Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if Python 3.8+
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python version is compatible"
else
    echo "✗ Python 3.8 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

# Check if python3-venv is installed
echo ""
echo "🔍 Checking python3-venv..."
if python3 -m venv --help &> /dev/null; then
    echo "✓ python3-venv is installed"
else
    echo "✗ python3-venv is not installed!"
    echo ""
    echo "Install it with:"
    echo "Ubuntu/Debian: sudo apt install python3-venv"
    echo "Fedora: sudo dnf install python3-venv"
    echo "Arch: sudo pacman -S python-virtualenv"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists"
    read -p "Remove and recreate? [y/N]: " recreate_venv
    if [[ $recreate_venv =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
        echo "Creating new virtual environment..."
        python3 -m venv venv
        echo "✓ Virtual environment recreated"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs screenshots extensions

echo "✓ Directories created"

# Check for Chrome
echo ""
echo "🌐 Checking for Google Chrome..."
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "✓ Chrome/Chromium found"
else
    echo "⚠ Chrome/Chromium not found. Please install Google Chrome."
fi

# Check for Tesseract (optional)
echo ""
echo "🔍 Checking for Tesseract OCR (optional)..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract found: $tesseract_version"
else
    echo "⚠ Tesseract not found (optional for auto captcha solving)"
    echo "Install with: sudo apt-get install tesseract-ocr"
fi

# Make run.py executable
echo ""
echo "🔧 Setting permissions..."
chmod +x run.py
chmod +x install.sh

echo "✓ Permissions set"

# Create activation helper script
echo ""
echo "📝 Creating activation helper script..."
cat > activate.sh << 'ACTIVATE_EOF'
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
ACTIVATE_EOF

chmod +x activate.sh
echo "✓ Created activate.sh helper script"

# Installation complete
echo ""
echo "✓ Installation Complete!"
echo ""
echo "🚀 To start the bot:"
echo ""
echo "   1. Activate virtual environment:"
echo "      source venv/bin/activate"
echo "      OR"
echo "      source activate.sh"
echo ""
echo "   2. Run the bot:"
echo "      python run.py"
echo "      OR"
echo "      python -m betlo"
echo ""
echo "   3. To deactivate when done:"
echo "      deactivate"
echo ""
echo "📖 For more information, see README.md"
echo ""
echo "💡 Quick commands:"
echo "   source activate.sh    # Activate venv"
echo "   python run.py         # Run bot"
echo "   deactivate            # Deactivate venv"
echo ""
