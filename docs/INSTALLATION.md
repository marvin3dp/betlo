# Installation Guide

Complete installation guide for TikTok Bot across different platforms.

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Linux Installation](#linux-installation)
- [macOS Installation](#macos-installation)
- [Windows Installation](#windows-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## System Requirements

### Minimum Requirements

- **OS:** Linux, macOS, or Windows
- **Python:** 3.8 or higher
- **RAM:** 2GB minimum, 4GB recommended
- **Disk Space:** 500MB free space
- **Internet:** Stable connection required

### Software Requirements

- Python 3.8+
- Tesseract OCR
- Google Chrome or Chromium
- Git (for cloning repository)

---

## Linux Installation

### Ubuntu/Debian (20.04, 22.04, 24.04)

#### Step 1: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install System Dependencies

```bash
# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python and tools
sudo apt-get install -y python3 python3-pip python3-venv

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# OR install Chromium
sudo apt-get install -y chromium-browser
```

#### Step 3: Clone Repository

```bash
cd ~/Documents
git clone <repository-url> bots
cd bots
```

#### Step 4: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Configure

```bash
# Copy example config (if exists)
cp config.example.yaml config.yaml

# Edit configuration
nano config.yaml
# OR
vim config.yaml
```

#### Step 6: Run

```bash
python run.py
```

---

### Arch Linux

```bash
# Update system
sudo pacman -Syu

# Install dependencies
sudo pacman -S tesseract tesseract-data-eng python python-pip google-chrome git

# Clone and setup
cd ~/Documents
git clone <repository-url> bots
cd bots

# Virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python run.py
```

---

### Fedora/RHEL

```bash
# Update system
sudo dnf update -y

# Install dependencies
sudo dnf install -y tesseract tesseract-langpack-eng python3 python3-pip git

# Install Chrome
sudo dnf install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

# Clone and setup
cd ~/Documents
git clone <repository-url> bots
cd bots

# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run
python run.py
```

---

## macOS Installation

### Prerequisites

Install Homebrew if not already installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Installation Steps

#### Step 1: Install Dependencies

```bash
# Install Tesseract
brew install tesseract

# Install Python
brew install python@3.11

# Install Chrome
brew install --cask google-chrome

# Install Git (if needed)
brew install git
```

#### Step 2: Clone Repository

```bash
cd ~/Documents
git clone <repository-url> bots
cd bots
```

#### Step 3: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure and Run

```bash
# Edit config
nano config.yaml

# Run bot
python run.py
```

---

## Windows Installation

### Step 1: Install Python

1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **Important:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Install Tesseract OCR

1. Download Tesseract from
   [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer
3. Install to: `C:\Program Files\Tesseract-OCR`
4. Add to PATH:
   - Open "Environment Variables"
   - Edit "Path" system variable
   - Add: `C:\Program Files\Tesseract-OCR`
5. Verify:
   ```cmd
   tesseract --version
   ```

### Step 3: Install Google Chrome

1. Download from [google.com/chrome](https://www.google.com/chrome/)
2. Install normally
3. Chrome will auto-update ChromeDriver

### Step 4: Install Git (Optional)

Download from [git-scm.com](https://git-scm.com/download/win)

### Step 5: Clone Repository

**Using Git:**

```cmd
cd %USERPROFILE%\Documents
git clone <repository-url> bots
cd bots
```

**OR Download ZIP:**

1. Download repository as ZIP
2. Extract to `Documents\bots`

### Step 6: Setup Python Environment

```cmd
cd %USERPROFILE%\Documents\bots

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 7: Configure and Run

```cmd
# Edit config with Notepad
notepad config.yaml

# Run bot
python run.py
```

---

## Verification

### Verify Tesseract Installation

```bash
tesseract --version
# Should show version 4.x or 5.x
```

### Verify Python Installation

```bash
python --version
# Should show 3.8 or higher
```

### Verify Chrome Installation

```bash
# Linux/macOS
google-chrome --version
# OR
chromium --version

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

### Verify Python Packages

```bash
# Activate venv first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Check packages
pip list | grep selenium
pip list | grep undetected-chromedriver
pip list | grep pytesseract
```

### Test Run

```bash
python run.py
```

If you see the welcome screen, installation is successful! 🎉

---

## Troubleshooting

### Tesseract Not Found

**Linux:**

```bash
# Check if installed
which tesseract

# If not found, reinstall
sudo apt-get install --reinstall tesseract-ocr
```

**macOS:**

```bash
# Reinstall via Homebrew
brew reinstall tesseract
```

**Windows:**

```cmd
# Check PATH
echo %PATH%

# Verify Tesseract location
dir "C:\Program Files\Tesseract-OCR"

# Add to PATH if missing (run as admin)
setx /M PATH "%PATH%;C:\Program Files\Tesseract-OCR"
```

---

### Python Version Too Old

**Linux/macOS:**

```bash
# Install Python 3.11
sudo apt-get install python3.11  # Ubuntu
brew install python@3.11         # macOS

# Use specific version
python3.11 -m venv venv
```

**Windows:** Download newer Python from
[python.org](https://www.python.org/downloads/)

---

### Chrome/ChromeDriver Issues

**Solution 1: Update Chrome**

```bash
# Linux
sudo apt-get update
sudo apt-get upgrade google-chrome-stable

# macOS
brew upgrade google-chrome

# Windows - Chrome auto-updates
```

**Solution 2: Clear Chrome Data**

```bash
# Run cleanup script
chmod +x fix_chrome.sh
./fix_chrome.sh
```

**Solution 3: Reinstall undetected-chromedriver**

```bash
pip install --upgrade --force-reinstall undetected-chromedriver
```

---

### Permission Errors (Linux/macOS)

```bash
# Make scripts executable
chmod +x run.py
chmod +x install.sh
chmod +x fix_chrome.sh

# If installing to system (not recommended)
sudo pip install -r requirements.txt  # DON'T DO THIS

# Instead use venv (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Virtual Environment Issues

**Linux/macOS:**

```bash
# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

**Windows:**

```cmd
# Remove old venv
rmdir /s venv

# Create new venv
python -m venv venv

# Activate
venv\Scripts\activate

# Reinstall
pip install -r requirements.txt
```

---

### Installation Script

For automated installation on Linux:

```bash
#!/bin/bash
# install.sh

echo "🚀 Installing TikTok Bot..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Installing..."
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Check Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "❌ Tesseract not found. Installing..."
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
fi

# Check Chrome
if ! command -v google-chrome &> /dev/null; then
    echo "❌ Chrome not found. Installing..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi

# Setup venv
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation complete!"
echo "Run: source venv/bin/activate && python run.py"
```

Make executable:

```bash
chmod +x install.sh
./install.sh
```

---

## Next Steps

After successful installation:

1. **Configure the bot:** Edit `config.yaml`
2. **Read usage guide:** See [USAGE_GUIDE.md](USAGE_GUIDE.md)
3. **Configure OCR:** See [OCR_TROUBLESHOOTING.md](OCR_TROUBLESHOOTING.md)
4. **Run the bot:** `python run.py`

---

## Getting Help

- 📖 [README.md](../README.md) - Main documentation
- 📝 [USAGE_GUIDE.md](USAGE_GUIDE.md) - How to use
- 🤖 [OCR_TROUBLESHOOTING.md](OCR_TROUBLESHOOTING.md) - OCR help
- 🐛 [GitHub Issues](https://github.com/issues) - Report problems

---

**Happy Botting! 🚀**
