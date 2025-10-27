#!/bin/bash
# Run Betlo Bot with automatic environment detection
# Automatically chooses best mode: Xvfb (VPS) or Visible (Desktop)

# Detect operating system
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
    Linux*) OS="Linux" ;;
    Darwin*) OS="macOS" ;;
    *) OS="Unknown" ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo ""
    echo "Run installation first:"
    echo "./install.sh"
    exit 1
fi

# Function to check if display is available
has_display() {
    # Check DISPLAY variable
    if [ -n "$DISPLAY" ]; then
        return 0  # Has display
    fi

    # Try xset command (Linux/macOS)
    if command -v xset &> /dev/null; then
        if xset q &> /dev/null; then
            return 0  # Has display
        fi
    fi

    # Check if Xvfb is running
    if pgrep -x "Xvfb" > /dev/null; then
        return 0  # Xvfb running
    fi

    return 1  # No display
}

# Activate venv
echo -e "${CYAN}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if activation successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}✗ Failed to activate virtual environment!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo "Python: $(which python)"
echo "Version: $(python --version)"
echo ""

# Auto-detect environment and choose best mode
echo -e "${CYAN}🔍 Detecting environment...${NC}"

if has_display; then
    # Desktop/Laptop or Xvfb already running
    echo -e "${GREEN}✓ Display detected${NC}"

    if [ -n "$DISPLAY" ] && [[ "$DISPLAY" == *":99"* || "$DISPLAY" == *":98"* ]]; then
        echo -e "${BLUE}ℹ️  Xvfb virtual display detected${NC}"
    else
        echo -e "${BLUE}ℹ️  Real display detected (Desktop/Laptop)${NC}"
    fi

    echo ""
    echo -e "${CYAN}🚀 Starting bot in visible mode...${NC}"
    echo ""

    # Run normal bot
    python run.py

else
    # VPS/Server without display
    echo -e "${YELLOW}⚠️  No display detected (VPS/Server environment)${NC}"
    echo ""
    echo -e "${YELLOW}📊 Environment: VPS/Headless Server${NC}"
    echo -e "${YELLOW}🎯 Best Mode: Xvfb (95%+ success rate)${NC}"
    echo ""

    # Check if Xvfb is available
    if command -v Xvfb &> /dev/null; then
        echo -e "${GREEN}✓ Xvfb detected${NC}"
        echo ""
        echo -e "${CYAN}🚀 Redirecting to Xvfb mode...${NC}"
        echo -e "${BLUE}   (Virtual display for best VPS compatibility)${NC}"
        echo ""
        sleep 2

        # Deactivate venv first (run_xvfb.sh will activate it)
        deactivate

        # Run with Xvfb
        exec ./run_xvfb.sh

    else
        echo -e "${YELLOW}⚠️  Xvfb not installed${NC}"
        echo ""
        echo -e "${YELLOW}📥 Installing Xvfb for better compatibility...${NC}"
        echo ""

        if [ "$OS" == "Linux" ]; then
            # Try to install Xvfb
            if command -v apt-get &> /dev/null; then
                echo "Installing Xvfb..."
                sudo apt-get update -qq
                sudo apt-get install -y xvfb

                if command -v Xvfb &> /dev/null; then
                    echo -e "${GREEN}✓ Xvfb installed successfully${NC}"
                    echo ""
                    echo -e "${CYAN}🚀 Starting with Xvfb...${NC}"
                    echo ""

                    # Deactivate venv
                    deactivate

                    # Run with Xvfb
                    exec ./run_xvfb.sh
                fi
            fi
        fi

        # Fallback to headless mode if Xvfb not available
        echo -e "${YELLOW}⚠️  Xvfb not available - falling back to headless mode${NC}"
        echo -e "${YELLOW}   (Lower success rate: 60-80%)${NC}"
        echo ""
        echo -e "${BLUE}💡 For better results, install Xvfb manually:${NC}"
        echo "   sudo apt-get install xvfb"
        echo "   Then run: ./run_xvfb.sh"
        echo ""

        read -p "Continue with headless mode? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Cancelled."
            deactivate
            exit 0
        fi

        echo ""
        echo -e "${CYAN}🚀 Starting in headless mode...${NC}"
        echo ""

        # Run in headless mode
        python run.py
    fi
fi

# Deactivate on exit
echo ""
echo -e "${CYAN}🔄 Deactivating virtual environment...${NC}"
deactivate
echo -e "${GREEN}✓ Done${NC}"
