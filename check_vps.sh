#!/bin/bash
# VPS Environment Check Script
# Checks if VPS is ready to run the bot

echo "🔍 VPS Environment Check"
echo ""

ALL_OK=true

# Check 1: Chrome/Chromium
echo "1️⃣  Checking Chrome/Chromium..."
if command -v google-chrome &> /dev/null; then
    VERSION=$(google-chrome --version)
    echo "   ✓ $VERSION"
elif command -v chromium &> /dev/null || command -v chromium-browser &> /dev/null; then
    VERSION=$(chromium --version 2> /dev/null || chromium-browser --version 2> /dev/null)
    echo "   ✓ $VERSION"
else
    echo "   ✗ Chrome/Chromium not found!"
    echo "     Install: ./install.sh (auto-installs Chrome + dependencies)"
    ALL_OK=false
fi
echo ""

# Check 2: Python version
echo "2️⃣  Checking Python..."
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version)
    echo "   ✓ $VERSION"
else
    echo "   ✗ Python 3 not found!"
    ALL_OK=false
fi
echo ""

# Check 3: Virtual environment
echo "3️⃣  Checking virtual environment..."
if [ -d "venv" ]; then
    if [ -f "venv/bin/python" ] && [ -f "venv/bin/pip" ]; then
        echo "   ✓ Virtual environment exists and is valid"
    else
        echo "   ⚠ Virtual environment incomplete"
        echo "     Recreate: rm -rf venv && ./install.sh"
        ALL_OK=false
    fi
else
    echo "   ✗ Virtual environment not found"
    echo "     Create: ./install.sh"
    ALL_OK=false
fi
echo ""

# Check 4: RAM
echo "4️⃣  Checking RAM..."
if command -v free &> /dev/null; then
    TOTAL_RAM=$(free -m | awk 'NR==2 {print $2}')
    AVAILABLE_RAM=$(free -m | awk 'NR==2 {print $7}')
    echo "   Total: ${TOTAL_RAM}MB | Available: ${AVAILABLE_RAM}MB"

    if [ "$TOTAL_RAM" -lt 2048 ]; then
        echo "   ⚠ Warning: Less than 2GB RAM (${TOTAL_RAM}MB)"
        echo "     Bot may crash. Consider:"
        echo "     - Set disable_images: true in config.yaml"
        echo "     - Set single_process: true in config.yaml (less stable)"
    else
        echo "   ✓ RAM is sufficient"
    fi
fi
echo ""

# Check 5: /dev/shm size
echo "5️⃣  Checking /dev/shm..."
if [ -d "/dev/shm" ]; then
    SHM_INFO=$(df -h /dev/shm | tail -n 1)
    SHM_SIZE=$(echo "$SHM_INFO" | awk '{print $2}')
    echo "   Size: $SHM_SIZE"

    # Convert to MB for comparison
    SHM_SIZE_NUM=$(echo "$SHM_SIZE" | sed 's/[^0-9]//g')
    SHM_UNIT=$(echo "$SHM_SIZE" | sed 's/[0-9.]//g')

    if [[ "$SHM_UNIT" == "M" && "$SHM_SIZE_NUM" -lt 64 ]] || [[ "$SHM_UNIT" == "K" ]]; then
        echo "   ✗ /dev/shm too small (< 64MB)!"
        echo "     Increase: sudo mount -o remount,size=256M /dev/shm"
        ALL_OK=false
    else
        echo "   ✓ /dev/shm size is adequate"
    fi
else
    echo "   ⚠ /dev/shm not found (unusual)"
fi
echo ""

# Check 6: Storage
echo "6️⃣  Checking disk space..."
AVAILABLE_GB=$(df -BG . | tail -n 1 | awk '{print $4}' | sed 's/G//')
echo "   Available: ${AVAILABLE_GB}GB"
if [ "$AVAILABLE_GB" -lt 5 ]; then
    echo "   ⚠ Warning: Less than 5GB free"
    ALL_OK=false
else
    echo "   ✓ Disk space is sufficient"
fi
echo ""

# Check 7: Config headless mode
echo "7️⃣  Checking config.yaml..."
if [ -f "config.yaml" ]; then
    HEADLESS=$(grep -A1 "^browser:" config.yaml | grep "headless:" | awk '{print $2}')
    if [ "$HEADLESS" == "true" ]; then
        echo "   ✓ Headless mode: enabled (good for VPS)"
    else
        echo "   ⚠ Headless mode: disabled in config"
        echo "     Note: Bot will auto-enable headless if no display detected"
        echo "     Recommended: Set headless: true in config.yaml"
    fi
else
    echo "   ✗ config.yaml not found"
    ALL_OK=false
fi
echo ""

# Check 8: Zombie Chrome processes
echo "8️⃣  Checking for zombie Chrome processes..."
CHROME_COUNT=$(ps aux | grep -i chrome | grep -v grep | wc -l)
if [ "$CHROME_COUNT" -gt 0 ]; then
    echo "   ⚠ Warning: $CHROME_COUNT Chrome process(es) running"
    echo "     Kill them: pkill -9 -f chrome"
else
    echo "   ✓ No zombie Chrome processes"
fi
echo ""

# Check 9: Python packages
echo "9️⃣  Checking Python packages..."
if [ -d "venv" ]; then
    source venv/bin/activate 2> /dev/null

    MISSING_PACKAGES=()

    for package in selenium undetected-chromedriver pytesseract; do
        if ! venv/bin/pip list 2> /dev/null | grep -qi "$package"; then
            MISSING_PACKAGES+=("$package")
        fi
    done

    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        echo "   ✓ All required packages installed"
    else
        echo "   ✗ Missing packages: ${MISSING_PACKAGES[*]}"
        echo "     Install: source venv/bin/activate && pip install -r requirements.txt"
        ALL_OK=false
    fi

    deactivate 2> /dev/null
fi
echo ""

# Summary
echo ""
if [ "$ALL_OK" = true ]; then
    echo "✅ All checks passed! VPS is ready to run the bot."
    echo ""
    echo "🚀 Run the bot:"
    echo "   source venv/bin/activate"
    echo "   python run.py"
else
    echo "⚠️  Some issues found. Please fix them before running the bot."
    echo ""
    echo "💡 Quick fixes:"
    echo "   1. Run smart installer: ./install.sh (auto-detects & installs everything)"
    echo "   2. Check VPS guide: docs/VPS_SETUP.md"
    echo "   3. Run with Xvfb: ./run_xvfb.sh"
    echo "   4. Or enable headless: Edit config.yaml, set headless: true"
fi
echo ""
