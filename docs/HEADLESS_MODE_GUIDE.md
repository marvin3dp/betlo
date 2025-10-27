# Headless Mode with Auto-Open Captcha - Quick Start Guide

## 🎯 What is Headless Mode?

**Headless mode** = Browser berjalan di background tanpa tampilan GUI window.

**Benefits:**

- ✅ Lebih cepat (no GUI rendering)
- ✅ Hemat resource (less RAM & CPU)
- ✅ Bisa jalan di server tanpa display
- ✅ Multiple instances lebih mudah

## 🚀 Quick Start

### 1. Enable Headless Mode

Edit `config.yaml`:

```yaml
browser:
  headless: true # ✅ Enable headless mode

captcha:
  manual_input: true
  save_image: true
  auto_open_image: true # ✅ Auto-open captcha saat manual mode
```

### 2. Run Bot

```bash
python run.py
```

### 3. When Captcha Appears

**Automatic behavior:**

1. ✅ Captcha akan di-save ke `screenshots/captcha_manual_TIMESTAMP.png`
2. ✅ Image viewer otomatis terbuka menampilkan captcha
3. ✅ Input captcha text di terminal
4. ✅ Submit dan continue!

**Terminal output:**

```
🔐 Manual Captcha Required 🔐

📸 Captcha image opened automatically
Location: captcha_manual_20251022_143052.png

📝 Enter the text you see
(lowercase letters only)

Enter captcha text: █
```

## 📸 How It Works

```
Browser (headless) → Captcha detected
         ↓
Save to screenshots/captcha_manual_XXX.png
         ↓
Auto-open with xdg-open (Linux) / open (macOS) / startfile (Windows)
         ↓
Image viewer shows captcha
         ↓
User inputs text in terminal
         ↓
Bot continues!
```

## 🔧 Supported Image Viewers

### Linux

Auto-detected in this order:

1. `xdg-open` (universal) ✅ **RECOMMENDED**
2. `eog` (GNOME Image Viewer)
3. `feh` (lightweight)
4. `display` (ImageMagick)
5. `gwenview` (KDE)
6. `gthumb`
7. `gpicview` (LXDE)

### macOS

- `open` (built-in) ✅

### Windows

- `os.startfile()` (built-in) ✅

## ⚙️ Configuration Options

| Setting                   | Values         | Description                   |
| ------------------------- | -------------- | ----------------------------- |
| `browser.headless`        | `true`/`false` | Enable headless mode          |
| `captcha.save_image`      | `true`/`false` | Save captcha to screenshots/  |
| `captcha.auto_open_image` | `true`/`false` | Auto-open with default viewer |
| `captcha.manual_input`    | `true`/`false` | Enable manual input mode      |

## 💡 Tips & Tricks

### Tip 1: Keep Image Viewer Open

Jangan close image viewer setelah input captcha pertama. Window akan auto-update
dengan captcha baru di execution berikutnya (on most viewers).

### Tip 2: Use Lightweight Viewer (Linux)

For better performance:

```bash
sudo apt install feh
```

`feh` sangat ringan dan perfect untuk headless mode.

### Tip 3: Multiple Monitors

Put image viewer di monitor kedua, terminal di monitor pertama. Workflow lebih
smooth!

### Tip 4: Cleanup Old Captchas

```bash
# Delete captcha images older than 7 days
find screenshots/ -name "captcha_manual_*.png" -mtime +7 -delete
```

## 🐛 Troubleshooting

### Problem: "No image viewer found"

**Solution (Linux):**

```bash
# Install xdg-utils (recommended)
sudo apt install xdg-utils

# Or install eog
sudo apt install eog

# Or install feh (lightweight)
sudo apt install feh
```

**Verify:**

```bash
which xdg-open
# Should output: /usr/bin/xdg-open
```

### Problem: Image tidak terbuka tapi bot tetap jalan

**This is expected!**

- Auto-open failure tidak akan stop bot
- Buka manual dari `screenshots/` folder
- Check log untuk details

**Manual open:**

```bash
# List captcha images
ls -lt screenshots/captcha_manual_*.png | head -1

# Open latest manually
xdg-open $(ls -t screenshots/captcha_manual_*.png | head -1)
```

### Problem: Too many windows opening

**Disable auto-open:**

```yaml
captcha:
  auto_open_image: false # Disable auto-open
  save_image: true # Still save for manual opening
```

Then open manually when needed.

## 🎨 Example Workflows

### Workflow 1: Full Headless with Auto-Open

```yaml
browser:
  headless: true

captcha:
  auto_solve: false # OCR might not work well
  manual_input: true # Manual input
  save_image: true # Save captcha
  auto_open_image: true # Auto-open
```

**Best for:** Desktop usage, manual captcha solving

### Workflow 2: Headless with Manual Open

```yaml
browser:
  headless: true

captcha:
  manual_input: true
  save_image: true
  auto_open_image: false # Don't auto-open
```

**Best for:** Server usage, VNC/remote desktop

### Workflow 3: Non-Headless (Traditional)

```yaml
browser:
  headless: false # See browser window

captcha:
  manual_input: true
  save_image: false # Don't save (see in browser)
  auto_open_image: false # Don't auto-open
```

**Best for:** Development, debugging

### Workflow 4: OCR Auto-Solve (Experimental)

```yaml
browser:
  headless: true

captcha:
  auto_solve: true # Try OCR first
  manual_input: true # Fallback to manual
  save_image: true
  auto_open_image: true # Auto-open if OCR fails
```

**Best for:** Reduce manual work (if OCR works well)

### Workflow 5: VPS/Remote Server with Cloud Upload ☁️ **NEW!**

```yaml
browser:
  headless: true

captcha:
  auto_solve: false
  manual_input: true
  save_image: true
  auto_open_image: false # No GUI on VPS
  upload_to_cloud: true # ✅ Upload to uploader.sh
  cloud_uploader_url: https://uploader.sh
```

**Best for:** VPS/remote servers without GUI

**How it works:**

1. Bot detects captcha
2. Automatically uploads image to uploader.sh
3. Displays URL in terminal (e.g., `https://uploader.sh/captcha_123.png`)
4. Open URL in your local browser/phone
5. View captcha and input text in VPS terminal
6. Done!

**Perfect for:**

- ✅ Running bot on VPS/cloud servers
- ✅ SSH sessions without X forwarding
- ✅ Remote access from mobile devices
- ✅ No need for image viewer installation

**See:** [docs/CLOUD_CAPTCHA_UPLOAD.md](CLOUD_CAPTCHA_UPLOAD.md) for detailed
guide

## 📊 Performance Comparison

| Mode                           | RAM Usage          | CPU Usage | Speed     | Captcha Method     | Best For           |
| ------------------------------ | ------------------ | --------- | --------- | ------------------ | ------------------ |
| **Headless + Cloud Upload** ☁️ | 🟢 Low (~400MB)    | 🟢 Low    | 🟢 Fast   | Cloud URL (VPS)    | VPS/Remote servers |
| **Headless + Auto-Open**       | 🟢 Low (~400MB)    | 🟢 Low    | 🟢 Fast   | Auto-open image    | Local desktop      |
| Non-Headless                   | 🟡 Medium (~600MB) | 🟡 Medium | 🟡 Normal | See in browser     | Development        |
| Headless + Manual Open         | 🟢 Low (~400MB)    | 🟢 Low    | 🔴 Slower | Manual folder open | Advanced users     |

## 🎯 Recommended Setup

**For daily usage:**

```yaml
browser:
  headless: true
  use_adblock: true
  disable_images: false # Need to see captcha!

captcha:
  auto_solve: false
  manual_input: true
  save_image: true
  auto_open_image: true
  debug_mode: false
```

This gives you:

- ✅ Best performance (headless)
- ✅ Easy captcha solving (auto-open)
- ✅ Clean workflow
- ✅ Low resource usage

## 🚀 Advanced: Multiple Instances

Run multiple bots dengan headless mode:

**Terminal 1:**

```bash
python run.py
# Captcha 1 opens → Input → Continue
```

**Terminal 2:**

```bash
python run.py
# Captcha 2 opens → Input → Continue
```

Each instance akan open captcha di separate image viewer window!

## 📝 Summary

✅ **Headless mode** = Browser tidak terlihat, save resource ✅ **Auto-open
captcha** = Image viewer otomatis terbuka ✅ **Save to screenshots/** =
Permanent record ✅ **Cross-platform** = Works on Linux, macOS, Windows ✅
**Configurable** = Customize sesuai kebutuhan

**Perfect untuk:**

- 🎯 Daily automation
- 🎯 Server/VPS usage
- 🎯 Multiple instances
- 🎯 Low resource environments

Enjoy your efficient headless bot! 🚀
