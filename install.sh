#!/bin/bash
# Installation script for Zefoy Bot with Python venv
# Compatible with Linux and macOS

# Detect operating system
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*) OS="Linux" ;;
    Darwin*) OS="macOS" ;;
    *) OS="Unknown" ;;
esac

echo "🖥️  Detected OS: $OS"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "Found Python $python_version"
else
    echo "✗ Python 3 not found!"
    echo "Please install Python 3.8 or higher"
    if [ "$OS" = "macOS" ]; then
        echo "macOS: brew install python3"
    else
        echo "Linux: sudo apt install python3 (Ubuntu/Debian)"
    fi
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

# Check for missing packages on Ubuntu/Debian
if [ "$OS" = "Linux" ] && command -v apt &> /dev/null; then
    MISSING_PACKAGES=""
    APT_UPDATED=false

    # Check python3-venv
    echo ""
    echo "🔍 Checking python3-venv..."
    if python3 -m venv --help &> /dev/null; then
        echo "✓ python3-venv is installed"
    else
        echo "✗ python3-venv is not installed!"
        MISSING_PACKAGES="$MISSING_PACKAGES python3-venv"
    fi

    # Check python3-full (required for Python 3.12+)
    echo ""
    echo "🔍 Checking python3-full (required for Python 3.12+)..."
    if command -v dpkg &> /dev/null && dpkg -l | grep -q "python3-full"; then
        echo "✓ python3-full is installed"
    else
        echo "✗ python3-full is not installed!"
        MISSING_PACKAGES="$MISSING_PACKAGES python3-full"
    fi

    # Install missing packages
    if [ -n "$MISSING_PACKAGES" ]; then
        echo ""
        echo "📦 Installing missing packages:$MISSING_PACKAGES"
        echo "Running: sudo apt update && sudo apt install$MISSING_PACKAGES -y"
        echo ""

        sudo apt update && sudo apt install$MISSING_PACKAGES -y

        if [ $? -eq 0 ]; then
            echo "✓ All packages installed successfully"
        else
            echo "✗ Failed to install packages"
            echo "Please try manually: sudo apt install$MISSING_PACKAGES"
            exit 1
        fi
    fi
elif [ "$OS" = "macOS" ]; then
    # Check python3-venv on macOS
    echo ""
    echo "🔍 Checking python3-venv..."
    if python3 -m venv --help &> /dev/null; then
        echo "✓ python3-venv is installed"
    else
        echo "✗ python3-venv is not installed!"
        echo "macOS: brew install python3 (includes venv)"
        exit 1
    fi
else
    # Other Linux distros
    echo ""
    echo "🔍 Checking python3-venv..."
    if python3 -m venv --help &> /dev/null; then
        echo "✓ python3-venv is installed"
    else
        echo "✗ python3-venv is not installed!"
        echo ""
        echo "Install it with:"
        echo "Fedora: sudo dnf install python3-venv"
        echo "Arch: sudo pacman -S python-virtualenv"
        exit 1
    fi
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
        if [ $? -ne 0 ]; then
            echo "✗ Failed to create virtual environment"
            echo "Make sure python3-full is installed: sudo apt install python3-full"
            exit 1
        fi
        echo "✓ Virtual environment recreated"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "✗ Failed to create virtual environment"
        echo "Make sure python3-full is installed: sudo apt install python3-full"
        exit 1
    fi
    echo "✓ Virtual environment created"
fi

# Verify venv was created properly
if [ ! -f "venv/bin/pip" ]; then
    echo "✗ Virtual environment appears incomplete (pip not found)"
    echo "This usually means python3-full is not installed."
    echo ""
    echo "Please run:"
    echo "  sudo apt install python3-full"
    echo ""
    echo "Then delete the venv directory and run this script again:"
    echo "  rm -rf venv"
    echo "  ./install.sh"
    exit 1
fi
echo "✓ Virtual environment verified"

# Install dependencies using venv pip directly
echo ""
echo "📦 Installing dependencies..."
echo "Using virtual environment pip..."

# Use venv pip directly to avoid externally-managed-environment issues
venv/bin/pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo "✗ Failed to upgrade pip"
    exit 1
fi

venv/bin/pip install -r requirements.txt

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
if [ "$OS" = "macOS" ]; then
    if [ -d "/Applications/Google Chrome.app" ] || [ -d "$HOME/Applications/Google Chrome.app" ] || command -v chromium &> /dev/null; then
        echo "✓ Chrome/Chromium found"
    else
        echo "⚠ Chrome/Chromium not found. Please install Google Chrome."
        echo "macOS: brew install --cask google-chrome"
    fi
else
    if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
        echo "✓ Chrome/Chromium found"
    else
        echo "⚠ Chrome/Chromium not found. Please install Google Chrome."
        echo "Ubuntu/Debian: wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo apt install ./google-chrome-stable_current_amd64.deb"
    fi
fi

# Check for Tesseract (optional)
echo ""
echo "🔍 Checking for Tesseract OCR (optional)..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version 2>&1 | head -n1)
    echo "✓ Tesseract found: $tesseract_version"
else
    echo "⚠ Tesseract not found (optional for auto captcha solving)"
    if [ "$OS" = "macOS" ]; then
        echo "Install with: brew install tesseract"
    else
        echo "Install with: sudo apt-get install tesseract-ocr"
    fi
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
