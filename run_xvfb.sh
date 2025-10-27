#!/bin/bash
# Run bot with Xvfb (Virtual Display)
# Better compatibility than pure headless for Zefoy

echo "🖥️  Starting Bot with Xvfb (Virtual Display)"
echo ""

# Check if Xvfb is installed
if ! command -v Xvfb &> /dev/null; then
    echo "❌ Xvfb not installed!"
    echo ""
    echo "Installing Xvfb..."
    sudo apt update
    sudo apt install -y xvfb

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Xvfb"
        echo "Please install manually: sudo apt install xvfb"
        exit 1
    fi

    echo "✓ Xvfb installed successfully"
    echo ""
fi

# Check if bot directory
if [ ! -f "run.py" ]; then
    echo "❌ Error: run.py not found"
    echo "Please run this script from the bot directory"
    exit 1
fi

# Activate venv if exists
if [ -d "venv" ]; then
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate
    echo "✓ Virtual environment activated"
    echo ""
else
    echo "⚠️  Warning: Virtual environment not found"
    echo "Run ./install.sh first"
    exit 1
fi

# Set display for Xvfb
export DISPLAY=:99

# Kill any existing Xvfb on display :99
pkill -f "Xvfb :99" 2> /dev/null

echo "🚀 Starting Xvfb virtual display..."
# Suppress xkbcomp warnings (they are harmless)
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset 2> /dev/null &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Check if Xvfb is running
if ps -p $XVFB_PID > /dev/null; then
    echo "✓ Xvfb running on display :99"
    echo "  (Note: Any xkbcomp warnings are harmless and suppressed)"
else
    echo "❌ Failed to start Xvfb"
    exit 1
fi

echo ""
echo "🤖 Starting bot with virtual display..."
echo ""
echo ""

# Note: Set headless=false in config for Xvfb mode
# Xvfb provides virtual display so browser runs in "visible" mode
# but without actual GUI window

# Check config headless setting
HEADLESS=$(grep -A1 "^browser:" config.yaml | grep "headless:" | awk '{print $2}')
if [ "$HEADLESS" == "true" ]; then
    echo "⚠️  Note: config.yaml has headless: true"
    echo "For best results with Xvfb, set headless: false"
    echo "Xvfb provides virtual display, so browser can run in visible mode"
    echo ""
fi

# Run bot
python run.py

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $XVFB_PID 2> /dev/null
echo "✓ Xvfb stopped"
echo ""
echo "Bot session ended."
