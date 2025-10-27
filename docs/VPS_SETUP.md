# VPS/Server Setup Guide

Guide untuk setup bot di VPS atau server tanpa GUI (headless environment).

---

## 🚨 Common VPS Errors

### Error: "Binary Location Must be a String"

**Penyebab:** Chrome tidak terinstall atau tidak ditemukan di VPS

**Solusi Cepat:**

```bash
# Jalankan script instalasi otomatis (smart auto-detect)
./install.sh
```

**✨ Script ini akan otomatis:**
- 🔍 Deteksi environment VPS/Server
- 📦 Install Python venv & dependencies
- 🌐 Install Chrome + dependencies
- 🖥️ Install Xvfb (virtual display)
- ⚙️ Configure untuk optimal performance

**Atau manual (jika diperlukan):**

```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Verifikasi
google-chrome --version
which google-chrome
```

---

## 📋 VPS Requirements

### Minimum Specs:

- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 5GB free space
- **Architecture:** x86_64 (amd64)

### Required Software:

- Python 3.8+
- Chrome or Chromium browser
- Xvfb (for headless display)

---

## 🚀 Quick Setup (Automatic)

Gunakan script instalasi yang sudah otomatis install semua dependencies:

```bash
# Clone repository
git clone <repo-url> bots
cd bots

# Run installer (akan auto-install Chrome, python3-full, dll)
./install.sh

# Verify VPS environment is ready
./check_vps.sh
```

Script ini akan otomatis:

- ✓ Install `python3-venv` dan `python3-full`
- ✓ Install Google Chrome + dependencies
- ✓ Create virtual environment
- ✓ Install Python packages
- ✓ Setup directories

**Check VPS Script** (`check_vps.sh`) akan verify:

- ✓ Chrome installation
- ✓ Python version
- ✓ Virtual environment
- ✓ RAM availability
- ✓ /dev/shm size
- ✓ Disk space
- ✓ Headless mode config
- ✓ No zombie processes
- ✓ Python packages installed

---

## 🔧 Manual Setup

### Step 1: Install System Dependencies

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install Python dan tools
sudo apt install -y \
    python3 \
    python3-full \
    python3-venv \
    python3-pip \
    wget \
    git

# Install Chrome dependencies
# Note: Package names may vary between Ubuntu/Debian versions
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
    xdg-utils

# For older Ubuntu/Debian (20.04, 22.04):
sudo apt install -y libatk-bridge2.0-0 libgtk-3-0 libasound2 2>/dev/null || \
# For newer Ubuntu/Debian (24.04+):
sudo apt install -y libatk-bridge2.0-0t64 libgtk-3-0t64 libasound2t64 2>/dev/null || true
```

### Step 2: Install Google Chrome

```bash
# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install
sudo apt install ./google-chrome-stable_current_amd64.deb

# Verify
google-chrome --version
```

**Alternative - Install Chromium:**

```bash
sudo apt install chromium-browser
chromium-browser --version
```

### Step 3: Setup Bot

```bash
# Clone repository
cd ~
git clone <repo-url> bots
cd bots

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs screenshots extensions
```

### Step 4: Configure for Headless Mode

**IMPORTANT:** Bot will **auto-detect VPS environment** and enable headless mode
automatically if no display is found!

However, it's recommended to explicitly set it in `config.yaml`:

```yaml
browser:
  headless: true # Recommended for VPS (auto-detected if not set)
  window_size: "1920,1080"

logging:
  level: INFO # atau DEBUG untuk troubleshooting
```

**Auto-Detection Features:**

- ✓ Checks for `$DISPLAY` environment variable
- ✓ Checks for Xvfb virtual display
- ✓ Auto-enables headless if no display found
- ✓ Prevents "chrome not reachable" errors on VPS
- ✓ Shows clear warning in logs when auto-enabled

**Stealth Mode (NEW! 🎭):**

- ✓ JavaScript injection to hide headless indicators
- ✓ Mock browser properties (plugins, languages, etc)
- ✓ Override navigator.webdriver property
- ✓ Makes headless mode undetectable by websites
- ✓ Automatic - no configuration needed!
- ✓ See [HEADLESS_STEALTH.md](./HEADLESS_STEALTH.md) for details

### Step 5: Run Bot

**Option A: With Xvfb (RECOMMENDED for best Zefoy compatibility):**

```bash
# Set headless: false in config.yaml (Xvfb provides display)
nano config.yaml
# Change: headless: false

# Run with smart auto-detect (uses Xvfb on VPS)
./venv.sh
```

**Option B: Pure Headless (60-80% success rate):**

```bash
# Set headless: true in config.yaml
nano config.yaml
# Change: headless: true

# Activate venv
source venv/bin/activate

# Run bot
python run.py
```

**Why Xvfb?**

- ✓ Zefoy works 95%+ reliably
- ✓ Full page rendering like real browser
- ✓ No headless detection issues
- ✓ Bot runs in "visible" mode without GUI
- ✓ Better than pure headless for aggressive detection sites

See [ZEFOY_HEADLESS_FIX.md](./ZEFOY_HEADLESS_FIX.md) for details.

---

## 🔍 Troubleshooting VPS

### 0. Zefoy Elements Not Detected in Headless ⚠️ COMMON ISSUE

**Symptom:** Bot says "No captcha found", service buttons not detected, page
elements missing in headless mode

**Cause:** Zefoy has aggressive bot detection. Pure headless mode may not work
well.

**✅ SOLUTION: Use Xvfb (Virtual Display)**

This is the MOST RELIABLE solution for VPS:

```bash
# Install Xvfb (if not already)
sudo apt install xvfb

# Set config to non-headless
nano config.yaml
# Set: headless: false

# Run with smart auto-detect (uses Xvfb on VPS)
./venv.sh
```

**Why This Works:**

- Bot runs in "visible" mode with virtual display
- Zefoy sees normal browser behavior
- 95%+ success rate vs 60-80% with pure headless
- No detection issues

**Note:** You may see xkbcomp warnings when starting Xvfb - these are harmless
and already suppressed by the script.

**See Complete Guide:** [ZEFOY_HEADLESS_FIX.md](./ZEFOY_HEADLESS_FIX.md)

---

### 1. Chrome Not Found

**Error:** `Binary Location Must be a String` atau `chrome not found`

**Solusi:**

```bash
# Cek apakah Chrome terinstall
which google-chrome
google-chrome --version

# Jika tidak ada, install:
./install.sh  # Smart installer with auto-detect
```

### 2. Chrome Not Reachable

**Error:** `cannot connect to chrome at 127.0.0.1:XXXXX` atau
`chrome not reachable`

**Symptoms:**

- Browser Mode shows "Visible" instead of "Headless"
- Chrome crashes immediately after starting
- Error: "session not created: cannot connect to chrome"

**Penyebab:**

- Chrome trying to run in visible mode on VPS (no display available)
- `$DISPLAY` environment variable not set
- Headless mode not enabled

**🆕 Auto-Detection (v2.0+):**

Bot sekarang **auto-detect VPS environment** dan akan enable headless mode
otomatis jika tidak ada display!

Check logs untuk pesan:

```
⚠ No display detected (VPS/Server environment)
⚠ Auto-enabling headless mode for stability
```

Dan browser mode akan menunjukkan:

```
Browser Mode: Headless (Auto - No Display Detected)
```

**Manual Fixes (jika auto-detection tidak bekerja):**

```bash
# 1. Manually set headless mode
nano config.yaml
# Set: headless: true

# 2. Check /dev/shm size (should be >64MB)
df -h /dev/shm

# Jika terlalu kecil (<64MB), increase size:
sudo mount -o remount,size=256M /dev/shm

# Make permanent (add to /etc/fstab):
echo "tmpfs /dev/shm tmpfs defaults,size=256M 0 0" | sudo tee -a /etc/fstab

# 3. Kill zombie Chrome processes
pkill -9 -f chrome
pkill -9 -f chromedriver
rm -rf /tmp/.com.google.Chrome.*

# 4. Install/verify Chrome dependencies & Xvfb
./install.sh  # Smart installer (auto-installs everything)

# 5. Run bot (auto-detects & uses Xvfb)
./venv.sh  # Unified smart runner (recommended)

# 6. For very low RAM VPS (<1GB), enable single-process mode
nano config.yaml
# Add: single_process: true
# WARNING: Less stable, only use if necessary
```

**Advanced: Check Chrome startup manually**

```bash
# Test Chrome startup
google-chrome --headless --no-sandbox --disable-dev-shm-usage --dump-dom https://google.com

# If this fails, check logs:
google-chrome --headless --no-sandbox --disable-dev-shm-usage --enable-logging --v=1 2>&1 | tee chrome_debug.log
```

### 3. Display/GPU Errors

**Error:** `Could not start Chrome` atau GPU-related errors

**Solusi:** Bot sudah include flags untuk headless, tapi jika masih error:

```bash
# Install Xvfb untuk virtual display
sudo apt install xvfb

# Run dengan Xvfb wrapper
xvfb-run python run.py
```

### 3. Permission Denied

**Error:** Permission errors saat install atau run

**Solusi:**

```bash
# Pastikan user punya sudo access
sudo -v

# Script sudah executable
chmod +x install.sh
chmod +x run.py
chmod +x venv.sh

# Jangan run bot sebagai root!
# Selalu run sebagai user biasa
```

### 4. Package Dependency Errors

**Error:** `Unable to locate package libgconf-2-4` atau
`Package 'libasound2' has no installation candidate`

**Penyebab:** Package names berbeda antara Ubuntu/Debian versi lama dan baru
(24.04+ menggunakan suffix `t64`)

**Solusi:**

Script `install.sh` sudah otomatis handle ini dengan smart fallback detection.
Tapi jika manual install:

```bash
# Ubuntu/Debian 24.04+ (menggunakan t64 packages)
sudo apt install -y \
    libatk-bridge2.0-0t64 \
    libgtk-3-0t64 \
    libasound2t64

# Ubuntu/Debian 20.04-22.04 (menggunakan non-t64)
sudo apt install -y \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2

# libgconf-2-4 sudah deprecated, tidak perlu diinstall
```

**Note:** Script instalasi otomatis akan coba keduanya dengan fallback.

### 5. Out of Memory

**Error:** Chrome crashes atau killed by kernel

**Solusi:**

```bash
# Check RAM usage
free -h

# VPS minimal 2GB RAM
# Jika kurang, upgrade VPS atau:

# Edit config.yaml - disable images
browser:
  disable_images: true  # Hemat RAM
```

### 6. Slow Performance

**Penyebab:** VPS specs rendah atau network lambat

**Optimasi:**

Edit `config.yaml`:

```yaml
browser:
  headless: true
  disable_images: true # Hemat bandwidth & RAM
  use_adblock: true # Block ads = lebih cepat

timeouts:
  page_load: 45 # Increase timeout untuk network lambat
  element_wait: 15
```

---

## 📊 VPS Performance Tips

### RAM Optimization

```yaml
# config.yaml
browser:
  disable_images: true # Save ~100-200MB RAM
  use_adblock: true # Less memory for ads
  headless: true # No GUI overhead
```

### Network Optimization

```bash
# Use closer DNS servers
# Edit /etc/resolv.conf (requires sudo)
sudo nano /etc/resolv.conf

# Add:
nameserver 1.1.1.1
nameserver 8.8.8.8
```

### Storage Optimization

```bash
# Regular cleanup
cd ~/bots

# Clean old logs (keep last 7 days)
find logs/ -name "*.log" -mtime +7 -delete

# Clean old screenshots (keep last 3 days)
find screenshots/ -name "*.png" -mtime +3 -delete

# Clean Chrome cache
rm -rf ~/.cache/google-chrome/
```

---

## 🔐 Security Tips for VPS

### 1. Don't Run as Root

```bash
# NEVER do this:
sudo python run.py  # ❌ DANGEROUS

# Always run as normal user:
source venv/bin/activate
python run.py  # ✓ SAFE
```

### 2. Firewall Setup

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (IMPORTANT - don't lock yourself out!)
sudo ufw allow 22/tcp

# Deny unnecessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status
```

### 3. Keep System Updated

```bash
# Regular updates
sudo apt update && sudo apt upgrade -y

# Update bot dependencies
cd ~/bots
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🔄 Running Bot 24/7

### Using Screen (Recommended)

```bash
# Install screen
sudo apt install screen

# Create session
screen -S betlo_bot

# Run bot
cd ~/bots
source venv/bin/activate
python run.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r betlo_bot
# List sessions: screen -ls
```

### Using tmux

```bash
# Install tmux
sudo apt install tmux

# Create session
tmux new -s betlo_bot

# Run bot
cd ~/bots
source venv/bin/activate
python run.py

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t betlo_bot
# List sessions: tmux ls
```

### Using Systemd Service (Advanced)

Create service file:

```bash
sudo nano /etc/systemd/system/betlo-bot.service
```

Add:

```ini
[Unit]
Description=Betlo Bot Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bots
ExecStart=/home/YOUR_USERNAME/bots/venv/bin/python /home/YOUR_USERNAME/bots/run.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
# Replace YOUR_USERNAME with your actual username
sudo systemctl daemon-reload
sudo systemctl enable betlo-bot
sudo systemctl start betlo-bot

# Check status
sudo systemctl status betlo-bot

# View logs
sudo journalctl -u betlo-bot -f
```

---

## 📝 Checking Logs on VPS

```bash
# Real-time log viewing
tail -f logs/betlo_*.log

# Search for errors
grep -i error logs/betlo_*.log

# Last 50 lines
tail -n 50 logs/betlo_*.log

# View specific date
cat logs/betlo_2025-10-27.log
```

---

## 🆘 Emergency Recovery

### Bot Stuck/Not Responding

```bash
# Kill all Chrome processes
pkill -9 -f chrome
pkill -9 -f chromedriver

# Clean temp files
rm -rf /tmp/.com.google.Chrome.*
rm -rf /tmp/.org.chromium.Chromium.*

# Restart bot
cd ~/bots
source venv/bin/activate
python run.py
```

### Reinstall Everything

```bash
# Remove venv and reinstall
cd ~/bots
rm -rf venv
./install.sh

# Or full reinstall
cd ~
rm -rf bots
git clone <repo-url> bots
cd bots
./install.sh
```

---

## ✅ VPS Checklist

Before running bot on VPS, verify:

- [ ] Chrome/Chromium installed: `google-chrome --version`
- [ ] Python 3.8+: `python3 --version`
- [ ] Virtual environment: `ls -la venv/`
- [ ] Dependencies installed: `pip list`
- [ ] Config set to headless: `grep headless config.yaml`
- [ ] Enough RAM: `free -h` (minimum 2GB)
- [ ] Enough storage: `df -h` (minimum 5GB free)
- [ ] /dev/shm size OK: `df -h /dev/shm` (minimum 64MB, recommended 256MB)
- [ ] No zombie Chrome: `ps aux | grep chrome` (should be empty)
- [ ] Bot runs without errors: `python run.py`

---

## 📚 Additional Resources

- [CHROME_TROUBLESHOOTING.md](./CHROME_TROUBLESHOOTING.md) - Chrome issues
- [HEADLESS_MODE_GUIDE.md](./HEADLESS_MODE_GUIDE.md) - Headless mode details
- [FAQ.md](./FAQ.md) - Common questions

---

## 🆕 Quick Commands Reference

```bash
# Install bot (first time)
./install.sh

# Check VPS environment
./check_vps.sh

# Quick Start (Unified Smart Runner - RECOMMENDED)
./venv.sh  # Auto-detects environment, uses Xvfb on VPS

# Alternative: Manual mode
source venv/bin/activate
python run.py

# Run with screen (for 24/7)
screen -S bot
./venv.sh  # Smart auto-detect
# Detach: Ctrl+A then D

# Check logs
tail -f logs/betlo_*.log

# Kill Chrome
pkill -f chrome

# Update bot
git pull
source venv/bin/activate
pip install -r requirements.txt
```

---

**Need help?** Check other docs or open an issue on GitHub.
