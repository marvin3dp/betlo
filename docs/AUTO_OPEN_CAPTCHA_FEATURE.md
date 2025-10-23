# Auto-Open Captcha Feature - October 22, 2025

## Overview

Menambahkan fitur **auto-open captcha image** saat mode manual input, dengan
otomatis membuka captcha menggunakan default image viewer yang terinstall di
sistem. Fitur ini sangat berguna saat menggunakan **headless mode** dimana
browser tidak terlihat.

## Problem Statement

### ❌ Masalah Sebelumnya

Saat menggunakan **headless mode** (`browser.headless: true`):

1. Browser tidak terlihat di screen
2. User tidak bisa melihat captcha di browser window
3. Captcha hanya disave ke folder `screenshots/` tapi user harus buka manual
4. Proses menjadi lambat dan tidak efisien

### ✅ Solusi Baru

Dengan fitur auto-open:

1. Captcha **otomatis disave** ke `screenshots/captcha_manual_TIMESTAMP.png`
2. Captcha **otomatis dibuka** dengan default image viewer (eog, feh, xdg-open,
   dll)
3. User langsung bisa lihat captcha tanpa perlu buka folder manual
4. Bekerja di **Linux**, **macOS**, dan **Windows**

## Changes Made

### 1. **Update `captcha_solver.py`**

#### A. Import Modules Baru

**Line 6-10:**

```python
import os
import platform
import subprocess
```

Modules ini diperlukan untuk:

- `platform`: Detect OS (Linux/macOS/Windows)
- `subprocess`: Execute command untuk open image
- `os`: Windows `startfile()` function

#### B. New Config Option

**Line 52:**

```python
self.auto_open_image = config.get('captcha.auto_open_image', True)
```

Config option baru untuk enable/disable auto-open feature.

#### C. New Method: `_open_image_with_default_app()`

**Line 342-398:**

Fungsi untuk membuka image dengan default application berdasarkan OS:

**Linux:**

- **First try**: `xdg-open` (universal, works on all desktop environments)
- **Fallback**: Try specific viewers: `eog`, `feh`, `display`, `gwenview`,
  `gthumb`, `gpicview`
- **Process**: `subprocess.Popen()` dengan DEVNULL untuk silent execution

**macOS:**

- **Command**: `open` (built-in macOS command)
- **Process**: `subprocess.Popen()`

**Windows:**

- **Command**: `os.startfile()` (built-in Windows function)
- **Behavior**: Opens with associated default app

**Error Handling:**

- Graceful fallback jika command tidak ditemukan
- Warning log jika gagal, tapi tidak stop execution
- Return `True`/`False` untuk indicate success

#### D. Updated Method: `_solve_manually()`

**Line 550-608:**

Perubahan di manual captcha solving:

**Before:**

```python
# Save captcha image
if self.save_image:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path = self.config.screenshot_path / f"captcha_{timestamp}.png"
    captcha_img.screenshot(str(img_path))
    self.logger.info(f"Captcha image saved: {img_path}")
```

**After:**

```python
# Save captcha image
img_path = None
if self.save_image:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path = self.config.screenshot_path / f"captcha_manual_{timestamp}.png"
    captcha_img.screenshot(str(img_path))
    self.logger.info(f"Captcha image saved: {img_path}")

    # ✅ NEW: Auto-open image with default application
    if self.auto_open_image:
        opened = self._open_image_with_default_app(img_path)
        if not opened:
            self.logger.warning("Could not auto-open captcha image. Check screenshots folder manually.")
```

**Changes:**

1. Filename changed: `captcha_{timestamp}.png` →
   `captcha_manual_{timestamp}.png` (untuk distinguish dari OCR captcha)
2. Auto-open jika `auto_open_image = True`
3. Warning log jika gagal open, tapi tetap lanjut

**UI Message Update:**

```python
if img_path and self.auto_open_image:
    captcha_content.append("📸 Captcha image opened automatically\n", style="bold green")
    captcha_content.append(f"Location: {img_path.name}\n\n", style="dim white")
else:
    captcha_content.append("Please look at the captcha image\n", style="bold white")
    captcha_content.append("in your browser window\n\n", style="bold white")
```

### 2. **Update `config.yaml`**

**Line 9-14:**

```yaml
captcha:
  auto_solve: false
  debug_mode: false
  manual_input: true
  save_image: true # ✅ Changed from false to true
  auto_open_image: true # ✅ NEW: Auto-open with default viewer
```

**Changes:**

- `save_image`: Changed to `true` (default enabled)
- `auto_open_image`: **NEW config option** (default enabled)

## How It Works

### Flow Diagram

```
Manual Captcha Required
        ↓
Save captcha_manual_TIMESTAMP.png
        ↓
Check: auto_open_image = true?
        ↓ YES
Detect OS (Linux/macOS/Windows)
        ↓
Open with default viewer:
  - Linux: xdg-open or eog/feh/etc
  - macOS: open
  - Windows: os.startfile()
        ↓
User sees captcha in image viewer
        ↓
User inputs captcha text
        ↓
Submit & verify
```

### Supported Image Viewers (Linux)

1. **xdg-open** - Universal (works on all desktop environments) ✅
   **RECOMMENDED**
2. **eog** - GNOME Image Viewer (Eye of GNOME)
3. **feh** - Lightweight image viewer
4. **display** - ImageMagick
5. **gwenview** - KDE image viewer
6. **gthumb** - Image viewer & browser
7. **gpicview** - Lightweight image viewer (LXDE)

Bot akan try secara otomatis dan use yang pertama available.

## Usage Examples

### Example 1: Headless Mode with Auto-Open

**config.yaml:**

```yaml
browser:
  headless: true # Browser tidak terlihat

captcha:
  manual_input: true
  save_image: true
  auto_open_image: true # ✅ Enable auto-open
```

**Result:**

```
🔧 Chrome Fix Script for Zefoy Bot
==================================

🔐 Manual Captcha Required 🔐

📸 Captcha image opened automatically
Location: captcha_manual_20251022_143052.png

📝 Enter the text you see
(lowercase letters only)

Enter captcha text: abcdef
```

Image viewer akan otomatis terbuka dan menampilkan captcha!

### Example 2: Non-Headless Mode with Auto-Open Disabled

**config.yaml:**

```yaml
browser:
  headless: false # Browser terlihat

captcha:
  manual_input: true
  save_image: true
  auto_open_image: false # ❌ Disable auto-open (lihat di browser saja)
```

**Result:**

```
🔐 Manual Captcha Required 🔐

Please look at the captcha image
in your browser window

📝 Enter the text you see
(lowercase letters only)

Enter captcha text: abcdef
```

User melihat captcha langsung di browser window.

### Example 3: Save Only (No Auto-Open)

**config.yaml:**

```yaml
captcha:
  manual_input: true
  save_image: true
  auto_open_image: false
```

Captcha akan disave ke `screenshots/` tapi tidak auto-open.

## Benefits

### ✅ Advantages

1. **Headless Mode Support**: Sekarang bisa menggunakan headless mode tanpa
   masalah
2. **User Friendly**: User tidak perlu buka folder screenshots manual
3. **Fast**: Image langsung terbuka saat captcha muncul
4. **Cross-Platform**: Works on Linux, macOS, Windows
5. **Graceful Fallback**: Jika auto-open gagal, user masih bisa buka manual
6. **Configurable**: Bisa disable jika tidak diperlukan

### ⚙️ Configuration Options

| Option                    | Default | Description                        |
| ------------------------- | ------- | ---------------------------------- |
| `captcha.save_image`      | `true`  | Save captcha ke screenshots folder |
| `captcha.auto_open_image` | `true`  | Auto-open dengan default viewer    |
| `captcha.manual_input`    | `true`  | Enable manual input mode           |

## Installation Notes

### Linux Users

**Recommended**: Install `xdg-open` (biasanya sudah ada di most distros)

```bash
# Ubuntu/Debian
sudo apt install xdg-utils

# Arch Linux
sudo pacman -S xdg-utils

# Fedora
sudo dnf install xdg-utils
```

**Alternative**: Install salah satu image viewer:

```bash
# Eye of GNOME (recommended for GNOME)
sudo apt install eog

# feh (lightweight)
sudo apt install feh

# ImageMagick
sudo apt install imagemagick
```

### macOS Users

No installation needed! `open` command is built-in.

### Windows Users

No installation needed! `os.startfile()` is built-in.

## Testing

### Test Case 1: Headless Mode + Auto-Open

```bash
# Set config.yaml
browser:
  headless: true
captcha:
  auto_open_image: true

# Run bot
python run.py

# Expected: Image viewer opens automatically when captcha appears
```

### Test Case 2: Non-Headless Mode + Auto-Open Disabled

```bash
# Set config.yaml
browser:
  headless: false
captcha:
  auto_open_image: false

# Run bot
python run.py

# Expected: See captcha in browser, no image viewer opens
```

### Test Case 3: Check Saved Images

```bash
ls -la screenshots/captcha_manual_*.png

# Should see saved captcha images with timestamps
```

## Troubleshooting

### Issue 1: "No image viewer found" on Linux

**Solution:**

```bash
# Install xdg-utils
sudo apt install xdg-utils

# Or install eog
sudo apt install eog
```

### Issue 2: Image tidak terbuka tapi bot tetap jalan

**This is expected behavior!**

- Auto-open failure tidak akan stop bot
- User masih bisa buka image manual dari `screenshots/` folder
- Check warning log untuk details

### Issue 3: Too many captcha images in screenshots folder

**Solution:**

```bash
# Clean old captcha images
cd screenshots/
rm captcha_manual_*.png

# Or keep only recent ones (Linux/macOS)
find screenshots/ -name "captcha_manual_*.png" -mtime +7 -delete
```

## Summary

**Total Changes**: 3 files

- `betlo/captcha_solver.py` - Added auto-open functionality
- `config.yaml` - Added `auto_open_image` config option
- **NEW**: `AUTO_OPEN_CAPTCHA_FEATURE.md` - This documentation

**Key Features**:

- ✅ Auto-save captcha ke `screenshots/captcha_manual_TIMESTAMP.png`
- ✅ Auto-open dengan default image viewer
- ✅ Support Linux (xdg-open, eog, feh, etc), macOS (open), Windows (startfile)
- ✅ Graceful fallback jika auto-open gagal
- ✅ Configurable via `config.yaml`
- ✅ Perfect untuk headless mode!

**Benefits untuk User**: 🎯 **Headless mode sekarang fully usable untuk manual
captcha!**
