#!/bin/bash

# Chrome Fix Script for Zefoy Bot
# This script helps kill zombie Chrome/ChromeDriver processes

echo "🔧 Chrome Fix Script for Zefoy Bot"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Step 1: Kill zombie Chrome processes
echo "Step 1: Killing zombie Chrome/ChromeDriver processes..."

# Kill Chrome browser processes (be specific to avoid killing this script)
pkill -9 "google-chrome" 2> /dev/null
pkill -9 "chrome-browser" 2> /dev/null
pkill -9 "chromium" 2> /dev/null
pkill -9 "chromium-browser" 2> /dev/null

# Kill ChromeDriver processes
pkill -9 "chromedriver" 2> /dev/null

sleep 1
echo -e "${GREEN}✓${NC} Zombie processes killed"
echo ""

# Clean Chrome temporary files
echo "Step 2: Cleaning Chrome temporary files..."
rm -rf ~/.config/google-chrome/Singleton* 2> /dev/null
rm -rf ~/.config/chromium/Singleton* 2> /dev/null
rm -rf /tmp/.com.google.Chrome.* 2> /dev/null
rm -rf /tmp/.org.chromium.Chromium.* 2> /dev/null
echo -e "${GREEN}✓${NC} Temporary files cleaned"
echo ""

echo -e "${GREEN}✓${NC} Chrome fix script completed!"
echo ""
