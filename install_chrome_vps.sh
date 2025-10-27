#!/bin/bash
# Quick Chrome installation script for VPS/Server
# Specifically for fixing "Binary Location Must be a String" error

echo "🌐 Chrome Installation Script for VPS/Server"
echo ""

# Check if running on Linux
if [ "$(uname -s)" != "Linux" ]; then
    echo "✗ This script is for Linux VPS/servers only"
    exit 1
fi

# Check for Chrome
echo "🔍 Checking for existing Chrome installation..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✓ Chrome already installed: $CHROME_VERSION"
    echo ""
    read -p "Reinstall Chrome? [y/N]: " reinstall
    if [[ ! $reinstall =~ ^[Yy]$ ]]; then
        echo "Skipping Chrome installation"
        exit 0
    fi
elif command -v chromium &> /dev/null || command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version 2> /dev/null || chromium-browser --version 2> /dev/null)
    echo "✓ Chromium already installed: $CHROMIUM_VERSION"
    echo ""
    echo "Note: Chromium is already installed. Chrome is not required."
    read -p "Install Chrome anyway? [y/N]: " install_anyway
    if [[ ! $install_anyway =~ ^[Yy]$ ]]; then
        echo "Skipping Chrome installation"
        exit 0
    fi
else
    echo "✗ Chrome/Chromium not found - will install"
fi

echo ""
echo "📦 Installing Chrome dependencies..."
sudo apt update

# Install dependencies with fallback for newer Ubuntu/Debian versions
# Note: Some packages have different names in newer versions (t64 suffix)
sudo apt install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libgbm1 \
    xvfb \
    libappindicator3-1 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils || true

# Try to install packages that might have version-specific names
# These might fail on some systems, so we ignore errors (|| true)
sudo apt install -y \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 2> /dev/null \
    || sudo apt install -y \
        libatk-bridge2.0-0t64 \
        libgtk-3-0t64 \
        libasound2t64 2> /dev/null || true

echo "✓ Dependencies installed"

echo ""
echo "📥 Downloading Google Chrome..."
TEMP_DEB="/tmp/google-chrome-stable_current_amd64.deb"
wget -q --show-progress -O "$TEMP_DEB" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

if [ $? -ne 0 ]; then
    echo "✗ Failed to download Chrome"
    echo ""
    echo "Alternative: Install Chromium instead"
    echo "  sudo apt install chromium-browser"
    exit 1
fi

echo ""
echo "📦 Installing Google Chrome..."
sudo apt install -y "$TEMP_DEB"

if [ $? -eq 0 ]; then
    rm -f "$TEMP_DEB"
    echo ""
    echo "✓ Google Chrome installed successfully!"
    echo ""
    google-chrome --version
    echo ""
    echo "Chrome binary location:"
    which google-chrome
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "You can now run the bot with:"
    echo "  source venv/bin/activate"
    echo "  python run.py"
else
    echo "✗ Failed to install Chrome"
    echo ""
    echo "Try manual installation:"
    echo "  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
    echo "  sudo apt install ./google-chrome-stable_current_amd64.deb"
    echo ""
    echo "Or install Chromium as alternative:"
    echo "  sudo apt install chromium-browser"
    exit 1
fi

# Cleanup
rm -f "$TEMP_DEB" 2> /dev/null

echo ""
echo "💡 Tips for VPS:"
echo "  - Use headless mode: Set 'headless: true' in config.yaml"
echo "  - Chrome requires ~500MB RAM minimum"
echo "  - For very low RAM VPS, consider using chromium-browser instead"
