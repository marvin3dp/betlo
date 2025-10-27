#!/bin/bash
# Test Zefoy Detection
# This script helps diagnose Zefoy page loading and element detection issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "════════════════════════════════════════════════════"
echo "   🔍 Zefoy Detection Test"
echo "════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    echo "Run ./install.sh first"
    exit 1
fi

# Check if using Xvfb
if [ -z "$DISPLAY" ]; then
    echo -e "${YELLOW}⚠️  No DISPLAY variable set${NC}"
    echo -e "${YELLOW}   Running in pure headless mode${NC}"
    echo ""
    echo -e "${BLUE}💡 For best Zefoy detection, use:${NC}"
    echo -e "${BLUE}   ./run_xvfb.sh${NC}"
    echo ""
    read -p "Continue with pure headless? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
else
    echo -e "${GREEN}✓ DISPLAY=$DISPLAY${NC}"
    if ps aux | grep -v grep | grep Xvfb > /dev/null; then
        echo -e "${GREEN}✓ Xvfb is running${NC}"
    fi
fi

echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "🧪 Running Zefoy detection test..."
echo "   This will:"
echo "   1. Load Zefoy page"
echo "   2. Check for captcha element"
echo "   3. Save debug info to debug/ folder"
echo ""

# Create a test Python script
cat > /tmp/test_zefoy_$$.py << 'EOF'
import sys
import os
from pathlib import Path
import time

# Add betlo to path
sys.path.insert(0, str(Path(__file__).parent))

from betlo.config import Config
from betlo.logger import setup_logger
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def test_zefoy():
    """Test Zefoy page loading and element detection"""

    print("🌐 Setting up Chrome...")
    config = Config()
    logger = setup_logger("DEBUG")

    # Setup Chrome with similar options
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    # Check if should use headless
    import subprocess
    result = subprocess.run(['xset', 'q'], capture_output=True)
    has_display = result.returncode == 0

    if not has_display:
        print("⚠️  No display detected, forcing headless mode")
        options.add_argument("--headless=new")
    else:
        print(f"✓ Display available: {os.environ.get('DISPLAY', 'unknown')}")

    print("🚀 Starting Chrome...")
    driver = uc.Chrome(options=options, version_main=None)

    try:
        print(f"🌐 Loading {config.zefoy_url}...")
        driver.get(config.zefoy_url)

        # Wait longer for Zefoy
        print("⏳ Waiting 10 seconds for page to load...")
        time.sleep(10)

        # Check ready state
        ready_state = driver.execute_script("return document.readyState")
        print(f"📄 Document ready state: {ready_state}")

        # Get page info
        title = driver.title
        url = driver.current_url
        source_len = len(driver.page_source)

        print(f"📋 Page Info:")
        print(f"   Title: {title}")
        print(f"   URL: {url}")
        print(f"   Source length: {source_len} chars")

        # Check for elements
        print("")
        print("🔍 Checking for elements...")

        # Captcha
        try:
            captcha = driver.find_element(By.ID, "captchatoken")
            print("   ✓ Captcha element FOUND (#captchatoken)")
        except:
            print("   ✗ Captcha element NOT FOUND (#captchatoken)")

        # Body
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            print("   ✓ Body element FOUND")
        except:
            print("   ✗ Body element NOT FOUND")

        # Forms
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"   Forms: {len(forms)}")

        # Buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"   Buttons: {len(buttons)}")

        # Save debug
        print("")
        print("💾 Saving debug info...")
        debug_dir = Path("debug")
        debug_dir.mkdir(exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # HTML
        html_path = debug_dir / f"test_source_{timestamp}.html"
        with open(html_path, "w") as f:
            f.write(driver.page_source)
        print(f"   ✓ HTML: {html_path}")

        # Screenshot
        screenshot_path = debug_dir / f"test_screenshot_{timestamp}.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"   ✓ Screenshot: {screenshot_path}")

        print("")
        print("✅ Test complete! Check debug/ folder for details.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("")
        print("🧹 Closing browser...")
        driver.quit()

    return True

if __name__ == "__main__":
    test_zefoy()
EOF

# Run the test
python /tmp/test_zefoy_$$.py

# Cleanup
rm /tmp/test_zefoy_$$.py

echo ""
echo "════════════════════════════════════════════════════"
echo "💡 Tips:"
echo "════════════════════════════════════════════════════"
echo ""
echo "If captcha NOT found:"
echo "  1. Check debug/ folder for HTML and screenshot"
echo "  2. Verify Zefoy URL is correct in config.yaml"
echo "  3. Try with Xvfb: ./run_xvfb.sh"
echo "  4. Check if Zefoy changed their page structure"
echo ""
echo "If you see Cloudflare or rate limit:"
echo "  1. Wait a few minutes and try again"
echo "  2. Zefoy may be blocking your IP"
echo ""
