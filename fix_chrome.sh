#!/bin/bash

# This script helps kill zombie Chrome/ChromeDriver processes
# Compatible with Linux and macOS

echo "🔧 Chrome Fix..."
echo ""

# Detect operating system
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*) OS="Linux" ;;
    Darwin*) OS="macOS" ;;
    *) OS="Unknown" ;;
esac

echo "🖥️  Detected OS: $OS"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Kill zombie Chrome processes
echo "Step 1: Killing zombie Chrome/ChromeDriver processes..."

if [ "$OS" = "macOS" ]; then
    # macOS uses different process names and pkill syntax
    pkill -9 "Google Chrome" 2> /dev/null
    pkill -9 "Chromium" 2> /dev/null
    pkill -9 "chromedriver" 2> /dev/null
    # Also kill using killall as backup
    killall -9 "Google Chrome" 2> /dev/null
    killall -9 "Chromium" 2> /dev/null
    killall -9 "chromedriver" 2> /dev/null
else
    # Linux process names
    pkill -9 "google-chrome" 2> /dev/null
    pkill -9 "chrome-browser" 2> /dev/null
    pkill -9 "chromium" 2> /dev/null
    pkill -9 "chromium-browser" 2> /dev/null
    pkill -9 "chromedriver" 2> /dev/null
fi

sleep 1
echo -e "${GREEN}✓${NC} Zombie processes killed"
echo ""

# Step 2: Clean Chrome temporary files
echo "Step 2: Cleaning Chrome temporary files..."

if [ "$OS" = "macOS" ]; then
    # macOS Chrome paths
    rm -rf ~/Library/Application\ Support/Google/Chrome/Singleton* 2> /dev/null
    rm -rf ~/Library/Application\ Support/Chromium/Singleton* 2> /dev/null
    rm -rf /tmp/.com.google.Chrome.* 2> /dev/null
    rm -rf /tmp/.org.chromium.Chromium.* 2> /dev/null
    rm -rf /private/tmp/.com.google.Chrome.* 2> /dev/null
    rm -rf /private/tmp/.org.chromium.Chromium.* 2> /dev/null
else
    # Linux Chrome paths
    rm -rf ~/.config/google-chrome/Singleton* 2> /dev/null
    rm -rf ~/.config/chromium/Singleton* 2> /dev/null
    rm -rf /tmp/.com.google.Chrome.* 2> /dev/null
    rm -rf /tmp/.org.chromium.Chromium.* 2> /dev/null
fi

echo -e "${GREEN}✓${NC} Temporary files cleaned"
echo ""

# Step 3: Update undetected-chromedriver (if in virtual environment)
echo "Step 3: Checking undetected-chromedriver..."

# Check if we're in a virtual environment
if [ -f "venv/bin/activate" ] || [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment detected, updating undetected-chromedriver..."
    if [ -f "venv/bin/pip" ]; then
        venv/bin/pip install --upgrade undetected-chromedriver 2> /dev/null
        echo -e "${GREEN}✓${NC} undetected-chromedriver updated"
    elif [ -n "$VIRTUAL_ENV" ]; then
        pip install --upgrade undetected-chromedriver 2> /dev/null
        echo -e "${GREEN}✓${NC} undetected-chromedriver updated"
    fi
else
    echo "No virtual environment detected, skipping undetected-chromedriver update"
    echo -e "${YELLOW}Note:${NC} If you're using a virtual environment, activate it first:"
    echo "  source venv/bin/activate"
    echo "  pip install --upgrade undetected-chromedriver"
fi
echo ""

echo -e "${GREEN}✓${NC} Chrome fix script completed!"
echo ""

if [ "$OS" = "macOS" ]; then
    echo -e "${YELLOW}Note:${NC} On macOS, if Chrome is still running, you may need to force quit from Activity Monitor"
fi
echo ""
