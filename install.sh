#!/bin/bash
# Installation script for Zefoy Bot with Python venv
# Compatible with Linux and macOS
# Smart environment detection for Desktop vs VPS/Server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect operating system
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*) OS="Linux" ;;
    Darwin*) OS="macOS" ;;
    *) OS="Unknown" ;;
esac

# Smart environment detection
has_display() {
    # Check if DISPLAY is set
    if [ -n "$DISPLAY" ]; then
        return 0
    fi

    # Check if xset can query X server
    if command -v xset &> /dev/null; then
        if xset q &> /dev/null 2>&1; then
            return 0
        fi
    fi

    # Check if Xvfb is already running
    if pgrep -x "Xvfb" > /dev/null; then
        return 0
    fi

    return 1
}

# Detect environment
if has_display; then
    ENVIRONMENT="Desktop"
    IS_VPS=false
else
    ENVIRONMENT="VPS/Server"
    IS_VPS=true
fi

echo -e "${CYAN}🖥️  Detected OS: $OS${NC}"
echo -e "${CYAN}🌐 Environment: $ENVIRONMENT${NC}"
echo ""

# Check Python version
echo -e "${CYAN}🔍 Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "   Found Python ${GREEN}$python_version${NC}"
else
    echo -e "${RED}✗ Python 3 not found!${NC}"
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
    echo -e "${GREEN}✓ Python version is compatible${NC}"
else
    echo -e "${RED}✗ Python 3.8 or higher is required${NC}"
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
echo -e "${CYAN}📦 Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Remove and recreate? [y/N]: " recreate_venv
    if [[ $recreate_venv =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
        echo "Creating new virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}✗ Failed to create virtual environment${NC}"
            echo "Make sure python3-full is installed: sudo apt install python3-full"
            exit 1
        fi
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        echo "Make sure python3-full is installed: sudo apt install python3-full"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Verify venv was created properly
if [ ! -f "venv/bin/pip" ]; then
    echo -e "${RED}✗ Virtual environment appears incomplete (pip not found)${NC}"
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
echo -e "${GREEN}✓ Virtual environment verified${NC}"

# Install dependencies using venv pip directly
echo ""
echo -e "${CYAN}📦 Installing dependencies...${NC}"
echo "Using virtual environment pip..."

# Use venv pip directly to avoid externally-managed-environment issues
venv/bin/pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Failed to upgrade pip${NC}"
    exit 1
fi

venv/bin/pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Create necessary directories
echo ""
echo -e "${CYAN}📁 Creating directories...${NC}"
mkdir -p logs screenshots extensions

echo -e "${GREEN}✓ Directories created${NC}"

# Check for Chrome/Chromium
echo ""
echo -e "${CYAN}🌐 Checking for Google Chrome/Chromium...${NC}"

if [ "$OS" = "macOS" ]; then
    # macOS Chrome check
    if [ -d "/Applications/Google Chrome.app" ] || [ -d "$HOME/Applications/Google Chrome.app" ] || command -v chromium &> /dev/null; then
        echo -e "${GREEN}✓ Chrome/Chromium found${NC}"
    else
        echo -e "${YELLOW}⚠ Chrome/Chromium not found. Please install Google Chrome.${NC}"
        echo "macOS: brew install --cask google-chrome"
    fi
else
    # Linux - check existing installation
    CHROME_FOUND=false
    if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version 2> /dev/null || chromium --version 2> /dev/null || chromium-browser --version 2> /dev/null || echo "unknown")
        echo -e "${GREEN}✓ Chrome/Chromium found: $CHROME_VERSION${NC}"
        CHROME_FOUND=true
    else
        echo -e "${YELLOW}⚠ Chrome/Chromium not found!${NC}"
        echo ""
    fi

    # Auto-install Chrome for Linux (Ubuntu/Debian)
    if [ "$CHROME_FOUND" = false ] && command -v apt &> /dev/null; then
        echo -e "${CYAN}📦 Installing Google Chrome automatically...${NC}"
        echo ""

        # Install VPS-specific dependencies if detected as VPS
        if [ "$IS_VPS" = true ]; then
            echo -e "${CYAN}🖥️  VPS/Server detected - Installing additional dependencies...${NC}"

            # Install Xvfb for virtual display
            echo "Installing Xvfb (X Virtual Framebuffer)..."
            sudo apt install -y xvfb

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Xvfb installed successfully${NC}"
            else
                echo -e "${RED}✗ Failed to install Xvfb${NC}"
                echo "You may need to run in pure headless mode"
            fi
            echo ""
        fi

        # Install Chrome dependencies
        echo "Installing Chrome dependencies..."

        # Core dependencies
        sudo apt install -y \
            wget \
            ca-certificates \
            fonts-liberation \
            libnss3 \
            libxss1 \
            libgbm1 \
            libappindicator3-1 \
            libu2f-udev \
            libvulkan1 \
            xdg-utils || true

        # Install packages with version-specific fallback (t64 suffix for newer systems)
        sudo apt install -y \
            libatk-bridge2.0-0 \
            libgtk-3-0 \
            libasound2 2> /dev/null \
            || sudo apt install -y \
                libatk-bridge2.0-0t64 \
                libgtk-3-0t64 \
                libasound2t64 2> /dev/null || true

        echo -e "${GREEN}✓ Dependencies installed${NC}"
        echo ""

        # Download and install Chrome
        TEMP_DEB="/tmp/google-chrome-stable_current_amd64.deb"
        echo "📥 Downloading Google Chrome..."

        if wget -q --show-progress -O "$TEMP_DEB" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb; then
            echo ""
            echo "📦 Installing Google Chrome..."
            sudo apt install -y "$TEMP_DEB"

            if [ $? -eq 0 ]; then
                rm -f "$TEMP_DEB"
                echo ""
                echo -e "${GREEN}✓ Google Chrome installed successfully!${NC}"
                google-chrome --version
                echo ""
                echo "Chrome binary location: $(which google-chrome)"
            else
                echo -e "${RED}✗ Failed to install Chrome${NC}"
                echo ""
                echo "Try manual installation:"
                echo "  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
                echo "  sudo apt install ./google-chrome-stable_current_amd64.deb"
                echo ""
                echo "Or install Chromium as alternative:"
                echo "  sudo apt install chromium-browser"
            fi
        else
            echo -e "${RED}✗ Failed to download Chrome${NC}"
            echo ""
            echo "Alternative: Install Chromium instead"
            echo "  sudo apt install chromium-browser"
        fi

        # Cleanup
        rm -f "$TEMP_DEB" 2> /dev/null
    elif [ "$CHROME_FOUND" = false ]; then
        echo "Please install Google Chrome manually"
        echo ""
    fi

    # Check and install Xvfb for VPS even if Chrome is already installed
    if [ "$IS_VPS" = true ] && [ "$CHROME_FOUND" = true ]; then
        echo ""
        echo -e "${CYAN}🖥️  VPS/Server detected - Checking Xvfb...${NC}"

        if command -v Xvfb &> /dev/null; then
            echo -e "${GREEN}✓ Xvfb already installed${NC}"
        else
            echo -e "${YELLOW}⚠ Xvfb not found - Installing...${NC}"
            if command -v apt &> /dev/null; then
                sudo apt install -y xvfb
                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}✓ Xvfb installed successfully${NC}"
                else
                    echo -e "${RED}✗ Failed to install Xvfb${NC}"
                fi
            fi
        fi
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
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo ""

# Environment-specific instructions
if [ "$IS_VPS" = true ]; then
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🖥️  VPS/SERVER INSTALLATION COMPLETE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  No display detected - VPS mode configured${NC}"
    echo ""
    echo -e "${GREEN}🚀 Quick Start (Recommended):${NC}"
    echo -e "   ${CYAN}./venv.sh${NC}  ${GREEN}# Smart auto-detect & run${NC}"
    echo ""
    echo -e "${GREEN}📖 Manual Options:${NC}"
    echo ""
    echo -e "  ${CYAN}Option 1: Xvfb Mode (Recommended for Zefoy)${NC}"
    echo "    ./run_xvfb.sh"
    echo ""
    echo -e "  ${CYAN}Option 2: Pure Headless Mode${NC}"
    echo "    source venv/bin/activate"
    echo "    python run.py"
    echo ""
    echo -e "${YELLOW}💡 Tips for VPS:${NC}"
    echo "  • Xvfb provides better compatibility with Zefoy"
    echo "  • Ensure /dev/shm has at least 500MB (check_vps.sh)"
    echo "  • Run ./check_vps.sh to verify environment"
    echo ""
else
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🖥️  DESKTOP INSTALLATION COMPLETE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}🚀 Quick Start (Recommended):${NC}"
    echo -e "   ${CYAN}./venv.sh${NC}  ${GREEN}# Smart auto-detect & run${NC}"
    echo ""
    echo -e "${GREEN}📖 Manual Options:${NC}"
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
fi

echo -e "${CYAN}📖 Documentation:${NC}"
echo "   README.md              # Main documentation"
echo "   docs/VPS_SETUP.md      # VPS-specific guide"
echo "   docs/DISPLAY_MODES.md  # Display mode comparison"
echo ""
echo -e "${CYAN}💡 Quick commands:${NC}"
echo "   ./venv.sh             # Smart auto-run (recommended)"
echo "   ./check_vps.sh        # Check VPS environment"
echo "   source activate.sh    # Activate venv only"
echo ""
