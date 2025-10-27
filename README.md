<div align="center">

<img src="assets/logo.png" alt="TikTok Bot Logo" width="400">

<br><br>

### 🚀 Advanced TikTok Services Automation

**Powerful bot with intelligent OCR captcha solver and modern terminal UI**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com)
[![OCR](https://img.shields.io/badge/OCR-Tesseract-orange.svg)](https://github.com/tesseract-ocr/tesseract)
![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/marvin3dp/betlo?utm_source=oss&utm_medium=github&utm_campaign=marvin3dp%2Fbetlo&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) •
[Configuration](#-configuration) • [Documentation](#-documentation) •
[FAQ](#-faq)

---

</div>

## 📋 Table of Contents

- [✨ Features](#-features)
- [🎯 Supported Services](#-supported-services)
- [📸 Screenshots](#-screenshots)
- [🚀 Installation](#-installation)
- [💡 Usage](#-usage)
- [⚙️ Configuration](#-configuration)
- [🤖 OCR Captcha Solver](#-ocr-captcha-solver)
- [📊 Performance](#-performance)
- [📚 Documentation](#-documentation)
- [🐛 Troubleshooting](#-troubleshooting)
- [❓ FAQ](#-faq)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#️-disclaimer)
- [📜 License](#-license)

---

## ✨ Features

### 🤖 **Intelligent OCR Captcha Solver**

<table>
<tr>
<td width="50%">

**FAST Mode** ⚡

- 5 preprocessing methods
- 5 OCR configurations
- ~30 attempts per captcha
- Processing time: **10-20 seconds**
- 2 OCR retries before manual
- **Recommended for most users**

</td>
<td width="50%">

**AGGRESSIVE Mode** 🐌

- Up to 12 preprocessing methods
- Up to 26 OCR configurations
- 300+ attempts per captcha
- Processing time: **3-5 minutes**
- 5 OCR retries before manual
- For difficult captchas

</td>
</tr>
</table>

**Advanced Capabilities:**

- 🔍 **Horizontal Reading** - Left→Right like humans
- 🎯 **Uneven Text Handling** - Handles overlapping & naik-turun text
- 📊 **Frequency-based Confidence Scoring** - Selects most reliable result
- 🐛 **Debug Mode** - Save all preprocessing steps for analysis
- 🖼️ **Auto-Open Captcha** - Perfect for headless mode
- ☁️ **Cloud Upload** - Upload captcha to uploader.sh for easy VPS access
- 🔄 **Manual Input Fallback** - Never gets stuck

### 🎨 **Modern Terminal UI**

- ✨ Beautiful rounded panels with Rich library
- 🎯 Interactive menus with questionary
- 📊 Real-time statistics display
- ⏱️ User-friendly uptime format (e.g., `4m 16s`)
- 🎨 Colorful logs with emoji support
- 📈 Progress bars and countdown timers
- 🖥️ Clean, centered messages

### 🛡️ **Advanced Bot Features**

- 🔄 **Intelligent Cooldown System** - 6 fallback points prevent rate limiting
- 🎯 **Target Goals & Progress Tracking** - Set targets and track automatically
- 🌐 **Headless Mode Support** - Run in background with auto-open captcha
- 🎭 **Stealth Mode** - Advanced techniques to hide headless/automation
- 🖥️ **VPS Auto-Detection** - Auto-enable headless on servers (no display)
- 🚫 **Advanced AdBlock** - DNS-based + Request interception
- 🤖 **Human-like Behavior** - Random delays, typing simulation
- 💾 **Session Persistence** - Continue where you left off
- 🧹 **Auto Cleanup** - Chrome zombie process killer
- 📝 **Comprehensive Logging** - MAIN/DEBUG/INFO levels

### 🎯 **Service Management**

- ✅ Enable/disable services individually
- 🎯 Active service marker (visual indicator)
- 📊 Live service status from Zefoy
- 🔄 Auto-retry on cooldown
- 📈 Real-time progress tracking
- 🎯 Three execution modes:
  - Manual Executions
  - Target Amount
  - Goal Mode (continuous)

---

## 🎯 Supported Services

| Service                | Status     | Rate Limit | Notes          |
| ---------------------- | ---------- | ---------- | -------------- |
| ❤️ **Hearts**          | ✅ Active  | ~25/exec   | Most reliable  |
| 👁️ **Views**           | ✅ Active  | ~500/exec  | High volume    |
| 🔄 **Shares**          | ✅ Active  | ~50/exec   | Fast cooldown  |
| ⭐ **Favorites**       | ✅ Active  | ~100/exec  | Stable         |
| 💬 **Comments Hearts** | ✅ Active  | ~25/exec   | Moderate       |
| 👥 **Followers**       | ⚠️ Offline | ~50/exec   | Zefoy disabled |
| 🔴 **Live Stream**     | ⚠️ Offline | ~50/exec   | Zefoy disabled |

> **Note:** Service availability depends on Zefoy's status. Bot automatically
> detects and marks offline services.

---

## 📸 Screenshots

<div align="center">

### Welcome Screen

```
╭─────────────────────────── 👋 Welcome ───────────────────────────╮
│                                                                   │
│                    TikTok Automation Tool                         │
│                                                                   │
│               🚀 Automate TikTok engagement                       │
│               ✨ Multiple services support                        │
│               🎯 Target goals & continuous mode                   │
│               ⚡ Real-time cooldown tracking                      │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
```

### Statistics Display

```
╭─────────────────────── 📊 Bot Statistics ───────────────────────╮
│                                                                  │
│                     Uptime: 1h 23m 45s                           │
│                     Captchas Solved: 15                          │
│                     Tasks Completed: 12                          │
│                     Tasks Failed: 0                              │
│                                                                  │
│                     Services Used:                               │
│                       • Hearts: 8                                │
│                       • Views: 4                                 │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

### Captcha Solving

```
╭──────────────────── 🔍 OCR Captcha Solver ─────────────────────╮
│                                                                 │
│  ⚡ FAST Mode: 30 attempts in 10-20s                            │
│  🎯 Horizontal reading enabled                                 │
│  📊 Confidence scoring active                                  │
│                                                                 │
│  [████████████████░░░░░░░░] 60% Complete                        │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
```

</div>

---

## 🚀 Installation

### Prerequisites

**System Requirements:**

- Python 3.8 or higher
- Tesseract OCR
- Google Chrome or Chromium
- 2GB RAM minimum
- Linux, macOS, or Windows

### Step 1: Install System Dependencies

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y google-chrome-stable  # or chromium-browser
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install tesseract
brew install python3
brew install --cask google-chrome
```

</details>

<details>
<summary><b>Windows</b></summary>

1. Install [Python 3.8+](https://www.python.org/downloads/)
2. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
3. Install [Google Chrome](https://www.google.com/chrome/)
4. Add Tesseract to PATH
</details>

### Step 2: Clone Repository

```bash
cd ~/Documents
git clone <repository-url> bots
cd bots
```

### Step 3: Install Python Dependencies

**Automated Installation (Recommended):**

```bash
chmod +x install.sh
./install.sh
```

The `install.sh` script will automatically:

- ✓ Install `python3-venv` and `python3-full` (Debian/Ubuntu)
- ✓ Install Google Chrome + dependencies
- ✓ Create virtual environment
- ✓ Install all Python packages
- ✓ Setup required directories

**Manual Installation:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🖥️ VPS/Server Installation

For VPS or headless servers, use the **smart automated installer**:

```bash
./install.sh
```

**✨ Smart Features:**
- 🔍 **Auto-detects** VPS/Server environment
- 📦 **Auto-installs** Chrome + dependencies
- 🖥️ **Auto-installs** Xvfb (virtual display)
- ⚙️ **Auto-configures** for optimal performance

**Check VPS Environment:**

```bash
./check_vps.sh  # Verify everything is configured correctly
```

**Important for VPS:**

- **⚠️ Zefoy Detection Issue?** Use Xvfb for 95%+ reliability!
  ```bash
  ./run_xvfb.sh  # Best solution for VPS
  ```
- **Auto-detection:** Bot automatically enables headless mode if no display is
  detected! 🎉
- **Alternative:** Pure headless with stealth (60-80% success rate)
- Minimum 2GB RAM required
- /dev/shm should be >64MB (check with `df -h /dev/shm`)
- **Troubleshooting:** [ZEFOY_HEADLESS_FIX.md](docs/ZEFOY_HEADLESS_FIX.md)
- **Complete guide:** [VPS_SETUP.md](docs/VPS_SETUP.md)

**Key Dependencies:**

- `selenium` 4.15.2 - Browser automation
- `undetected-chromedriver` 3.5.5 - Anti-detection
- `pytesseract` 0.3.10 - OCR engine
- `opencv-python` 4.8.1.78 - Image processing
- `Pillow` 10.1.0 - Image manipulation
- `numpy` 1.26.4 - Numerical operations
- `PyYAML` 6.0.1 - Configuration
- `rich` 13.7.0 - Terminal UI
- `questionary` 2.0.1 - Interactive prompts

### Step 4: Configure

Edit `config.yaml` with your preferences:

```yaml
# Quick Start Configuration
captcha:
  auto_solve: true # Enable OCR
  fast_mode: true # Use FAST mode (recommended)
  manual_input: true # Fallback to manual
  auto_open_image: true # Auto-open captcha (local mode)
  upload_to_cloud: false # Upload to uploader.sh (VPS mode)

browser:
  headless: false # Set true for background mode
  use_adblock: true # Block ads for faster loading

logging:
  level: MAIN # Clean user-friendly logs
  colorful: true # Colorful terminal output
```

### Step 5: Run

```bash
python run.py
```

Or with virtual environment:

```bash
source venv/bin/activate
python run.py
```

---

## 💡 Usage

### Quick Start (Smart Auto-Detect) ⭐ **RECOMMENDED**

The **easiest way** - automatically detects your environment and chooses the best mode:

```bash
./venv.sh
```

**What it does:**
- ✅ **Desktop/Laptop** → Runs in visible mode (99% success)
- ✅ **VPS with Xvfb** → Uses virtual display (95%+ success)
- ✅ **VPS without Xvfb** → Auto-installs Xvfb or falls back to headless

This is the smartest way to run the bot - it picks the optimal mode for you!

### Manual Start

1. **Start the bot:**

   ```bash
   python run.py
   ```

2. **From main menu, select:** `🚀 Start Bot`

3. **Choose your service:** Hearts, Views, Shares, etc.

4. **Enter TikTok video URL**

5. **Select execution mode:**
   - **Manual Executions** - Set number of times (e.g., 5 times)
   - **Target Amount** - Set target count (e.g., 10,000 hearts)
   - **Goal Mode** - Use targets from config

6. **Sit back and relax!** Bot handles everything automatically.

### Execution Modes Explained

**1. Manual Executions**

```
Execute service exactly N times
Example: "Run 5 times" → Executes 5 times then stops
Perfect for: Quick boosts, testing
```

**2. Target Amount**

```
Run until reaching specific amount
Example: "Get 10,000 hearts" → Runs until 10k reached
Perfect for: Specific goals, one-time campaigns
```

**3. Goal Mode**

```
Uses targets from config.yaml
Tracks progress across sessions
Perfect for: Long-term goals, continuous growth
```

### Interactive Menus

**Main Menu:**

- 🚀 Start Bot
- ⚙️ Configure Settings
- 📊 View Statistics
- 📋 View Available Services
- ❓ Help
- 🚪 Exit

**Settings Menu:**

- 🌐 Browser Settings (headless, adblock, user agent)
- ⏱️ Timeout Settings
- 🔐 Captcha & OCR Settings (FAST/AGGRESSIVE modes)
- 📝 Logging Settings
- 🎯 Service Target Goals
- 🔌 Enable/Disable Services

**Bot Running Menu:**

- ▶️ Execute Service
- 📊 View Statistics (live session stats)
- 🎯 View Target Goals Progress
- 🔄 Refresh Page
- ◀️ Back to Main Menu

---

## ⚙️ Configuration

### Configuration File Structure

```yaml
# config.yaml - Complete configuration reference

browser:
  headless: false # Run in background
  use_adblock: true # Block ads (recommended)
  disable_images: false # Disable images for speed
  window_size: "1920,1080" # Browser resolution
  user_agent: "Mozilla/5.0..." # Custom user agent

captcha:
  auto_solve: true # Enable OCR
  fast_mode: true # FAST mode (10-20s)
  manual_input: true # Manual fallback
  save_image: true # Save screenshots
  auto_open_image: true # Auto-open (headless!)
  debug_mode: false # Debug preprocessing

  ocr_advanced: # AGGRESSIVE mode settings
    horizontal_reading: true # Left→Right reading
    handle_uneven_text: true # Uneven text support
    aggressive_preprocessing: false # 12 methods vs 5
    aggressive_ocr_configs: false # 26 configs vs 5

timeouts:
  page_load: 30 # Page load timeout
  element_wait: 10 # Element wait time
  captcha_solve: 120 # Captcha timeout
  between_actions: 2 # Action delays
  retry_delay: 5 # Retry delay

retry:
  auto_retry_on_cooldown: true # Auto-retry
  max_attempts: 3 # Max retry attempts
  on_captcha_fail: true # Retry on captcha fail

service_execution:
  show_countdown: true # Show cooldown timer
  active_service_only: false # Single service mode
  default_target: 1 # Default target

service_targets: # Goal mode targets
  hearts: 10000
  views: 50000
  followers: 1000
  shares: 2000
  favorites: 3000
  comments_hearts: 5000
  livestream: 500

  per_execution: # Average per execution
    hearts: 100
    views: 1000
    followers: 50
    shares: 50
    favorites: 100
    comments_hearts: 50
    livestream: 50

logging:
  level: MAIN # MAIN/INFO/DEBUG
  colorful: true # Colored output
  save_to_file: true # Save to logs/

zefoy:
  url: "https://zefoy.com"

  services: # Service configuration
    - name: "Hearts"
      enabled: true
      button_class: "t-hearts-button"

    - name: "Views"
      enabled: true
      button_class: "t-views-button"

    # ... more services

paths:
  screenshots: "screenshots" # Screenshot folder
  logs: "logs" # Log folder
  extensions: "extensions" # Extensions folder
```

### Common Configuration Scenarios

<details>
<summary><b>Headless Mode (Background Operation)</b></summary>

```yaml
browser:
  headless: true

captcha:
  auto_solve: true
  auto_open_image: true # Important for headless!
  save_image: true
```

</details>

<details>
<summary><b>Maximum Speed</b></summary>

```yaml
browser:
  headless: true
  use_adblock: true
  disable_images: true

captcha:
  fast_mode: true # Quick OCR

timeouts:
  between_actions: 1 # Minimal delays
```

</details>

<details>
<summary><b>Maximum Accuracy (Difficult Captchas)</b></summary>

```yaml
captcha:
  auto_solve: true
  fast_mode: false # AGGRESSIVE mode

  ocr_advanced:
    aggressive_preprocessing: true
    aggressive_ocr_configs: true
    horizontal_reading: true
    handle_uneven_text: true
```

</details>

<details>
<summary><b>Debug Mode</b></summary>

```yaml
captcha:
  debug_mode: true # Save all preprocessing

logging:
  level: DEBUG # Verbose logging
```

</details>

---

## 🤖 OCR Captcha Solver

### How It Works

```
┌─────────────┐
│   Captcha   │
│   Image     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Preprocessing (5-12 methods)     │
│   • Line removal                    │
│   • Noise reduction                 │
│   • Contrast enhancement            │
│   • Thresholding                    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   OCR Engine (5-26 configs)        │
│   • Tesseract LSTM                  │
│   • Multiple PSM modes              │
│   • Horizontal reading              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Confidence Scoring                │
│   • Frequency analysis              │
│   • Length validation               │
│   • Pattern detection               │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Result    │
│   (a-z,A-Z) │
└─────────────┘
```

### FAST Mode vs AGGRESSIVE Mode

| Feature             | FAST Mode ⚡  | AGGRESSIVE Mode 🐌 |
| ------------------- | ------------- | ------------------ |
| **Preprocessing**   | 5 methods     | Up to 12 methods   |
| **OCR Configs**     | 5 configs     | Up to 26 configs   |
| **Total Attempts**  | ~30           | 300+               |
| **Processing Time** | 10-20 seconds | 3-5 minutes        |
| **OCR Retries**     | 2 retries     | 5 retries          |
| **Success Rate**    | 70-85%        | 75-90%             |
| **Recommended For** | Most users    | Difficult captchas |

### Preprocessing Methods

1. **Line Removal + Adaptive Threshold**
   - Morphological operations to detect and remove lines
   - Adaptive thresholding for varying lighting

2. **Morphological Line Removal + Otsu**
   - Aggressive line detection with larger kernels
   - Otsu's binarization for optimal threshold

3. **Bilateral Filter + CLAHE**
   - Edge-preserving noise reduction
   - Contrast Limited Adaptive Histogram Equalization

4. **Inverted + Line Removal**
   - For light text on dark background
   - Inverts colors before processing

5. **Median Blur + Line Removal**
   - Salt-and-pepper noise removal
   - Maintains edge sharpness

6. **Erosion-Dilation** _(AGGRESSIVE only)_
   - Morphological operations
   - Thick line handling

**+ 6 additional methods in AGGRESSIVE mode**

### OCR Configurations

**Page Segmentation Modes (PSM):**

- PSM 8 - Single word (most common)
- PSM 7 - Single line of text
- PSM 6 - Uniform block of text
- PSM 13 - Raw line (no dictionaries)
- PSM 10 - Single character

**OCR Engine Modes (OEM):**

- OEM 1 - LSTM only (neural network)
- OEM 3 - Legacy + LSTM (hybrid)

**+ 21 additional configs in AGGRESSIVE mode**

### Confidence Scoring

```python
# Scoring factors:
1. Length score (3-8 chars optimal)
2. Frequency count (same result multiple times)
3. Pattern detection (avoid repeated chars like "aaaa")
4. Character whitelist (a-z, A-Z only)

# Example:
Result "abCdEf" appears 5 times → High confidence ✅
Result "aaaa" appears 3 times → Low confidence (pattern) ❌
Result "ab12" appears 2 times → Invalid (numbers) ❌
```

---

## 📊 Performance

### Success Rates

| Captcha Type     | FAST Mode | AGGRESSIVE Mode |
| ---------------- | --------- | --------------- |
| Clean text       | 85-95%    | 90-98%          |
| With lines       | 70-80%    | 80-90%          |
| Heavy noise      | 50-65%    | 65-80%          |
| Overlapping text | 40-55%    | 60-75%          |
| Uneven text      | 55-70%    | 70-85%          |

### Speed Comparison

| Mode           | Processing Time | Total Attempts | Recommended Use                      |
| -------------- | --------------- | -------------- | ------------------------------------ |
| **FAST**       | 10-20 seconds   | ~30            | Daily use, most captchas             |
| **AGGRESSIVE** | 3-5 minutes     | 300+           | Difficult captchas, low success rate |

### System Performance

**Resource Usage:**

- CPU: 10-30% (during OCR processing)
- RAM: 200-500 MB
- Disk: ~10 MB for screenshots (with debug)

**Execution Speed:**

- Captcha solve: 10-20s (FAST) / 3-5min (AGGRESSIVE)
- Service execution: 5-10s
- Cooldown wait: 2-5 minutes (varies by service)
- Total per execution: 3-7 minutes average

---

## 📚 Documentation

### Main Documentation

| Document                          | Description                 |
| --------------------------------- | --------------------------- |
| [README.md](README.md)            | This file - Complete guide  |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and updates |
| [LICENSE](LICENSE)                | MIT License                 |

### Feature Guides

| Guide                                                             | Topic                           |
| ----------------------------------------------------------------- | ------------------------------- |
| [VPS_SETUP.md](docs/VPS_SETUP.md)                                 | **VPS/Server setup guide**      |
| [INSTALLATION.md](docs/INSTALLATION.md)                           | Detailed installation guide     |
| [CHROME_TROUBLESHOOTING.md](docs/CHROME_TROUBLESHOOTING.md)       | Chrome/ChromeDriver issues      |
| [OCR_TROUBLESHOOTING.md](docs/OCR_TROUBLESHOOTING.md)             | OCR debugging and optimization  |
| [AGGRESSIVE_OCR_MODE.md](docs/AGGRESSIVE_OCR_MODE.md)             | AGGRESSIVE mode detailed guide  |
| [DISPLAY_MODES.md](docs/DISPLAY_MODES.md)                         | **Display modes comparison** ⭐ |
| [HEADLESS_MODE_GUIDE.md](docs/HEADLESS_MODE_GUIDE.md)             | Running in headless mode        |
| [HEADLESS_STEALTH.md](docs/HEADLESS_STEALTH.md)                   | Stealth mode details            |
| [ZEFOY_HEADLESS_FIX.md](docs/ZEFOY_HEADLESS_FIX.md)               | Fix Zefoy detection (Xvfb)      |
| [ZEFOY_DETECTION_FIX.md](docs/ZEFOY_DETECTION_FIX.md)             | **Captcha not detected fix** ⚠️ |
| [VPS_CDP_FIX.md](docs/VPS_CDP_FIX.md)                             | **Runtime.evaluate error** ⚠️   |
| [CDP_ERROR_FINAL_FIX.md](docs/CDP_ERROR_FINAL_FIX.md)             | **CDP error suppression** ✅    |
| [STUCK_HEADLESS_FIX.md](docs/STUCK_HEADLESS_FIX.md)               | **Bot stuck/timeout fix** ✅    |
| [FINAL_FIXES_v2.md](docs/FINAL_FIXES_v2.md)                       | **All comprehensive fixes** 📚  |
| [FIXES_SUMMARY.md](docs/FIXES_SUMMARY.md)                         | **Quick fixes summary** 📋      |
| [AUTO_OPEN_CAPTCHA_FEATURE.md](docs/AUTO_OPEN_CAPTCHA_FEATURE.md) | Auto-open captcha feature       |
| [COOLDOWN.md](docs/COOLDOWN.md)                                   | Cooldown system explained       |

### Quick References

| Reference              | Link                                     |
| ---------------------- | ---------------------------------------- |
| Installation Help      | See [Installation](#-installation)       |
| Configuration Examples | See [Configuration](#-configuration)     |
| FAQ                    | See [FAQ](#-faq)                         |
| Troubleshooting        | See [Troubleshooting](#-troubleshooting) |

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>❌ OCR keeps failing / Low success rate</b></summary>

**Solutions:**

1. **Enable Debug Mode:**

   ```yaml
   captcha:
     debug_mode: true
   logging:
     level: DEBUG
   ```

2. **Check Screenshots:**
   - Look in `screenshots/` folder
   - Check preprocessing quality
   - Verify text is readable

3. **Try AGGRESSIVE Mode:**

   ```yaml
   captcha:
     fast_mode: false
     ocr_advanced:
       aggressive_preprocessing: true
       aggressive_ocr_configs: true
   ```

4. **Enable Manual Fallback:**
   ```yaml
   captcha:
     manual_input: true
   ```

**See:** [docs/OCR_TROUBLESHOOTING.md](docs/OCR_TROUBLESHOOTING.md)

</details>

<details>
<summary><b>❌ Chrome not found / ChromeDriver error</b></summary>

**Solutions:**

1. **Install Chrome:**

   ```bash
   # Ubuntu/Debian
   sudo apt-get install google-chrome-stable

   # macOS
   brew install --cask google-chrome
   ```

2. **Clean Chrome Processes:**

   ```bash
   chmod +x fix_chrome.sh
   ./fix_chrome.sh
   ```

3. **Update ChromeDriver:**
   ```bash
   pip install --upgrade undetected-chromedriver
   ```

**See:** [docs/CHROME_TROUBLESHOOTING.md](docs/CHROME_TROUBLESHOOTING.md)

</details>

<details>
<summary><b>❌ Service on cooldown constantly</b></summary>

**This is normal!** Services have cooldowns:

- First execution: No cooldown
- After success: 2-5 minutes cooldown
- Bot waits automatically

**Enable auto-retry:**

```yaml
retry:
  auto_retry_on_cooldown: true
```

**See:** [docs/COOLDOWN.md](docs/COOLDOWN.md)

</details>

<details>
<summary><b>❌ Headless mode - Can't see captcha</b></summary>

**Solution - Auto-open feature:**

```yaml
browser:
  headless: true

captcha:
  save_image: true
  auto_open_image: true # ← This opens captcha automatically!
```

Bot will open captcha image with default viewer automatically!

**See:** [docs/HEADLESS_MODE_GUIDE.md](docs/HEADLESS_MODE_GUIDE.md)

</details>

<details>
<summary><b>❌ Tesseract not found</b></summary>

**Install Tesseract:**

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH after installation
```

**Verify installation:**

```bash
tesseract --version
```

</details>

<details>
<summary><b>❌ Bot crashes / Freezes</b></summary>

**Solutions:**

1. **Check logs:**

   ```bash
   tail -f logs/betlo_*.log
   ```

2. **Clean Chrome:**

   ```bash
   ./fix_chrome.sh
   ```

3. **Restart with DEBUG:**

   ```yaml
   logging:
     level: DEBUG
   ```

4. **Check system resources:**
   - Ensure 2GB+ RAM available
   - Close other Chrome instances
   </details>

### Getting Help

1. **Check logs:** `logs/betlo_YYYYMMDD.log`
2. **Enable DEBUG mode:** Set `logging.level: DEBUG`
3. **Check documentation:** See [docs/](docs/) folder
4. **Review FAQ:** See [FAQ](#-faq) section below

---

## ❓ FAQ

### General Questions

**Q: Is this safe to use?** A: The bot uses undetected-chromedriver and
human-like behavior to minimize detection. However, use at your own risk and
follow TikTok/Zefoy ToS.

**Q: Do I need a Zefoy account?** A: No, Zefoy doesn't require accounts. Just
visit the website and use services.

**Q: Can I run multiple instances?** A: Not recommended. Running multiple
instances may cause conflicts and increase detection risk.

**Q: Does this work on mobile?** A: No, this is a desktop application requiring
Python and Chrome.

### OCR Questions

**Q: What's the difference between FAST and AGGRESSIVE mode?** A: FAST mode is
faster (10-20s) with good accuracy (70-85%). AGGRESSIVE mode is slower (3-5min)
but more thorough (75-90%). Use FAST for daily use, AGGRESSIVE for difficult
captchas.

**Q: Can I train my own OCR model?** A: Not currently. The bot uses Tesseract
OCR which is pre-trained. You can adjust preprocessing methods in the code.

**Q: OCR never works, should I disable it?** A: Don't disable! Instead, enable
`manual_input: true` for fallback. This way OCR tries first, manual as backup.

### Configuration Questions

**Q: How do I run in background?** A: Set `browser.headless: true` and
`captcha.auto_open_image: true` in config.yaml

**Q: Can I customize service targets?** A: Yes! Edit `service_targets` section
in config.yaml

**Q: How do I enable only specific services?** A: Use Settings menu →
Enable/Disable Services, or edit config.yaml

### Troubleshooting Questions

**Q: Service shows "OFFLINE", what to do?** A: This means Zefoy has disabled the
service. Wait for Zefoy to re-enable it. You can still try to use it, but it may
not work.

**Q: Cooldown is too long, can I skip it?** A: No, cooldowns are enforced by
Zefoy. Skipping would cause errors. Enable `show_countdown: true` to see
countdown timer.

**Q: Statistics not showing, why?** A: Statistics show when bot is running. From
main menu, it shows last session data from `target_progress.json`. Execute some
services first!

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Areas for Improvement

- 🎯 Additional preprocessing methods for OCR
- 📊 Better confidence scoring algorithms
- 🌐 Support for other captcha types
- ⚡ Performance optimizations
- 🎨 UI/UX improvements
- 📝 Documentation improvements
- 🌍 Internationalization (i18n)

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit:** `git commit -m 'Add amazing feature'`
6. **Push:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions
- Comment complex logic
- Keep functions focused and small

### Testing

- Test on multiple platforms (Linux, macOS, Windows)
- Test with different captcha types
- Verify no regressions in existing features
- Check for linter errors

---

## ⚠️ Disclaimer

### Educational Purpose Only

This bot is created for **educational and research purposes only**. By using
this software, you acknowledge that:

- ⚖️ You will use it **responsibly and ethically**
- 📜 You understand the **risks and consequences**
- ✅ You will **comply with all applicable laws** and Terms of Service
- 🚫 You will **not use it for spam, abuse, or commercial purposes** without
  permission
- 👤 You take **full responsibility** for your actions

### Legal Notice

- This software is provided "AS IS" without warranties
- Authors are not responsible for misuse or damages
- Not affiliated with TikTok or Zefoy
- Users must comply with TikTok and Zefoy Terms of Service
- Automated interactions may violate platform policies

### Use at Your Own Risk

- Account bans or restrictions are possible
- Service availability depends on Zefoy
- Results are not guaranteed
- No warranty or support guarantee

**By using this software, you agree to these terms.**

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE)
file for details.

### MIT License Summary

✅ **Permissions:**

- Commercial use
- Modification
- Distribution
- Private use

❌ **Limitations:**

- Liability
- Warranty

📋 **Conditions:**

- License and copyright notice must be included

---

## 🙏 Credits & Acknowledgments

This project uses the following open-source libraries:

### Core Dependencies

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Optical
  character recognition engine
- [OpenCV](https://opencv.org/) - Image processing library
- [Selenium](https://www.selenium.dev/) - Browser automation framework
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) -
  Anti-detection Chrome driver

### UI & Utilities

- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [Questionary](https://github.com/tmbo/questionary) - Interactive CLI prompts
- [PyYAML](https://pyyaml.org/) - YAML configuration parser
- [Pillow](https://python-pillow.org/) - Image manipulation
- [NumPy](https://numpy.org/) - Numerical operations

### Special Thanks

- The open-source community for amazing tools
- Tesseract OCR team for powerful OCR engine
- Contributors and users of this project

---

## 🆕 What's New in v3.0.0

### October 23, 2025 Update - Major Release

#### 🔄 BREAKING CHANGE: Package Renamed to Betlo

- **Package renamed** from `zefoy_bot` to `betlo`
  - Import changes: `from zefoy_bot.main` → `from betlo.main`
  - Log files: `zefoy_bot_*.log` → `betlo_*.log`
  - Module path: `python -m zefoy_bot` → `python -m betlo`
  - All 37 files updated with new package name
  - Complete documentation updated across all files

#### ⚡ 10-60x Faster Commits with Optimized Pre-commit

- **Commit speed improved dramatically**
  - Before: 2-5 minutes (waiting for Node.js/Go installation)
  - After: 2-5 seconds for normal commits ⚡
- **Two-tier approach**
  - Fast hooks: Run automatically on every commit (2-5 seconds)
  - Slow hooks: Run manually before push (2-5 minutes)
- **Smart hook staging**
  - Markdown linter → manual only (was slow)
  - YAML formatter → manual only (was slow)
  - Shell formatter → manual only (was slow)
  - Python formatters → auto-run, scoped to `betlo/*.py`

- **New documentation**
  - `PRE_COMMIT_GUIDE.md` - Complete usage guide
  - Learn how to run fast commits and full checks

#### 📝 Migration Guide

**Update your imports:**

```python
# OLD
from zefoy_bot.main import main
import zefoy_bot

# NEW
from betlo.main import main
import betlo
```

**Quick steps:**

1. Pull latest changes: `git pull`
2. Update imports in your code
3. Reinstall pre-commit: `pre-commit install`
4. Enjoy faster commits! 🚀

**See [CHANGELOG.md](docs/CHANGELOG.md) for complete version history**

---

## 📞 Support & Contact

### Documentation

- 📖 [Full Documentation](docs/)
- 📝 [Changelog](docs/CHANGELOG.md)
- ❓ [FAQ](#-faq)
- 🐛 [Troubleshooting](#-troubleshooting)

### Resources

- 💻 [GitHub Repository](https://github.com)
- 📊 [Issue Tracker](https://github.com/issues)
- 💬 [Discussions](https://github.com/discussions)

---

<div align="center">

### ⭐ Star this project if you find it useful!

**Made with ❤️ by the community**

---

**Last Updated:** October 23, 2025 **Current Version:** 3.0.0 - Package Renamed
to Betlo & Optimized Pre-commit

**[↑ Back to Top](#-table-of-contents)**

</div>
